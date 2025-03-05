from sqlalchemy import Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from app.data_apis.bcb import get_divliq_data
from app.data_apis.conect_post.database import Session, engine
import logging
import pandas as pd
from datetime import datetime, timedelta

# Cria modelo para DIVLIQ
Base = declarative_base()

class DivLiqModel(Base):
    __tablename__ = 'divliq'
    
    data = Column(Date, primary_key=True)
    divliq = Column(Float)

# Cria tabela se não existir
Base.metadata.create_all(engine)

# Função para preencher os dados na tabela
def upsert_divliq_data(divliq_data):
    session = Session()
    try:
        # Converter o DataFrame para lista de dicionários
        records = [
            {'data': row['data'], 'divliq': float(row['divliq'])} 
            for _, row in divliq_data.iterrows()
        ]
        
        # Inserir ou atualizar registros
        for record in records:
            existing = session.query(DivLiqModel).filter_by(data=record['data']).first()
            
            if existing:
                # Atualizar registro existente
                existing.divliq = record['divliq']
            else:
                # Criar novo registro
                new_record = DivLiqModel(**record)
                session.add(new_record)
        session.commit()

        logging.info(f"Dados da DIVLIQ inseridos/atualizados: {len(records)} registros")        
    except Exception as e:
        session.rollback()
        logging.error(f"Erro ao inserir dados da DIVLIQ: {e}", exc_info=True)
    finally:
        session.close()


# Função para popular a tabela DIVLIQ se ela estiver vazia                    

def popular_divliq_se_vazia():
    session = Session()
    try:
        # Verificar se a tabela está vazia
        count = session.query(DivLiqModel).count()
        
        logging.info(f"🔍 Verificando tabela DIVLIQ. Total de registros: {count}")
        
        # Sempre buscar e tentar inserir dados, independente de estar vazia
        # Buscar dados da API
        divliq_data = get_divliq_data()
        
        # Imprimir detalhes completos dos dados recebidos
        logging.info(f"📊 Dados DIVLIQ recebidos: {divliq_data}")
        
        if divliq_data is not None:
            # Verificar as chaves do dicionário
            logging.info(f"🔑 Chaves do dicionário: {divliq_data.keys()}")
            
            # Converter para DataFrame
            df = pd.DataFrame({
                'data': pd.to_datetime(divliq_data['dates'], format='%Y%m%d'),
                'divliq': divliq_data['values']
            })
            
            # Imprimir detalhes do DataFrame
            logging.info(f"📝 DataFrame criado:\n{df.head()}")
            logging.info(f"📊 Total de registros no DataFrame: {len(df)}")
            
            # Inserir dados no banco
            upsert_divliq_data(df)
            logging.info("✅ Tabela DIVLIQ atualizada com sucesso")
        else:
            logging.warning("❌ Não foi possível obter dados do DIVLIQ")
    
    except Exception as e:
        logging.error(f"❌ Erro ao popular tabela DIVLIQ: {e}", exc_info=True)
    finally:
        session.close()


# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    popular_divliq_se_vazia()



def get_divliq_data_from_db():
    session = Session()
    try:
        # Buscar todos os registros ordenados por data
        records = session.query(DivLiqModel).order_by(DivLiqModel.data).all()
        
        if not records:
            logging.warning("Nenhum registro de DIVLIQ encontrado")
            return None
        
        dates = [record.data.strftime('%Y-%m-%d') for record in records]
        values = [record.divliq for record in records]
        
        return {
            'dates': dates,
            'values': values,
            'label': 'Dívida Líquida do Governo do Estado da Paraíba',
            'unit': 'Milhões de Reais'
        }
    
    except Exception as e:
        logging.error(f"Erro ao buscar dados do DIVLIQ do banco: {e}")
        return None
    finally:
        session.close()    



def verificar_dados_divliq():
    session = Session()
    try:
        # Buscar o último registro
        ultimo_registro = session.query(DivLiqModel).order_by(DivLiqModel.data.desc()).first()

        # Definir data de início dinamicamente
        if ultimo_registro:
            # Pega a última data e subtrai 10 anos
            data_inicio = ultimo_registro.data - timedelta(days=365 * 10)
        else:
            # Se não há registros, define uma data padrão
            data_inicio = datetime(2011, 10, 1).date()

        # Buscar dados a partir da data de início
        divliq_data = get_divliq_data(period_start=data_inicio.strftime('%Y%m%d'))
        
        if divliq_data is not None:
            # Converter para DataFrame
            df = pd.DataFrame({
                'data': pd.to_datetime(divliq_data['dates'], format='%Y%m%d'),
                'divliq': divliq_data['values']
            })
            
            # Inserir dados
            upsert_divliq_data(df)
            
            logging.info(f"Dados de DIVLIQ atualizados. Novos registros: {len(df)}")
        else:
            logging.warning("Não foi possível obter dados de DIVLIQ")
        
        # Verificar registros após atualização
        count = session.query(DivLiqModel).count()
        logging.info(f"Total de registros na tabela DIVLIQ: {count}")
        
        return count > 0
    except Exception as e:
        logging.error(f"Erro ao verificar dados da DIVLIQ: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False
    finally:
        session.close()

# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    verificar_dados_divliq()          