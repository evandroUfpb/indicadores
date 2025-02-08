import sys
import os

# Adiciona o diretório raiz do projeto ao path do Python
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Configura o logging
import logging
logging.basicConfig(level=logging.INFO)

# Importa a função de população
from app.data_apis.conect_post.conect_post_pib_pb import popular_pib_pb_se_vazia

def main():
    try:
        print("🔍 Iniciando população do banco de dados de PIB da Paraíba...")
        logging.info("Iniciando população do banco de dados de PIB da Paraíba")
        
        popular_pib_pb_se_vazia()
        
        print("✅ População do banco de dados concluída com sucesso!")
        logging.info("População do banco de dados concluída com sucesso")
    
    except Exception as e:
        print(f"❌ Erro durante a população do banco de dados: {e}")
        logging.error(f"Erro durante a população do banco de dados: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
