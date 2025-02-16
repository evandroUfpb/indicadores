from apscheduler.schedulers.blocking import BlockingScheduler
from app.data_apis.conect_post.conect_post_cambio import verificar_dados_cambio
from app.data_apis.conect_post.conect_post_ipca import verificar_dados_ipca
from app.data_apis.conect_post.conect_post_selic import verificar_dados_selic
import logging

def start_etl_scheduler():
    # Criar agendador
    scheduler = BlockingScheduler()
    
    # # Agendar atualização diária do Câmbio
    # scheduler.add_job(
    #     atualizar_cambio_diariamente, 
    #     'cron', 
    #     hour=1,  # Às 1 da manhã
    #     minute=0
    # )

    # Agendar jobs para rodar no primeiro dia de cada mês
    scheduler.add_job(
        verificar_dados_cambio, 
        'cron', 
        day=1,  # Primeiro dia do mês
        hour=3,  # Às 3 da manhã
        minute=0
    )
    
    scheduler.add_job(
        verificar_dados_ipca, 
        'cron', 
        day=1,  # Primeiro dia do mês
        hour=3,  # Às 3 da manhã
        minute=15  # Defasado em 15 minutos para evitar conflitos
    )
    
    scheduler.add_job(
        verificar_dados_selic, 
        'cron', 
        day=1,  # Primeiro dia do mês
        hour=3,  # Às 3 da manhã
        minute=30  # Defasado em 30 minutos para evitar conflitos
    )
    
    try:
        logging.info("Iniciando agendador de ETL para CÂMBIO, IPCA e SELIC")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass