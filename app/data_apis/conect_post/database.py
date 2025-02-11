from sqlalchemy import create_engine, Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool  # Adicionar esta linha

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de conexão
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://usuario:senha@localhost:5432/nome_do_banco')


# Criar engine do SQLAlchemy
engine = create_engine(DATABASE_URL,
    echo=False,
     poolclass=QueuePool,
    pool_size=10,  # Número de conexões mantidas no pool
    max_overflow=20,  # Número máximo de conexões além do pool_size
    pool_timeout=30,  # Tempo de espera para obter uma conexão
    pool_recycle=1800,  # Recicla conexões a cada 30 minutos
    )

# Criar SessionLocal
Session = sessionmaker(bind=engine,
    autocommit=False, 
    autoflush=False,
    expire_on_commit=False  # Melhora performance
    )

def verificar_conexao():
    try:
        with engine.connect() as connection:
            print("Conexão com o banco de dados estabelecida com sucesso!")
            return True
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return False