import logging
logging.basicConfig(level=logging.DEBUG)  # Adicione isso no início do seu script
import requests
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed


#---------------------- Função para pegar o PIB do Brasil ---------------------
def get_pib_data():
    url = pd.read_json("https://apisidra.ibge.gov.br/values/t/5932/n1/all/v/6561/p/all/c11255/90707/d/v6561%201?formato=json")
    
    # Renomear as colunas usando a primeira linha
    url.columns = url.iloc[0]
    
    # Remover a primeira linha (que agora são os nomes das colunas)
    url = url.iloc[1:]
    
    # Tratar os dados
    pib_br = (
        url
        .assign(
            #Converter o código do trimestre para data
            data = lambda x: pd.to_datetime(
                x["Trimestre (Código)"].str[:4] + '-' + 
                (((x["Trimestre (Código)"].str[4:].astype(int) - 1) * 3 + 1).astype(str).str.zfill(2)) + 
                '-01', 
                format='%Y-%m-%d'
            ),

            
            # Converter o valor corretamente
            pib = lambda x: x["Valor"].str.replace(',', '.').astype(float)
        )
        .filter(items=['data', 'pib'])
        .set_index("data")
        .asfreq("QS")
        .query('data > "2011-10-01"')
    )
    return pib_br



#---------------------- Função para pegar o PIB da Paraíba ---------------------


def get_pib_data_pb():
    try:
        # Log de entrada da função
        print("INÍCIO: Função get_pib_data_pb() chamada")
        logging.info("INÍCIO: Função get_pib_data_pb() chamada")

        # URL da API do IBGE para PIB da Paraíba
        url_api = "http://apisidra.ibge.gov.br/values/t/5938/n3/25/v/37/p/all?formato=json"
        
        # Adicionar headers para evitar bloqueios
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Log de início da requisição
        print(f"Iniciando requisição para URL: {url_api}")
        logging.info(f"Iniciando requisição para URL: {url_api}")
        
        # Fazer requisição com requests para maior controle
        response = requests.get(url_api, headers=headers)
        
        # Log do status da resposta
        print(f"Status da resposta: {response.status_code}")
        logging.info(f"Status da resposta: {response.status_code}")
               
        response.raise_for_status()  # Lança exceção para códigos de erro HTTP
        
        # Log do conteúdo bruto da resposta
        raw_json = response.json()
        print(f"Número total de itens no JSON: {len(raw_json)}")
        logging.info(f"Número total de itens no JSON: {len(raw_json)}")
        
        
        # Converter JSON para DataFrame
        url = pd.DataFrame(raw_json)
        
        # Log de depuração
        print(f"Colunas no DataFrame: {url.columns}")
        logging.info(f"Colunas disponíveis: {url.columns}")
        
        
        # Verificar se há dados
        if url.empty:
            print("AVISO: Nenhum dado retornado pela API do PIB da Paraíba")
            logging.warning("Nenhum dado retornado pela API do PIB da Paraíba")
            return None
        
        
        
        # Renomear as colunas usando a primeira linha
        url.columns = url.iloc[0]
        
        # Remover a primeira linha (que agora são os nomes das colunas)
        url = url.iloc[1:]
        
        # Tratar os dados
        pib_pb = (
            url
            .assign(
                # Converter o código do trimestre para data
                data = lambda x: pd.to_datetime(
                    x["Ano"], 
                    format='%Y'
                ),
                # Converter o valor corretamente
                pib = lambda x: x["Valor"].str.replace(',', '.').astype(float)
            )
            .filter(items=['data', 'pib'])
            .set_index("data")
            # .query('data > "2011"')
        )
        # Log adicional para depuração
        logging.info("Todos os dados antes da filtragem:")
        logging.info(pib_pb)
        
        # Filtrar dados após 2011
        pib_pb = pib_pb.query('data > "2011"')

        # Log de depuração
        # Log após filtragem
         # Log após filtragem
        logging.info("Dados do PIB após filtragem:")
        logging.info(pib_pb.to_string())
        logging.info(f"Número de registros após filtragem: {len(pib_pb)}")
        logging.info(f"Primeiro ano após filtragem: {pib_pb.index.min().year}")
        logging.info(f"Último ano após filtragem: {pib_pb.index.max().year}")
        

        return pib_pb
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro de requisição ao buscar dados do PIB da Paraíba: {e}")
        return None
    
    except Exception as e:
        logging.error(f"Erro ao processar dados do PIB da Paraíba: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return None


    # --------------- Função para coletar dados da Desocupação do Brasil ----------

def get_desocupacao_data():
    url = pd.read_json("https://apisidra.ibge.gov.br/values/t/4099/n1/all/v/4099/p/all?formato=json")
    
    # Renomear as colunas usando a primeira linha
    url.columns = url.iloc[0]
    
    # Remover a primeira linha (que agora são os nomes das colunas)
    url = url.iloc[1:]
    
    # Tratar os dados
    des_br = (
        url
        .assign(
            # Converter o código do trimestre para data
            data = lambda x: pd.to_datetime(
                x["Trimestre (Código)"].str[:4] + '-' + 
                (((x["Trimestre (Código)"].str[4:].astype(int) - 1) * 3 + 1).astype(str).str.zfill(2)) + 
                '-01', 
                format='%Y-%m-%d'
            ),
            # Converter o valor corretamente
            des = lambda x: x["Valor"].str.replace(',', '.').astype(float)
        )
        .filter(items=['data', 'des'])
        .set_index("data")
        .asfreq("QS")
        .query('data > "2011-10-01"')
    )
    return des_br



 # --------------- Função para coletar dados da Desocupação da Paraíba ----------

def get_desocupacao_pb_data(start_date = None):
    url = pd.read_json("https://apisidra.ibge.gov.br/values/t/4099/n3/25/v/4099/p/all?formato=json")
    
    # Renomear as colunas usando a primeira linha
    url.columns = url.iloc[0]
    
    # Remover a primeira linha (que agora são os nomes das colunas)
    url = url.iloc[1:]

    # Se nenhuma data de início for fornecida, use a data padrão
    if start_date is None:
        start_date = "2011-10-01"

    # Converter start_date para datetime se for uma string
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)    
    
    # Tratar os dados
    des_pb = (
        url
        .assign(
            # Converter o código do trimestre para data
            data = lambda x: pd.to_datetime(
                x["Trimestre (Código)"].str[:4] + '-' + 
                (((x["Trimestre (Código)"].str[4:].astype(int) - 1) * 3 + 1).astype(str).str.zfill(2)) + 
                '-01', 
                format='%Y-%m-%d'
            ),
            # Converter o valor corretamente
            des = lambda x: x["Valor"].str.replace(',', '.').astype(float)
        )
        .filter(items=['data', 'des'])
        .set_index("data")
        .asfreq("QS")
        .query(f'data > "{start_date}"')
    )
    return des_pb
