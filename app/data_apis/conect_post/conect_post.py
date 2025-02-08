
from sqlalchemy import create_engine, Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de conexão
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://usuario:senha@localhost:5432/nome_do_banco')

# Criar engine de conexão
engine = create_engine(DATABASE_URL)

# Criar sessão
Session = sessionmaker(bind=engine)

# Declarative base para modelos
Base = declarative_base()

# Modelo para a tabela PIB
class PIBModel(Base):
    __tablename__ = 'pib_br'
    
    data = Column(Date, primary_key=True)
    pib = Column(Float)

# Função para criar tabelas
def create_tables():
    Base.metadata.create_all(engine)

# Função para inserir ou atualizar dados
def upsert_pib_data(df):
    session = Session()
    try:
        # Converter o índice (data) de volta para coluna
        df_reset = df.reset_index()
        
        # Inserir ou atualizar cada registro
        for _, row in df_reset.iterrows():
            existing = session.query(PIBModel).filter_by(data=row['data']).first()
            
            if existing:
                # Atualizar se já existir
                existing.pib = row['pib']
            else:
                # Inserir novo registro
                new_record = PIBModel(data=row['data'], pib=row['pib'])
                session.add(new_record)
        
        session.commit()
        print(f"Inseridos/Atualizados {len(df_reset)} registros de PIB")
    except Exception as e:
        session.rollback()
        print(f"Erro ao inserir dados: {e}")
    finally:
        session.close()



# app/data_apis/conect_post/conect_post.py
def get_pib_data_from_db():
    session = Session()
    try:
        # Verificar conexão com o banco
        connection = session.connection()
        print("Conexão com o banco estabelecida com sucesso")
        
        # Buscar todos os registros ordenados por data
        pib_records = session.query(PIBModel).order_by(PIBModel.data).all()
        
        # Log detalhado
        print(f"Número de registros encontrados: {len(pib_records)}")
        
        # Verificar se há registros
        if not pib_records:
            print("Nenhum registro encontrado na tabela PIB")
            return None
        
        # Converter para dicionário
        data = {
            'dates': [record.data.strftime('%Y-%m-%d') for record in pib_records],
            'values': [float(record.pib) for record in pib_records],
            'label': 'PIB do Brasil',
            'unit': '%'
        }
        
        # Log dos dados
        print(f"Datas: {data['dates']}")
        print(f"Valores: {data['values']}")
        
        return data
    except Exception as e:
        print(f"Erro ao buscar dados do PIB: {e}")
        import traceback
        print(traceback.format_exc())
        return None
    finally:
        session.close()


# app/data_apis/conect_post/conect_post.py
def popular_tabela_pib():
    from app.data_apis.sidra import get_pib_data
    
    # Buscar dados do PIB
    pib_data = get_pib_data()
    
    # Inserir dados
    upsert_pib_data(pib_data)
    
    print("Tabela PIB populada com sucesso!")

# Você pode chamar esta função no terminal ou adicionar ao seu script de inicialização
if __name__ == "__main__":
    popular_tabela_pib()               


# No final do arquivo conect_post.py
def verificar_conexao_e_dados():
    session = Session()
    try:
        # Testar conexão
        connection = session.connection()
        print("Conexão com o banco de dados estabelecida com sucesso")
        
        # Contar registros
        count = session.query(PIBModel).count()
        print(f"Número total de registros na tabela PIB: {count}")
        
        # Mostrar alguns registros
        if count > 0:
            registros = session.query(PIBModel).order_by(PIBModel.data).limit(5).all()
            for registro in registros:
                print(f"Data: {registro.data}, PIB: {registro.pib}")
        else:
            print("A tabela PIB está vazia")
    except Exception as e:
        print(f"Erro ao verificar dados: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        session.close()


def popular_tabela_pib_se_vazia():
    session = Session()
    try:
        # Verificar se a tabela está vazia
        count = session.query(PIBModel).count()
        if count == 0:
            from app.data_apis.sidra import get_pib_data
            
            # Buscar dados do PIB
            pib_data = get_pib_data()
            
            # Inserir dados
            upsert_pib_data(pib_data)
            
            print("Tabela PIB populada com sucesso!")
        else:
            print(f"Tabela já contém {count} registros")
    except Exception as e:
        print(f"Erro ao popular tabela: {e}")
    finally:
        session.close()

# Chame esta função no seu script de inicialização
if __name__ == "__main__":
    popular_tabela_pib_se_vazia()


# Adicione esta chamada no final do arquivo ou em seu script de inicialização
if __name__ == "__main__":
    verificar_conexao_e_dados()    