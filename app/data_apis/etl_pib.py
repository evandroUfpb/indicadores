# app/data_apis/etl_pib.py
from apscheduler.schedulers.blocking import BlockingScheduler
from app.data_apis.sidra import get_pib_data
from app.data_apis.conect_post.conect_post import upsert_pib_data, create_tables
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def etl_pib_job():
    try:
        # Criar tabelas se não existirem
        create_tables()
        
        # Buscar dados do PIB
        pib_data = get_pib_data()
        
        # Inserir/Atualizar dados no banco
        upsert_pib_data(pib_data)
        
        logger.info("ETL de PIB concluída com sucesso")
    except Exception as e:
        logger.error(f"Erro na ETL de PIB: {e}")

def start_etl_scheduler():
    # Criar scheduler
    scheduler = BlockingScheduler()
    
    # Agendar job para rodar no primeiro dia de cada mês
    scheduler.add_job(
        etl_pib_job, 
        'cron', 
        day=1,  # Primeiro dia do mês
        hour=3,  # Às 3 da manhã
        minute=0
    )
    
    try:
        logger.info("Iniciando scheduler de ETL para PIB")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

# Para executar manualmente
if __name__ == "__main__":
    etl_pib_job()