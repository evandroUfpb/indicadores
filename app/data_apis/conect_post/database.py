from sqlalchemy import create_engine, Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de conexão
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://usuario:senha@localhost:5432/nome_do_banco')


# Criar engine do SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Criar SessionLocal
Session = sessionmaker(bind=engine)

def verificar_conexao():
    try:
        with engine.connect() as connection:
            print("Conexão com o banco de dados estabelecida com sucesso!")
            return True
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return False