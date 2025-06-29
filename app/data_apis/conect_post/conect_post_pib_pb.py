import logging
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base

from app.data_apis.sidra import get_pib_data_pb
from app.data_apis.conect_post.database import Session as SessionLocal, engine

# Configurar logging para DEBUG
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Criar base para o modelo
Base = declarative_base()

class Pib_pbModel(Base):
    """
    Modelo para armazenar dados do PIB da Paraíba
    """
    __tablename__ = 'pib_pb'
    
    data = Column(Date, primary_key=True)
    pib_pb = Column(Float)

# Criar tabela se não existir
Base.metadata.create_all(engine)

def upsert_pib_pb_data(pib_pb_data):
    """
    Insere ou atualiza dados do PIB da Paraíba no banco de dados.
    
    Args:
        pib_pb_data (pd.DataFrame): DataFrame com dados do PIB
    """
    logger.debug("Iniciando upsert de dados do PIB da Paraíba")
    session = SessionLocal()
    try:
        # Converter o DataFrame para lista de dicionários
        records = [
            {'data': index, 'pib_pb': float(row['pib'])} 
            for index, row in pib_pb_data.iterrows()
        ]
        
        # Contador de registros inseridos/atualizados
        inserted_count = 0
        updated_count = 0
        
        for record in records:
            # Verificar se já existe um registro para esta data
            existing = session.query(Pib_pbModel).filter(
                Pib_pbModel.data == record['data']
            ).first()
            
            if existing:
                # Atualizar registro existente
                existing.pib_pb = record['pib_pb']
                updated_count += 1
            else:
                # Criar novo registro
                new_record = Pib_pbModel(**record)
                session.add(new_record)
                inserted_count += 1
        
        # Commit das alterações
        session.commit()
        
        logger.info(f"Registros de PIB da Paraíba - Inseridos: {inserted_count}, Atualizados: {updated_count}")
    
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao inserir/atualizar dados do PIB da Paraíba: {e}")
        raise
    
    finally:
        session.close()

def get_pib_pb_data_from_db():
    """
    Recupera dados do PIB da Paraíba do banco de dados.
    
    Returns:
        dict: Dicionário com datas, valores e metadados
    """
    logger.debug("Iniciando recuperação de dados do PIB da Paraíba do banco de dados")
    session = SessionLocal()
    try:
        # Buscar todos os registros ordenados por data
        pib_pb_records = (
            session.query(Pib_pbModel)
            .order_by(Pib_pbModel.data)
            .all()
        )
        
        # Verificar se há registros
        if not pib_pb_records:
            logger.warning("Nenhum registro encontrado na tabela do PIB da Paraíba")
            return None
        
        # Converter para dicionário de dados
        data = {
            'dates': [record.data.strftime('%Y-%m-%d') for record in pib_pb_records],
            'values': [float(record.pib_pb) / 1000 for record in pib_pb_records],
            'label': 'PIB da Paraíba',
            'unit': 'Milhões de Reais'
        }
        
        # Log detalhado dos dados
        logger.info(f"Dados do PIB da Paraíba recuperados: {len(data['dates'])} registros")
        logger.debug(f"Primeiras 5 datas: {data['dates'][:5]}")
        logger.debug(f"Primeiros 5 valores: {data['values'][:5]}")
        
        return data
    
    except Exception as e:
        logger.error(f"Erro ao buscar dados do PIB da Paraíba: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None
    
    finally:
        session.close()

def popular_pib_pb_se_vazia():
    """
    Popula a tabela de PIB da Paraíba se estiver vazia.
    """
    logger.debug("Iniciando população da tabela de PIB da Paraíba")
    session = SessionLocal()
    try:
        # Verificar se a tabela está vazia
        count = session.query(func.count(Pib_pbModel.data)).scalar()
        
        logger.info(f"Contagem de registros existentes: {count}")
        
        if count == 0:
            logger.info("Tabela do PIB da Paraíba vazia. Buscando dados...")
            
            # Buscar dados do PIB da Paraíba
            pib_pb_data = get_pib_data_pb()
            
            logger.debug(f"Dados obtidos de get_pib_data_pb(): {pib_pb_data}")
            
            if pib_pb_data is not None and not pib_pb_data.empty:
                # Inserir dados
                upsert_pib_pb_data(pib_pb_data)
                
                logger.info(f"Tabela do PIB da Paraíba populada com sucesso: {len(pib_pb_data)} registros")
            else:
                logger.warning("Não foi possível obter dados do PIB da Paraíba")
        else:
            logger.info(f"Tabela já contém {count} registros")
    
    except Exception as e:
        logger.error(f"Erro ao popular tabela do PIB da Paraíba: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        session.close()

# Para testes manuais
if __name__ == "__main__":
    popular_pib_pb_se_vazia()

        
