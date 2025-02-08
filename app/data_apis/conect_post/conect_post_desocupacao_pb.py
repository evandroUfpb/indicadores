from sqlalchemy import Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from app.data_apis.sidra import get_desocupacao_pb_data
from app.data_apis.conect_post.database import Session, engine
import logging

# Criar modelo para Desocupação
Base = declarative_base()

class DesocupacaoPbModel(Base):
    __tablename__ = 'desocupacao_pb'
    
    data = Column(Date, primary_key=True)
    desocupacao_pb = Column(Float)

# Criar tabela se não existir
Base.metadata.create_all(engine)

def upsert_desocupacao_pb_data(desocupacao_pb_data):
    session = Session()
    try:
        # Converter o DataFrame para lista de dicionários
        records = [
            {'data': index, 'desocupacao_pb': row['des']} 
            for index, row in desocupacao_pb_data.iterrows()
        ]
        
        # Inserir ou atualizar registros
        for record in records:
            existing = session.query(DesocupacaoPbModel).filter_by(data=record['data']).first()
            
            if existing:
                # Atualizar registro existente
                existing.desocupacao_pb = record['desocupacao_pb']
            else:
                # Criar novo registro
                new_record = DesocupacaoPbModel(**record)
                session.add(new_record)
        
        session.commit()
        logging.info(f"Dados de Desocupação da Paraíba inseridos/atualizados: {len(records)} registros")
    except Exception as e:
        session.rollback()
        logging.error(f"Erro ao inserir dados de Desocupação da Paraíba: {e}")
    finally:
        session.close()

def get_desocupacao_pb_data_from_db():
    session = Session()
    try:
        # Verificar conexão com o banco
        connection = session.connection()
        logging.info("Conexão com o banco estabelecida com sucesso")
        
        # Buscar todos os registros ordenados por data
        desocupacao_pb_records = session.query(DesocupacaoPbModel).order_by(DesocupacaoPbModel.data).all()
        
        # Log detalhado
        logging.info(f"Número de registros encontrados: {len(desocupacao_pb_records)}")
        
        # Imprimir detalhes de cada registro
        for record in desocupacao_pb_records[:5]:  # Mostrar os primeiros 5 registros
            logging.info(f"Registro: Data={record.data}, Desocupação={record.desocupacao_pb}")
        
        # Verificar se há registros
        if not desocupacao_pb_records:
            logging.warning("Nenhum registro encontrado na tabela Desocupação PB")
            return None
        
        # Converter para dicionário
        data = {
            'dates': [record.data.strftime('%Y-%m-%d') for record in desocupacao_pb_records],
            'values': [float(record.desocupacao_pb) for record in desocupacao_pb_records],
            'label': 'Taxa de Desocupação da Paraíba',
            'unit': '%'
        }
        
        # Log dos dados
        logging.info(f"Datas: {data['dates']}")
        logging.info(f"Valores: {data['values']}")
        
        return data
    except Exception as e:
        logging.error(f"Erro ao buscar dados da Desocupação da Paraíba: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return None
    finally:
        session.close()

def popular_desocupacao_pb_se_vazia():
    session = Session()
    try:
        # Verificar se a tabela está vazia
        count = session.query(DesocupacaoPbModel).count()
        if count == 0:
            # Buscar dados da Desocupação
            desocupacao_pb_data = get_desocupacao_pb_data()
            
            # Inserir dados
            upsert_desocupacao_pb_data(desocupacao_pb_data)
            
            logging.info("Tabela Desocupação da Paraíba populada com sucesso!")
        else:
            logging.info(f"Tabela já contém {count} registros")
    except Exception as e:
        logging.error(f"Erro ao popular tabela de Desocupação da Paraíba: {e}")
    finally:
        session.close()

# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    popular_desocupacao_pb_se_vazia()

def verificar_dados_desocupacao_pb():
    session = Session()
    try:
        # Contar registros
        count = session.query(DesocupacaoPbModel).count()
        print(f"Número total de registros na tabela Desocupação da Paraíba: {count}")
        
        # Buscar alguns registros
        registros = session.query(DesocupacaoPbModel).order_by(DesocupacaoPbModel.data).limit(5).all()
        
        print("\nPrimeiros registros:")
        for registro in registros:
            print(f"Data: {registro.data}, Desocupação: {registro.desocupacao_pb}")
        
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar dados de Desocupação da Paraíba: {e}")
        return False
    finally:
        session.close()

# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    verificar_dados_desocupacao_pb()    