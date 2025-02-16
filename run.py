from app import app
from app.agendamento_atualizacao import start_etl_scheduler
import threading

# Iniciar o agendador em um thread separado
scheduler_thread = threading.Thread(target=start_etl_scheduler, daemon=True)
scheduler_thread.start()

from app.data_apis.conect_post.conect_post import (
    verificar_conexao_e_dados, 
    popular_tabela_pib_se_vazia
)
from app.data_apis.conect_post.condect_post_desocupacao import (
    popular_desocupacao_se_vazia, 
    get_desocupacao_data_from_db,
    verificar_dados_desocupacao
)

from app.data_apis.conect_post.conect_post_desocupacao_pb import (
    popular_desocupacao_pb_se_vazia, 
    get_desocupacao_pb_data_from_db,
    verificar_dados_desocupacao_pb,
    
)



from  app.data_apis.conect_post.conect_post_ipca import (
    popular_ipca_se_vazia,
    get_ipca_data_from_db,
    verificar_dados_ipca
   )

from app.data_apis.conect_post.conect_post_selic import popular_selic_se_vazia

from app.data_apis.conect_post.conect_post_cambio import popular_cambio_se_vazia

from app.data_apis.conect_post.conect_post_sbcpb import popular_bcpb_se_vazia

from app.data_apis.conect_post.conect_post_divliq_pb import popular_divliq_se_vazia, verificar_dados_divliq 

# Antes de iniciar o aplicativo
verificar_conexao_e_dados()
popular_tabela_pib_se_vazia()
popular_desocupacao_se_vazia()
popular_ipca_se_vazia()
popular_selic_se_vazia()
popular_cambio_se_vazia()
popular_bcpb_se_vazia()
popular_desocupacao_pb_se_vazia()
verificar_dados_desocupacao_pb()
popular_divliq_se_vazia()
verificar_dados_divliq()


# Verificação adicional da Dívida Pública
print("\nVerificando dados da Dívida Pública:")
verificar_dados_divliq()



# Verificação adicional de dados
print("\nVerificando dados de Desocupação:")

print("\nVerificando dados de Desocupação da Paraíba:")
verificar_dados_desocupacao_pb()

desocupacao_data = get_desocupacao_data_from_db()
if desocupacao_data:
    print(f"\nNúmero de registros: {len(desocupacao_data['dates'])}")
    print(f"Primeiras 5 datas: {desocupacao_data['dates'][:5]}")
    print(f"Primeiros 5 valores: {desocupacao_data['values'][:5]}")
else:
    print("Nenhum dado de Desocupação encontrado!")


desocupacao_pb_data = get_desocupacao_pb_data_from_db()
if desocupacao_pb_data:
    print(f"\nNúmero de registros: {len(desocupacao_pb_data['dates'])}")
    print(f"Primeiras 5 datas: {desocupacao_pb_data['dates'][:5]}")
    print(f"Primeiros 5 valores: {desocupacao_pb_data['values'][:5]}")
else:
    print("Nenhum dado de Desocupação da Paraíba encontrado!")


# Verificação adicional de dados
print("\nVerificando dados de Ipca:")
verificar_dados_ipca()

ipca_data = get_ipca_data_from_db()
if ipca_data:
    print(f"\nNúmero de registros: {len(ipca_data['dates'])}")
    print(f"Primeiras 5 datas: {ipca_data['dates'][:5]}")
    print(f"Primeiros 5 valores: {ipca_data['values'][:5]}")
else:
    print("Nenhum dado de Ipca encontrado!")    

if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    app.run(debug=True)