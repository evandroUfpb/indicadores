from apscheduler.schedulers.blocking import BlockingScheduler
from app.data_apis.conect_post.conect_post_cambio import verificar_dados_cambio
from app.data_apis.conect_post.conect_post_ipca import verificar_dados_ipca
from app.data_apis.conect_post.conect_post_selic import verificar_dados_selic
import logging
import sys

def start_etl_scheduler():
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # Criar agendador
    scheduler = BlockingScheduler()
    
    # Adicionar jobs para execução imediata (para teste)
    logger.info("\n" + "="*80)
    logger.info("🔄 INICIANDO EXECUÇÃO IMEDIATA DAS TAREFAS DE ATUALIZAÇÃO")
    logger.info("="*80)
    
    try:
        # Executar verificação de IPCA imediatamente
        logger.info("\n🔍 INICIANDO ATUALIZAÇÃO DO IPCA")
        resultado_ipca = verificar_dados_ipca()
        logger.info(f"✅ RESULTADO DA ATUALIZAÇÃO DO IPCA: {'SUCESSO' if resultado_ipca else 'FALHA'}")
        
        # Executar verificação de Câmbio imediatamente
        logger.info("\n🔍 INICIANDO ATUALIZAÇÃO DO CÂMBIO")
        resultado_cambio = verificar_dados_cambio()
        logger.info(f"✅ RESULTADO DA ATUALIZAÇÃO DO CÂMBIO: {'SUCESSO' if resultado_cambio else 'FALHA'}")
        
        # Executar verificação de Selic imediatamente
        logger.info("\n🔍 INICIANDO ATUALIZAÇÃO DA SELIC")
        resultado_selic = verificar_dados_selic()
        logger.info(f"✅ RESULTADO DA ATUALIZAÇÃO DA SELIC: {'SUCESSO' if resultado_selic else 'FALHA'}")
        
        logger.info("\n✅ TODAS AS ATUALIZAÇÕES FORAM CONCLUÍDAS")
        logger.info("="*80 + "\n")
        
    except Exception as e:
        logger.error(f"❌ ERRO DURANTE A EXECUÇÃO DAS TAREFAS: {str(e)}", exc_info=True)
    
    # Agendar execuções futuras (agendamento normal)
    try:
        logger.info("\n" + "="*80)
        logger.info("⏰ CONFIGURANDO AGENDADOR PARA EXECUÇÕES FUTURAS")
        logger.info("="*80)
        
        # Agendamento diário para Câmbio
        scheduler.add_job(
            verificar_dados_cambio, 
            'cron', 
            hour=1,  # Às 1 da manhã
            minute=0,
            name='Atualização Diária - Câmbio'
        )
        logger.info("✅ Agendada atualização diária do CÂMBIO para 1:00 AM")
        
        # Agendamento mensal para IPCA (dia 1 de cada mês às 3:15 AM)
        scheduler.add_job(
            verificar_dados_ipca, 
            'cron', 
            day=1,
            hour=3,
            minute=15,
            name='Atualização Mensal - IPCA'
        )
        logger.info("✅ Agendada atualização mensal do IPCA para o dia 1 de cada mês às 3:15 AM")
        
        # Agendamento mensal para Selic (dia 1 de cada mês às 3:30 AM)
        scheduler.add_job(
            verificar_dados_selic, 
            'cron', 
            day=1,
            hour=3,
            minute=30,
            name='Atualização Mensal - Selic'
        )
        logger.info("✅ Agendada atualização mensal da SELIC para o dia 1 de cada mês às 3:30 AM")
        
        # Iniciar o agendador
        logger.info("\n🚀 AGENDADOR INICIADO COM SUCESSO!")
        logger.info("Pressione Ctrl+C para encerrar...")
        logger.info("="*80 + "\n")
        
        scheduler.start()
        
    except Exception as e:
        logger.error(f"❌ ERRO AO INICIAR O AGENDADOR: {str(e)}", exc_info=True)
        
    finally:
        logger.info("\n🛑 AGENDADOR ENCERRADO")