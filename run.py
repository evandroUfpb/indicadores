from app import app
from apscheduler.schedulers.background import BackgroundScheduler
from app.agendamento_atualizacao import start_etl_scheduler
import threading
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Importações consolidadas
from app.data_apis.conect_post.conect_post import verificar_conexao_e_dados, popular_tabela_pib_se_vazia
from app.data_apis.conect_post.condect_post_desocupacao import (
    #popular_desocupacao_se_vazia, 
    verificar_dados_desocupacao
)
from app.data_apis.conect_post.conect_post_desocupacao_pb import (
    #popular_desocupacao_pb_se_vazia, 
    verificar_dados_desocupacao_pb
)
from app.data_apis.conect_post.conect_post_divliq_pb import (
    #popular_divliq_se_vazia,
    verificar_dados_divliq
)

from app.data_apis.conect_post.conect_post_sbcpb import (
    verificar_e_atualizar_bcpb
)

from app.data_apis.conect_post.conect_post_selic import verificar_dados_selic

from app.data_apis.conect_post.conect_post_cambio import verificar_dados_cambio

# Iniciar o agendador em um thread separado
scheduler_thread = threading.Thread(target=start_etl_scheduler, daemon=True)
scheduler_thread.start()
logging.info("Scheduler iniciado em thread separada")

# Funções de população e verificação
def popular_e_verificar_dados():
    try:
        # Verifica conexão e popula dados iniciais
        verificar_conexao_e_dados()
        #popular_tabela_pib_se_vazia()

        # População de dados de desocupação
        #popular_desocupacao_se_vazia()
        verificar_dados_desocupacao()

        # População de dados de desocupação PB
        #popular_desocupacao_pb_se_vazia()
        verificar_dados_desocupacao_pb()

        # População de dados de dívida líquida
        #popular_divliq_se_vazia()
        verificar_dados_divliq()

        # Verificação de dados de câmbio
        verificar_dados_cambio()

        # População de dados de Selic
        verificar_dados_selic()

        # População de dados de Selic
        verificar_e_atualizar_bcpb()

        logging.info("Todos os dados foram populados e verificados com sucesso")
    except Exception as e:
        logging.error(f"Erro ao popular e verificar dados: {e}")

# Executa a população e verificação de dados
popular_e_verificar_dados()



if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(start_etl_scheduler, 'interval', hours=24)  # Ajuste o intervalo conforme necessário
    scheduler.start()
    app.run(debug=True)

