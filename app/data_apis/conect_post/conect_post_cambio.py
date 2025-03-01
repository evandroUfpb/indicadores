from datetime import datetime, date, timedelta
import logging
import pandas as pd
from sqlalchemy import Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from app.data_apis.bcb import get_cambio_data
from app.data_apis.conect_post.database import Session, engine



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
        
        # Obter a última data disponível na tabela
        last_record_date = session.query(func.max(CambioModel.data)).scalar()
        
        if last_record_date is None:
            logging.warning("Nenhum registro encontrado na tabela de câmbio.")
            return None

        # Calcular a data inicial como 30 dias antes da última data
        start_date = last_record_date - timedelta(days=30)
        
        # Buscar registros dos últimos 30 dias
        cambio_records = (
            session.query(CambioModel)
            .filter(CambioModel.data >= start_date)
            .order_by(CambioModel.data)
            .all()
        )
        
        logging.info(f"Registros filtrados: {len(cambio_records)}")
        
        # Verificar se há registros
        if not cambio_records:
            logging.warning("Nenhum registro encontrado na tabela CAMBIO após filtragem")
            return None
        
        # Imprimir detalhes dos últimos registros
        for record in cambio_records[-5:]:  # Mostrar os últimos 5 registros
            logging.info(f"Último registro: Data={record.data}, cambio={record.cambio}")
        
        # Converter para dicionário
        data = {
            'dates': [record.data.strftime('%Y-%m-%d') for record in cambio_records],
            'values': [float(record.cambio) for record in cambio_records],
            'label': 'CÂMBIO',
            'unit': 'U$/R$'
        }
        
        logging.info(f"📊 Dados do Câmbio processados:")
        logging.info(f"   Primeiro registro: {data['dates'][0]}, valor: {data['values'][0]}")
        logging.info(f"   Último registro: {data['dates'][-1]}, valor: {data['values'][-1]}")
        
        return data
    except Exception as e:
        logging.error(f"Erro ao buscar dados da CAMBIO: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return None
    finally:
        session.close()



# Verifica e atualiza dados do Cambio
def verificar_dados_cambio():
    try:
        # Conexão com o banco de dados
        session = Session()
        
        logging.info("🔍 Verificando tabela CAMBIO")

        # Buscar o último registro
        ultimo_registro = session.query(CambioModel).order_by(CambioModel.data.desc()).first()

        # Data atual
        data_atual = date.today()
        
        # Se não há registros, ou o último registro é de mais de um dia atrás
        if not ultimo_registro or (data_atual - ultimo_registro.data).days >= 1:
            logging.info("🔄 Iniciando atualização dos dados de Câmbio")
            
            # Buscar novos dados
            dados_cambio = get_cambio_data()
            
            if dados_cambio:
                # Processar e inserir dados
                df_cambio = pd.DataFrame({
                    'data': dados_cambio['dates'],
                    'cambio': dados_cambio['values']
                })
                
                # Converter datas para datetime.date
                df_cambio['data'] = pd.to_datetime(df_cambio['data']).dt.date
                
                # Inserir dados no banco
                for index, row in df_cambio.iterrows():
                    registro_existente = session.query(CambioModel).filter_by(data=row['data']).first()
                    
                    if not registro_existente:
                        novo_registro = CambioModel(data=row['data'], cambio=row['cambio'])
                        session.add(novo_registro)
                
                session.commit()
                logging.info(f"✅ Dados de Câmbio atualizados: {len(df_cambio)} registros")
            else:
                logging.warning("❌ Nenhum dado de Câmbio encontrado para atualização")
        
        else:
            logging.info("✔️ Dados de Câmbio já estão atualizados")
        
        session.close()
    
    except Exception as e:
        logging.error(f"❌ Erro ao verificar dados do Câmbio: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        raise

# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    verificar_dados_cambio()
