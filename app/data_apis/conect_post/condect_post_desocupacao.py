from sqlalchemy import Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from app.data_apis.sidra import get_desocupacao_data
from app.data_apis.conect_post.database import Session, engine
import logging
import pandas as pd

# Criar modelo para Desocupação
Base = declarative_base()

class DesocupacaoModel(Base):
    __tablename__ = 'desocupacao'
    
    data = Column(Date, primary_key=True)
    desocupacao = Column(Float)

# Criar tabela se não existir
Base.metadata.create_all(engine)

def upsert_desocupacao_data(desocupacao_data):
    session = Session()
    try:
        # Converter o DataFrame para lista de dicionários
        records = [
            {'data': index, 'desocupacao': row['des']} 
            for index, row in desocupacao_data.iterrows()
        ]
        
        # Inserir ou atualizar registros
        for record in records:
            existing = session.query(DesocupacaoModel).filter_by(data=record['data']).first()
            
            if existing:
                # Atualizar registro existente
                existing.desocupacao = record['desocupacao']
            else:
                # Criar novo registro
                new_record = DesocupacaoModel(**record)
                session.add(new_record)
        
        session.commit()
        logging.info(f"Dados de Desocupação inseridos/atualizados: {len(records)} registros")
    except Exception as e:
        session.rollback()
        logging.error(f"Erro ao inserir dados de Desocupação: {e}")
    finally:
        session.close()

def get_desocupacao_data_from_db():
    session = Session()
    try:
        # Verificar conexão com o banco
        connection = session.connection()
        logging.info("Conexão com o banco estabelecida com sucesso")
        
        # Buscar todos os registros ordenados por data
        desocupacao_records = session.query(DesocupacaoModel).order_by(DesocupacaoModel.data).all()
        
        # Log detalhado
        logging.info(f"Número de registros encontrados: {len(desocupacao_records)}")
        
        # Verificar se há registros
        if not desocupacao_records:
            logging.warning("Nenhum registro encontrado na tabela Desocupação")
            return None
        
        # Converter para dicionário mantendo o formato original
        formatted_data = {
            'dates': [record.data.strftime('%Y-%m-%d') for record in desocupacao_records],
            'values': [float(record.desocupacao) for record in desocupacao_records],
            'label': 'Taxa de Desocupação',
            'unit': '%',
            'format': 'date'  # Adicionar um campo para indicar o formato
        }
        
        # Log dos dados
        ## logging.info(f"Datas originais: {formatted_data['dates']}")
        ##logging.info(f"Valores: {formatted_data['values']}")
        
        return formatted_data
    except Exception as e:
        logging.error(f"Erro ao buscar dados da Desocupação: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return None
    finally:
        session.close()

def popular_desocupacao_se_vazia():
    session = Session()
    try:
        # Verificar se a tabela está vazia
        count = session.query(DesocupacaoModel).count()
        if count == 0:
            # Buscar dados da Desocupação
            desocupacao_data = get_desocupacao_data()
            
            # Inserir dados
            upsert_desocupacao_data(desocupacao_data)
            
            logging.info("Tabela Desocupação populada com sucesso!")
        else:
            logging.info(f"Tabela já contém {count} registros")
    except Exception as e:
        logging.error(f"Erro ao popular tabela de Desocupação: {e}")
    finally:
        session.close()

# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    popular_desocupacao_se_vazia()

def verificar_dados_desocupacao():
    session = Session()
    try:
        # Buscar dados mais recentes da API
        desocupacao_data = get_desocupacao_data()
        
        if desocupacao_data is None:
            logging.warning("Não foi possível obter dados de desocupação da API")
            return False
        
        # Converter o DataFrame para lista de dicionários
        records = [
            {'data': index, 'desocupacao': row['des']} 
            for index, row in desocupacao_data.iterrows()
        ]
        
        # Encontrar o último registro na base de dados
        ultimo_registro = session.query(DesocupacaoModel).order_by(DesocupacaoModel.data.desc()).first()
        
        # Filtrar apenas registros mais novos que o último registro
        if ultimo_registro:
            records = [
                record for record in records 
                if pd.Timestamp(record['data']).date() > ultimo_registro.data
            ]
        
        # Inserir novos registros
        for record in records:
            new_record = DesocupacaoModel(**record)
            session.add(new_record)
        
        session.commit()
        
        logging.info(f"Novos registros de Desocupação inseridos: {len(records)}")
        
        return len(records) > 0
    except Exception as e:
        session.rollback()
        logging.error(f"Erro ao verificar e atualizar dados de Desocupação: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False
    finally:
        session.close()

# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    verificar_dados_desocupacao()