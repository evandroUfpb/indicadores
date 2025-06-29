from app import app
from apscheduler.schedulers.background import BackgroundScheduler
from app.agendamento_atualizacao import start_etl_scheduler
import threading
import logging
import os

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Importações consolidadas
from app.data_apis.conect_post.conect_post import popular_tabela_pib, verificar_conexao_e_dados
from app.data_apis.conect_post.condect_post_desocupacao import verificar_dados_desocupacao
from app.data_apis.conect_post.conect_post_desocupacao_pb import verificar_dados_desocupacao_pb
from app.data_apis.conect_post.conect_post_divliq_pb import verificar_dados_divliq
from app.data_apis.conect_post.conect_post_sbcpb import verificar_e_atualizar_bcpb
from app.data_apis.conect_post.conect_post_selic import verificar_dados_selic
from app.data_apis.conect_post.conect_post_cambio import verificar_dados_cambio
from app.data_apis.conect_post.conect_post_ipca import verificar_dados_ipca

def popular_e_verificar_dados():
    """Função para popular e verificar dados iniciais"""
    try:
        logging.info("Iniciando verificação e atualização de dados iniciais...")
        
        # Atualiza dados do PIB_BR
        popular_tabela_pib()
        verificar_conexao_e_dados()
        
        # Verificação de dados de desocupação
        verificar_dados_desocupacao()
        
        # Verificação de dados de desocupação PB
        verificar_dados_desocupacao_pb()
        
        # Verificação de dados de dívida líquida
        verificar_dados_divliq()
        
        # Verificação de dados de câmbio
        verificar_dados_cambio()
        
        # Verificação de dados de Selic
        verificar_dados_selic()
        
        # Verificação de dados de BC/PB
        verificar_e_atualizar_bcpb()
        
        # Verificação de dados de IPCA
        verificar_dados_ipca()
        
        logging.info("Verificação e atualização de dados iniciais concluída com sucesso")
    except Exception as e:
        logging.error(f"Erro ao popular e verificar dados iniciais: {e}")

def iniciar_aplicacao():
    """Função para iniciar a aplicação e o agendador"""
    # Executa a verificação inicial de dados
    popular_e_verificar_dados()
    
    # Inicia o servidor Flask
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    # Inicia o agendador em uma thread separada
    scheduler_thread = threading.Thread(target=start_etl_scheduler, daemon=True)
    scheduler_thread.start()
    logging.info("Agendador de atualizações iniciado em thread separada")
    
    # Inicia a aplicação
    iniciar_aplicacao()
