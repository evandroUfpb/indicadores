from sqlalchemy import Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from app.data_apis.bcb import get_cambio_data
from app.data_apis.conect_post.database import Session, engine
import logging
import pandas as pd


# Cria modelo para CAMBIO
Base = declarative_base()

class CambioModel(Base):
    __tablename__ = 'cambio'
    
    data = Column(Date, primary_key=True)
    cambio = Column(Float)

# Cria tabela se não existir
Base.metadata.create_all(engine)


# Inserir os dados no banco
def upsert_cambio_data(cambio_data):
    session = Session()
    try:
        # Converter o DataFrame para lista de dicionários
        records = [
            {'data': index, 'cambio': row['valor']} 
            for index, row in cambio_data.iterrows()
        ]
        
        # Inserir ou atualizar registros
        for record in records:
            existing = session.query(CambioModel).filter_by(data=record['data']).first() or session.query(CambioModel).filter_by(data=record['data']).first()
            
            if existing:
                # Atualizar registro existente
                existing.cambio = record['cambio']
            else:
                # Criar novo registro
                new_record = CambioModel(**record)
                session.add(new_record)
        session.commit()

        logging.info(f"Dados do Cambio inseridos/atualizados: {len(records)} registros")        
    except Exception as e:
        session.rollback()
        logging.error(f"Erro ao inserir dados do Cambio: {e}")
    finally:
        session.close()            

# Baixa os dados do CAMBIO do  post
def get_cambio_data_from_db():
    session = Session()
    try:
        # Verificar conexão com o banco
        connection = session.connection()
        logging.info("Conexão com o banco estabelecida com sucesso")
        
        # Buscar todos os registros ordenados por data
        cambio_records = session.query(CambioModel).order_by(CambioModel.data).all()
        
        # Log detalhado
        logging.info(f"Número de registros encontrados: {len(cambio_records)}")
        
        # Imprimir detalhes de cada registro
        for record in cambio_records[:5]:  # Mostrar os primeiros 5 registros
            logging.info(f"Registro: Data={record.data}, cambio={record.cambio}")
        
        # Verificar se há registros
        if not cambio_records:
            logging.warning("Nenhum registro encontrado na tabela CAMBIO")
            return None
        
        # Converter para dicionário
        data = {
            'dates': [record.data.strftime('%Y-%m-%d') for record in cambio_records],
            'values': [float(record.cambio) for record in cambio_records],
            'label': 'CAMBIO',
            'unit': '%'
        }
        
        # Log dos dados
        logging.info(f"Datas: {data['dates']}")
        logging.info(f"Valores: {data['values']}")
        
        return data
    except Exception as e:
        logging.error(f"Erro ao buscar dados da CAMBIO: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return None
    finally:
        session.close()

def popular_cambio_se_vazia():
    session = Session()
    try:
        # Verificar se a tabela está vazia
        count = session.query(CambioModel).count()
        if count == 0:
            logging.info("Tabela CAMBIO vazia. Buscando dados...")
            
            # Buscar dados da CAMBIO
            cambio_data = get_cambio_data()
            
            if cambio_data is not None:
                logging.info(f"Dados do CAMBIO obtidos: {len(cambio_data['dates'])} registros")
                
                # Converter datas e valores para DataFrame
                df = pd.DataFrame({
                    'data': pd.to_datetime(cambio_data['dates'], format='%Y-%m-%d'),
                    'valor': cambio_data['values']
                })
                
                # Inserir dados no banco usando bulk_save_objects
                try:
                    # Criar lista de objetos CambioModel
                    cambio_records = [
                        CambioModel(data=row['data'], cambio=row['valor']) 
                        for _, row in df.iterrows()
                    ]
                    
                    # Inserção em lote
                    session.bulk_save_objects(cambio_records)
                    session.commit()
                    
                    logging.info(f"Dados do CAMBIO populados com sucesso: {len(cambio_records)} registros")
                
                except Exception as e:
                    session.rollback()
                    logging.error(f"Erro ao inserir dados do CAMBIO: {e}")
            else:
                logging.warning("Não foi possível obter dados da CAMBIO")
        else:
            logging.info(f"Tabela CAMBIO já possui {count} registros")
    
    except Exception as e:
        logging.error(f"Erro ao popular dados da CAMBIO: {e}")
    
    finally:
        session.close()


# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    popular_cambio_se_vazia()

def verificar_dados_cambio():
    session = Session()
    try:
        # Contar registros
        count = session.query(CambioModel).count()
        print(f"Número total de registros na tabela Cambio: {count}")
        
        # Buscar alguns registros
        registros = session.query(CambioModel).order_by(CambioModel.data).limit(5).all()
        
        print("\nPrimeiros registros:")
        for registro in registros:
            print(f"Data: {registro.data}, Cambio: {registro.cambio}")
        
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar dados da Cambio: {e}")
        return False
    finally:
        session.close()

# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    verificar_dados_cambio()                