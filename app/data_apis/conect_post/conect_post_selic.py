from sqlalchemy import Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from app.data_apis.bcb import get_selic_data
from app.data_apis.conect_post.database import Session, engine
import logging
import pandas as pd
from datetime import datetime, timedelta


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
        

        three_years_ago = datetime.now() - timedelta(days=36*30)
        logging.info(f"Filtrando registros a partir de: {three_years_ago}")

        # Buscar todos os registros ordenados por data
        selic_records = (
            session.query(SelicModel)
            .filter(SelicModel.data >= three_years_ago)
            .order_by(SelicModel.data).all()
        )

        logging.info(f"Registros filtrados: {len(selic_records)}")
        
        # Verificar se há registros
        if not selic_records:
            logging.warning("Nenhum registro encontrado na tabela SELIC")
            return None
        
        # Imprimir detalhes de cada registro
        for record in selic_records[-5:]:  # Mostrar os últimos 5 registros
            logging.info(f"Último registro: Data={record.data}, selic={record.selic}")
        
        # Converter para dicionário
        data = {
            'dates': [record.data.strftime('%Y-%m-%d') for record in selic_records],
            'values': [float(record.selic) for record in selic_records],
            'label': 'SELIC',
            'unit': '%'
        }
        
        logging.info(f"📊 Dados da SELIC processados:")
        logging.info(f"   Primeiro registro: {data['dates'][0]}, valor: {data['values'][0]}")
        logging.info(f"   Último registro: {data['dates'][-1]}, valor: {data['values'][-1]}")
        
        return data
    except Exception as e:
        logging.error(f"Erro ao buscar dados da SELIC: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return None
    finally:
        session.close()



def verificar_dados_selic():
    """
    Verifica e atualiza os dados de SELIC.
    
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
        count = session.query(SelicModel).count()
        print(f"Número total de registros na tabela Selic: {count}")
        
        # Buscar alguns registros
        registros = session.query(SelicModel).order_by(SelicModel.data).limit(5).all()
        
        print("\nPrimeiros registros:")
        for registro in registros:
            print(f"Data: {registro.data}, Selic: {registro.selic}")
        
        # Verificar a necessidade de atualização
        ultimo_registro = session.query(SelicModel).order_by(SelicModel.data.desc()).first()
        
        # Data atual
        data_atual = datetime.now().date()
        
        # Se não há registros, ou o último registro é de mais de 30 dias atrás
        if not ultimo_registro or (data_atual - ultimo_registro.data).days >= 30:
            logging.info("🔄 Iniciando atualização dos dados de SELIC")
            
            # Buscar novos dados
            selic_data = get_selic_data()
            
            if selic_data is not None:
                # Converter datas
                df = pd.DataFrame({
                    'data': pd.to_datetime(selic_data['dates'], format='%Y-%m-%d'),
                    'valor': selic_data['values']
                })
                
                # Filtrar registros mais recentes que o último
                if ultimo_registro:
                    #df = df[df['data'] > ultimo_registro.data]
                    # Convert ultimo_registro.data to datetime if it's not already
                    ultimo_data = pd.to_datetime(ultimo_registro.data)
                    df = df[df['data'] > ultimo_data]
                
                # Inserir novos registros
                if not df.empty:
                    try:
                        selic_records = [
                            SelicModel(data=row['data'], selic=row['valor']) 
                            for _, row in df.iterrows()
                        ]
                        
                        session.bulk_save_objects(selic_records)
                        session.commit()
                        
                        logging.info(f"✅ Dados da SELIC atualizados: {len(selic_records)} novos registros")
                        print(f"✅ Dados da SELIC atualizados: {len(selic_records)} novos registros")
                    except Exception as e:
                        session.rollback()
                        logging.error(f"❌ Erro ao inserir dados da SELIC: {e}")
                        print(f"❌ Erro ao inserir dados da SELIC: {e}")
                else:
                    logging.info("ℹ️ Nenhum novo dado de SELIC para inserir")
                    print("ℹ️ Nenhum novo dado de SELIC para inserir")
            else:
                logging.warning("❌ Não foi possível obter dados da SELIC")
                print("❌ Não foi possível obter dados da SELIC")
        
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar dados da Selic: {e}")
        return False
    finally:
        session.close()

# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    verificar_dados_selic()                