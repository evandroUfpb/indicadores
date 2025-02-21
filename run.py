from app import app
from app.agendamento_atualizacao import start_etl_scheduler
import threading
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Importações consolidadas
from app.data_apis.conect_post.conect_post import verificar_conexao_e_dados, popular_tabela_pib_se_vazia
from app.data_apis.conect_post.condect_post_desocupacao import (
    popular_desocupacao_se_vazia, 
    verificar_dados_desocupacao
)
from app.data_apis.conect_post.conect_post_desocupacao_pb import (
    popular_desocupacao_pb_se_vazia, 
    verificar_dados_desocupacao_pb
)
from app.data_apis.conect_post.conect_post_divliq_pb import (
    popular_divliq_se_vazia,
    verificar_dados_divliq
)


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
        popular_tabela_pib_se_vazia()

        # População de dados de desocupação
        popular_desocupacao_se_vazia()
        verificar_dados_desocupacao()

        # População de dados de desocupação PB
        popular_desocupacao_pb_se_vazia()
        verificar_dados_desocupacao_pb()

        # População de dados de dívida líquida
        popular_divliq_se_vazia()
        verificar_dados_divliq()

        # Verificação de dados de câmbio
        verificar_dados_cambio()

        logging.info("Todos os dados foram populados e verificados com sucesso")
    except Exception as e:
        logging.error(f"Erro ao popular e verificar dados: {e}")

# Executa a população e verificação de dados
popular_e_verificar_dados()



if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    app.run(debug=True)


# from app import app
# from app.agendamento_atualizacao import start_etl_scheduler
# import threading
# import logging


# # Configuração de logging
# logging.basicConfig(level=logging.INFO)

# # Iniciar o agendador em um thread separado
# scheduler_thread = threading.Thread(target=start_etl_scheduler, daemon=True)
# scheduler_thread.start()
# logging.info("Scheduler iniciado em thread separada")

# from app.data_apis.conect_post.conect_post import (
#     verificar_conexao_e_dados, 
#     popular_tabela_pib_se_vazia
# )

# from app.data_apis.conect_post.condect_post_desocupacao import (
#     popular_desocupacao_se_vazia, 
#     get_desocupacao_data_from_db,
#     verificar_dados_desocupacao)

# from app.data_apis.conect_post.conect_post_desocupacao_pb import (
#     popular_desocupacao_pb_se_vazia, 
#     get_desocupacao_pb_data_from_db,
#     verificar_dados_desocupacao_pb,
    
# )



# from  app.data_apis.conect_post.conect_post_ipca import (
#     #popular_ipca_se_vazia,
#     get_ipca_data_from_db,
#     verificar_dados_ipca
#    )

# #from app.data_apis.conect_post.conect_post_selic import #popular_selic_se_vazia

# from app.data_apis.conect_post.conect_post_cambio import verificar_dados_cambio

# from app.data_apis.conect_post.conect_post_sbcpb import popular_bcpb_se_vazia

# from app.data_apis.conect_post.conect_post_divliq_pb import verificar_dados_divliq, popular_divliq_se_vazia 

# # Antes de iniciar o aplicativo
# verificar_conexao_e_dados()
# popular_tabela_pib_se_vazia()
# popular_desocupacao_se_vazia()
# #popular_ipca_se_vazia()
# #popular_selic_se_vazia()
# #popular_cambio_se_vazia()
# popular_bcpb_se_vazia()
# popular_desocupacao_pb_se_vazia()
# verificar_dados_desocupacao_pb()
# verificar_dados_desocupacao()
# popular_divliq_se_vazia()
# verificar_dados_divliq()
# verificar_dados_cambio()

# # Verificação adicional da Dívida Pública
# print("\nVerificando dados da Dívida Pública:")
# verificar_dados_divliq()



# # Verificação adicional de dados
# print("\nVerificando dados de Desocupação:")

# print("\nVerificando dados de Desocupação da Paraíba:")
# verificar_dados_desocupacao_pb()

# desocupacao_data = get_desocupacao_data_from_db()
# if desocupacao_data:
#     print(f"\nNúmero de registros: {len(desocupacao_data['dates'])}")
#     print(f"Primeiras 5 datas: {desocupacao_data['dates'][:5]}")
#     print(f"Primeiros 5 valores: {desocupacao_data['values'][:5]}")
# else:
#     print("Nenhum dado de Desocupação encontrado!")


# desocupacao_pb_data = get_desocupacao_pb_data_from_db()
# if desocupacao_pb_data:
#     print(f"\nNúmero de registros: {len(desocupacao_pb_data['dates'])}")
#     print(f"Primeiras 5 datas: {desocupacao_pb_data['dates'][:5]}")
#     print(f"Primeiros 5 valores: {desocupacao_pb_data['values'][:5]}")
# else:
#     print("Nenhum dado de Desocupação da Paraíba encontrado!")


# # Verificação adicional de dados
# print("\nVerificando dados de Ipca:")
# verificar_dados_ipca()

# ipca_data = get_ipca_data_from_db()
# if ipca_data:
#     print(f"\nNúmero de registros: {len(ipca_data['dates'])}")
#     print(f"Primeiras 5 datas: {ipca_data['dates'][:5]}")
#     print(f"Primeiros 5 valores: {ipca_data['values'][:5]}")
# else:
#     print("Nenhum dado de Ipca encontrado!")    

# if __name__ == '__main__':
#     print("Iniciando servidor Flask...")
#     app.run(debug=True)