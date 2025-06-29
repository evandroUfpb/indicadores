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


def comparar_datas(data1, data2):
    """
    Compara duas datas, convertendo-as para o mesmo tipo, se necessário.
    
    Args:
        data1: Primeira data (pode ser datetime.date, datetime.datetime ou string)
        data2: Segunda data (pode ser datetime.date, datetime.datetime ou string)
        
    Returns:
        bool: True se data1 > data2, False caso contrário
    """
    from datetime import datetime, date
    
    # Converter data1 para datetime.date se necessário
    if isinstance(data1, str):
        data1 = datetime.strptime(data1.split(' ')[0], '%Y-%m-%d').date()
    elif hasattr(data1, 'date'):
        data1 = data1.date()
    
    # Converter data2 para datetime.date se necessário
    if isinstance(data2, str):
        data2 = datetime.strptime(data2.split(' ')[0], '%Y-%m-%d').date()
    elif hasattr(data2, 'date'):
        data2 = data2.date()
    
    return data1 > data2

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
    logging.info("\n" + "="*80)
    logging.info(" INICIANDO VERIFICAÇÃO DE DADOS DO IPCA")
    logging.info("="*80)
    
    session = Session()
    try:
        # 1. Verificar registros atuais
        count = session.query(IpcaModel).count()
        logging.info(f" NÚMERO TOTAL DE REGISTROS NA TABELA IPCA: {count}")
        
        # Buscar últimos 5 registros
        registros = session.query(IpcaModel).order_by(IpcaModel.data.desc()).limit(5).all()
        
        logging.info("\n ÚLTIMOS 5 REGISTROS NO BANCO DE DADOS:")
        for i, registro in enumerate(registros, 1):
            logging.info(f"   {i}. Data: {registro.data} (tipo: {type(registro.data)}), Ipca: {registro.ipca} (tipo: {type(registro.ipca)})")
        
        # 2. Verificar necessidade de atualização
        ultimo_registro = session.query(IpcaModel).order_by(IpcaModel.data.desc()).first()
        data_atual = datetime.now().date()
        
        logging.info(f"\n DATA ATUAL: {data_atual} (tipo: {type(data_atual)})")
        
        if ultimo_registro:
            dias_desde_ultima_atualizacao = (data_atual - ultimo_registro.data).days
            logging.info(f"  ÚLTIMA ATUALIZAÇÃO: {ultimo_registro.data} (há {dias_desde_ultima_atualizacao} dias)")
            precisa_atualizar = dias_desde_ultima_atualizacao >= 30
        else:
            logging.info("  NENHUM REGISTRO ENCONTRADO NO BANCO DE DADOS.")
            precisa_atualizar = True
        
        if not precisa_atualizar:
            logging.info("\n  OS DADOS DO IPCA JÁ ESTÃO ATUALIZADOS.")
            return True
            
        # 3. Buscar novos dados
        logging.info("\n BUSCANDO NOVOS DADOS DO IPCA...")
        dados_ipca = get_ipca_data(period_start='2000-01-01')
        
        if not dados_ipca:
            logging.error(" FALHA AO OBTER DADOS DO IPCA: Resposta vazia ou inválida")
            return False
            
        if 'dates' not in dados_ipca or 'values' not in dados_ipca:
            logging.error(f" FORMATO DE DADOS INVÁLIDO: {dados_ipca.keys()}")
            return False
            
        total_registros = len(dados_ipca['dates'])
        logging.info(f" DADOS OBTIDOS: {total_registros} registros")
        
        # 4. Processar dados
        df = pd.DataFrame({
            'data': pd.to_datetime(dados_ipca['dates']).date,
            'valor': pd.to_numeric(dados_ipca['values'], errors='coerce')
        })
        
        # Remover valores nulos
        df = df.dropna()
        
        # Ordenar por data
        df = df.sort_values('data')
        
        # Filtrar apenas registros mais recentes que o último no banco
        if ultimo_registro:
            df = df[df['data'] > ultimo_registro.data]
            
        if df.empty:
            logging.info(" NENHUM NOVO REGISTRO PARA INSERIR.")
            return True
            
        # 5. Inserir novos registros
        logging.info(f"\n PREPARANDO PARA INSERIR {len(df)} NOVOS REGISTROS...")
        
        # Log dos primeiros e últimos registros
        logging.info(" PRIMEIROS 3 REGISTROS:")
        for i, (_, row) in enumerate(df.head(3).iterrows(), 1):
            logging.info(f"   {i}. Data: {row['data']}, Valor: {row['valor']}")
            
        logging.info(" ÚLTIMOS 3 REGISTROS:")
        for i, (_, row) in enumerate(df.tail(3).iterrows(), 1):
            logging.info(f"   {i}. Data: {row['data']}, Valor: {row['valor']}")
        
        try:
            # Inserir em lotes
            batch_size = 100
            total_inseridos = 0
            
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i + batch_size]
                registros = [
                    IpcaModel(data=row['data'], ipca=float(row['valor']))
                    for _, row in batch.iterrows()
                ]
                
                session.bulk_save_objects(registros)
                session.commit()
                
                total_inseridos += len(registros)
                logging.info(f" LOTE {i//batch_size + 1} INSERIDO: {len(registros)} registros")
            
            # Verificar inserção
            novo_total = session.query(IpcaModel).count()
            ultimo = session.query(IpcaModel).order_by(IpcaModel.data.desc()).first()
            
            logging.info("\n ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
            logging.info(f" TOTAL DE REGISTROS: {novo_total} (antes: {count})")
            logging.info(f" REGISTROS INSERIDOS: {total_inseridos}")
            
            if ultimo:
                logging.info(f" ÚLTIMO REGISTRO: {ultimo.data} = {ultimo.ipca}%")
            
            return True
            
        except Exception as e:
            session.rollback()
            logging.error(f" ERRO AO INSERIR DADOS: {str(e)}", exc_info=True)
            return False
            
    except Exception as e:
        logging.error(f" ERRO NA VERIFICAÇÃO DO IPCA: {str(e)}", exc_info=True)
        return False
        
    finally:
        session.close()
        logging.info("="*80 + "\n")