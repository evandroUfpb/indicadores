from sqlalchemy import Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from app.data_apis.bcb import get_bcpb_data
from app.data_apis.conect_post.database import Session, engine
import logging
import pandas as pd
from datetime import date

# Cria modelo para BCPB
Base = declarative_base()

class BcPbModel(Base):
    __tablename__ = 'bcpb'
    
    data = Column(Date, primary_key=True)
    bcpb = Column(Float)

# Cria tabela se não existir
Base.metadata.create_all(engine)

# Função para preencher os dados 
def upsert_bcpb_data(bcpb_data):
    session = Session()
    try:
        # Converter o DataFrame para lista de dicionários
        records = [
            {'data': row['data'], 'bcpb': float(row['bcpb'])} 
            for _, row in bcpb_data.iterrows()
        ]
        
        # Inserir ou atualizar registros
        for record in records:
            existing = session.query(BcPbModel).filter_by(data=record['data']).first()
            
            if existing:
                # Atualizar registro existente
                existing.bcpb = record['bcpb']
            else:
                # Criar novo registro
                new_record = BcPbModel(**record)
                session.add(new_record)
        session.commit()

        logging.info(f"Dados da BCPB inseridos/atualizados: {len(records)} registros")        
    except Exception as e:
        session.rollback()
        logging.error(f"Erro ao inserir dados da BCPB: {e}", exc_info=True)
    finally:
        session.close()


# Função para popular a tabela BCPB se ela estiver vazia                    
def popular_bcpb_se_vazia():
    session = Session()
    try:
        # Verificar se a tabela está vazia
        count = session.query(BcPbModel).count()
        
        if count == 0:
            logging.info("Tabela BCPB vazia. Iniciando população...")
            
            # Buscar dados da API
            bcpb_data = get_bcpb_data()
            
            # Imprimir detalhes completos dos dados recebidos
            logging.info(f"Dados recebidos: {bcpb_data}")
            
            if bcpb_data is not None:
                # Verificar as chaves do dicionário
                logging.info(f"Chaves do dicionário: {bcpb_data.keys()}")
                
                # Converter para DataFrame
                df = pd.DataFrame({
                    'data': pd.to_datetime(bcpb_data['dates'], format='%Y%m%d'),
                    'bcpb': bcpb_data['values']  # corrigido para 'values'
                })
                
                # Imprimir detalhes do DataFrame
                logging.info(f"DataFrame criado:\n{df.head()}")
                
                # Inserir dados no banco
                upsert_bcpb_data(df)
                logging.info("Tabela BCPB populada com sucesso")
            else:
                logging.warning("Não foi possível obter dados do BCPB")
        else:
            logging.info(f"Tabela BCPB já contém {count} registros")
    
    except Exception as e:
        logging.error(f"Erro ao popular tabela BCPB: {e}", exc_info=True)
    finally:
        session.close()



# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    popular_bcpb_se_vazia()



def get_bcpb_data_from_db():
    session = Session()
    try:
        # Buscar todos os registros ordenados por data
        records = session.query(BcPbModel).order_by(BcPbModel.data).all()
        
        if not records:
            logging.warning("Nenhum registro de BCPB encontrado")
            return None
        
        dates = [record.data.strftime('%Y-%m-%d') for record in records]
        values = [record.bcpb for record in records]
        
        return {
            'dates': dates,
            'values': values,
            'label': 'Saldo da Balança Comercial da Paraíba',
            'unit': 'Milhões de Reais'
        }
    
    except Exception as e:
        logging.error(f"Erro ao buscar dados do BCPB do banco: {e}")
        return None
    finally:
        session.close()    




def verificar_e_atualizar_bcpb():
    """
    Verifica a necessidade de atualização dos dados do BCPB no banco de dados.
    
    Etapas:
    1. Busca os dados existentes no banco de dados
    2. Obtém os dados mais recentes da API
    3. Compara as datas e atualiza se necessário
    4. Registra logs de todas as ações realizadas
    """
    session = Session()
    try:
        # Buscar a data mais recente no banco de dados
        ultima_data_db = session.query(BcPbModel.data).order_by(BcPbModel.data.desc()).first()
        
        if ultima_data_db:
            ultima_data_db = ultima_data_db[0]
            logging.info(f"Última data no banco de dados: {ultima_data_db}")
        else:
            logging.info("Banco de dados de BCPB está vazio")
            # Se o banco estiver vazio, chama a função de população
            session.close()
            popular_bcpb_se_vazia()
            return
        
        # Buscar dados da API
        bcpb_data = get_bcpb_data()
        
        if bcpb_data is None:
            logging.warning("Não foi possível obter novos dados do BCPB")
            return
        
        # Converter para DataFrame
        dates = [pd.to_datetime(d, format='%Y%m%d').date() for d in bcpb_data['dates']]
        df = pd.DataFrame({
            'data': dates,
            'bcpb': bcpb_data['values']
        })
        
        # Converter ultima_data_db para date se ainda não for
        if not isinstance(ultima_data_db, date):
            ultima_data_db = ultima_data_db.date()
        
        # Filtrar apenas dados mais recentes que a última data no banco
        df_novos = df[df['data'].apply(lambda x: x > ultima_data_db)]
        
        if not df_novos.empty:
            logging.info(f"Encontrados {len(df_novos)} novos registros de BCPB")
            
            # Converter de volta para DataFrame com datetime
            df_novos['data'] = pd.to_datetime(df_novos['data'])
            
            upsert_bcpb_data(df_novos)
            logging.info("Dados de BCPB atualizados com sucesso")
        else:
            logging.info("Não há novos dados para atualizar")
    
    except Exception as e:
        logging.error(f"Erro ao verificar e atualizar dados do BCPB: {e}", exc_info=True)
    finally:
        session.close()

# Adicionar chamada no bloco de inicialização
if __name__ == "__main__":
    verificar_e_atualizar_bcpb()