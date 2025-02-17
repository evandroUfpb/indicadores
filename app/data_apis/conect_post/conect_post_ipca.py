from sqlalchemy import Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from app.data_apis.bcb import get_ipca_data
from app.data_apis.conect_post.database import Session, engine
import logging
from datetime import datetime, date
import pandas as pd


# Cria modelo para ipca
Base = declarative_base()

class IpcaModel(Base):
    __tablename__ = 'ipca'
    
    data = Column(Date, primary_key=True)
    ipca = Column(Float)

# Cria tabela se não existir
Base.metadata.create_all(engine)


# Inserir os dados no banco
def upsert_ipca_data(ipca_data):
    session = Session()
    try:
        # Converter o DataFrame para lista de dicionários
        records = [
            {'data': index, 'ipca': row['valor']} 
            for index, row in ipca_data.iterrows()
        ]
        
        # Inserir ou atualizar registros
        for record in records:
            existing = session.query(IpcaModel).filter_by(data=record['data']).first() or session.query(IpcaModel).filter_by(data=record['data']).first()
            
            if existing:
                # Atualizar registro existente
                existing.ipca = record['ipca']
            else:
                # Criar novo registro
                new_record = IpcaModel(**record)
                session.add(new_record)
        session.commit()

        logging.info(f"Dados de Ipca inseridos/atualizados: {len(records)} registros")        
    except Exception as e:
        session.rollback()
        logging.error(f"Erro ao inserir dados do Ipca: {e}")
    finally:
        session.close()            

# Baixa os dados do IPCA do  post
def get_ipca_data_from_db():
    session = Session()
    try:
        # Verificar conexão com o banco
        connection = session.connection()
        logging.info("Conexão com o banco estabelecida com sucesso")
        
        # Buscar todos os registros ordenados por data
        ipca_records = session.query(IpcaModel).order_by(IpcaModel.data).all()
        
        # Log detalhado
        logging.info(f"Número de registros encontrados: {len(ipca_records)}")
        
        # Imprimir detalhes de cada registro
        for record in ipca_records[:5]:  # Mostrar os primeiros 5 registros
            logging.info(f"Registro: Data={record.data}, ipca={record.ipca}")
        
        # Verificar se há registros
        if not ipca_records:
            logging.warning("Nenhum registro encontrado na tabela IPCA")
            return None
        
        # Converter para dicionário
        data = {
            'dates': [record.data.strftime('%Y-%m-%d') for record in ipca_records],
            'values': [float(record.ipca) for record in ipca_records],
            'label': 'IPCA',
            'unit': '%'
        }
        
        # Log dos dados
        logging.info(f"Datas: {data['dates']}")
        logging.info(f"Valores: {data['values']}")
        
        return data
    except Exception as e:
        logging.error(f"Erro ao buscar dados do IPCA: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return None
    finally:
        session.close()

# def popular_ipca_se_vazia():
#     session = Session()
#     try:
#         # Verificar se a tabela está vazia
#         count = session.query(IpcaModel).count()
#         if count == 0:
#             logging.info("Tabela IPCA vazia. Buscando dados...")
            
#             # Buscar dados do IPCA
#             ipca_data = get_ipca_data()
            
#             if ipca_data is not None:
#                 # Inserir dados no banco
#                 upsert_ipca_data(ipca_data)
#                 logging.info("Dados do IPCA populados com sucesso")
#             else:
#                 logging.error("Não foi possível buscar dados do IPCA")
#         else:
#             logging.info(f"Tabela IPCA já contém {count} registros")
#     except Exception as e:
#         logging.error(f"Erro ao popular dados do IPCA: {e}")
#     finally:
#         session.close()


# # Chame esta função no seu script de inicialização
# if __name__ == "__main__":
#     popular_ipca_se_vazia()


# Verifica dados do IPCA e atualiza se necessário    

def verificar_dados_ipca():
    """
    Verifica e atualiza os dados de IPCA.
    
    Realiza as seguintes ações:
    1. Conta o número total de registros
    2. Imprime os primeiros registros
    3. Busca e insere novos dados se necessário
    
    Returns:
        bool: True se há registros, False caso contrário
    """
    session = Session()
    try:
        # Contar registros
        count = session.query(IpcaModel).count()
        print(f"Número total de registros na tabela Ipca: {count}")
        
        # Buscar alguns registros
        registros = session.query(IpcaModel).order_by(IpcaModel.data).limit(5).all()
        
        print("\nPrimeiros registros:")
        for registro in registros:
            print(f"Data: {registro.data}, Ipca: {registro.ipca}")
        
        # Verificar a necessidade de atualização
        ultimo_registro = session.query(IpcaModel).order_by(IpcaModel.data.desc()).first()
        
        # Data atual
        data_atual = datetime.now().date()
        
        # Se não há registros, ou o último registro é de mais de 30 dias atrás
        if not ultimo_registro or (data_atual - ultimo_registro.data).days >= 30:
            logging.info("🔄 Iniciando atualização dos dados de IPCA")
            
            # Buscar novos dados
            ipca_data = get_ipca_data()
            
            if ipca_data is not None:
                # Converter datas
                df = pd.DataFrame({
                    #'data': pd.to_datetime(ipca_data['dates'], format='%Y-%m-%d'),
                    'data': pd.to_datetime(ipca_data['dates']).date,
                    'valor': ipca_data['values']
                })

                # Log de diagnóstico
                logging.info(f"Dados recebidos do IPCA: {len(df)} registros")
                logging.info(f"Primeiro registro: {df.iloc[0]['data']}, Último registro: {df.iloc[-1]['data']}")

                
                # Filtrar registros mais recentes que o último
                if ultimo_registro:
                    df = df[df['data'] > ultimo_registro.data]
                
                # Inserir novos registros
                if not df.empty:
                    try:
                        ipca_records = [
                            IpcaModel(data=row['data'], ipca=row['valor']) 
                            for _, row in df.iterrows()
                        ]
                        
                        session.bulk_save_objects(ipca_records)
                        session.commit()
                        
                        logging.info(f"✅ Dados do IPCA atualizados: {len(ipca_records)} novos registros")
                        print(f"✅ Dados do IPCA atualizados: {len(ipca_records)} novos registros")
                    except Exception as e:
                        session.rollback()
                        logging.error(f"❌ Erro ao inserir dados do IPCA: {e}")
                        print(f"❌ Erro ao inserir dados do IPCA: {e}")
                else:
                    logging.info("ℹ️ Nenhum novo dado de IPCA para inserir")
                    print("ℹ️ Nenhum novo dado de IPCA para inserir")
            else:
                logging.warning("❌ Não foi possível obter dados do IPCA")
                print("❌ Não foi possível obter dados do IPCA")
        
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar dados do Ipca: {e}")
        return False
    finally:
        session.close()              