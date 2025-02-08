from sqlalchemy import Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from app.data_apis.bcb import get_selic_data
from app.data_apis.conect_post.database import Session, engine
import logging
import pandas as pd


# Cria modelo para SELCI
Base = declarative_base()

class SelicModel(Base):
    __tablename__ = 'selic'
    
    data = Column(Date, primary_key=True)
    selic = Column(Float)

# Cria tabela se não existir
Base.metadata.create_all(engine)


# Inserir os dados no banco
def upsert_selic_data(selic_data):
    session = Session()
    try:
        # Converter o DataFrame para lista de dicionários
        records = [
            {'data': index, 'selic': row['valor']} 
            for index, row in selic_data.iterrows()
        ]
        
        # Inserir ou atualizar registros
        for record in records:
            existing = session.query(SelicModel).filter_by(data=record['data']).first() or session.query(SelicModel).filter_by(data=record['data']).first()
            
            if existing:
                # Atualizar registro existente
                existing.selic = record['selic']
            else:
                # Criar novo registro
                new_record = SelicModel(**record)
                session.add(new_record)
        session.commit()

        logging.info(f"Dados da Selic inseridos/atualizados: {len(records)} registros")        
    except Exception as e:
        session.rollback()
        logging.error(f"Erro ao inserir dados da Selic: {e}")
    finally:
        session.close()            

# Baixa os dados do SELIC do  post
def get_selic_data_from_db():
    session = Session()
    try:
        # Verificar conexão com o banco
        connection = session.connection()
        logging.info("Conexão com o banco estabelecida com sucesso")
        
        # Buscar todos os registros ordenados por data
        selic_records = session.query(SelicModel).order_by(SelicModel.data).all()
        
        # Log detalhado
        logging.info(f"Número de registros encontrados: {len(selic_records)}")
        
        # Imprimir detalhes de cada registro
        for record in selic_records[:5]:  # Mostrar os primeiros 5 registros
            logging.info(f"Registro: Data={record.data}, selic={record.selic}")
        
        # Verificar se há registros
        if not selic_records:
            logging.warning("Nenhum registro encontrado na tabela SELIC")
            return None
        
        # Converter para dicionário
        data = {
            'dates': [record.data.strftime('%Y-%m-%d') for record in selic_records],
            'values': [float(record.selic) for record in selic_records],
            'label': 'SELIC',
            'unit': '%'
        }
        
        # Log dos dados
        logging.info(f"Datas: {data['dates']}")
        logging.info(f"Valores: {data['values']}")
        
        return data
    except Exception as e:
        logging.error(f"Erro ao buscar dados da SELIC: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return None
    finally:
        session.close()

def popular_selic_se_vazia():
    session = Session()
    try:
        # Verificar se a tabela está vazia
        count = session.query(SelicModel).count()
        if count == 0:
            logging.info("Tabela SELIC vazia. Buscando dados...")
            
            # Buscar dados da SELIC
            selic_data = get_selic_data()
            
            if selic_data is not None:
                logging.info(f"Dados da SELIC obtidos: {len(selic_data['dates'])} registros")
                
                # Converter datas e valores para DataFrame
                df = pd.DataFrame({
                    'data': pd.to_datetime(selic_data['dates'], format='%Y-%m'),
                    'valor': selic_data['values']
                })
                
                # Inserir dados no banco
                try:
                    for index, row in df.iterrows():
                        selic_record = SelicModel(data=row['data'], selic=row['valor'])
                        session.merge(selic_record)
                    
                    session.commit()
                    logging.info("Dados da SELIC populados com sucesso")
                
                except Exception as e:
                    session.rollback()
                    logging.error(f"Erro ao inserir dados da SELIC: {e}")
            else:
                logging.warning("Não foi possível obter dados da SELIC")
        else:
            logging.info(f"Tabela SELIC já possui {count} registros")
    
    except Exception as e:
        logging.error(f"Erro ao popular dados da SELIC: {e}")
    
    finally:
        session.close()


# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    popular_selic_se_vazia()

def verificar_dados_selic():
    session = Session()
    try:
        # Contar registros
        count = session.query(SelicModel).count()
        print(f"Número total de registros na tabela Selic: {count}")
        
        # Buscar alguns registros
        registros = session.query(SelicModel).order_by(SelicModel.data).limit(5).all()
        
        print("\nPrimeiros registros:")
        for registro in registros:
            print(f"Data: {registro.data}, Selic: {registro.selic}")
        
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar dados da Selic: {e}")
        return False
    finally:
        session.close()

# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    verificar_dados_selic()                