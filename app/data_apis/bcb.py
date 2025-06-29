import logging
import pandas as pd
import requests
import itertools
from datetime import date, timedelta
from tenacity import retry, stop_after_attempt, wait_fixed
import json



# ----------------- IPCA ---------------- ------------------------------------------

def get_ipca_data(period_start=None, period_end=None):
    """
    Obtém dados do IPCA do Banco Central do Brasil
    """
    try:
        # Se não foi especificada uma data final, usa a data atual
        if period_end is None:
            period_end = date.today()
        else:
            period_end = pd.to_datetime(period_end).date()
            
        # Converte as datas para o formato da API
        if period_start is None:
            # Buscar dados dos últimos 180 dias
            period_start = period_end - timedelta(days=180)
        else:
            period_start = pd.to_datetime(period_start).date()

        # Log das datas para diagnóstico
        logging.info(f"🕒 Intervalo de datas para busca de IPCA: {period_start} a {period_end}")

        start = period_start.strftime("%d/%m/%Y")
        end = period_end.strftime("%d/%m/%Y")
            
        # URL da API do BCB
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial={start}&dataFinal={end}"
        
        logging.info(f"🌐 URL de requisição IPCA: {url}")
        
        # Configurações para melhorar resiliência
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Aumentar timeout e adicionar retry
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry

        retry_strategy = Retry(
            total=3,  # Número total de tentativas
            status_forcelist=[429, 500, 502, 503, 504],  # Códigos de status para retry
            allowed_methods=["GET"],
            backoff_factor=1  # Tempo entre as tentativas aumenta exponencialmente
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)

        # Faz a requisição com timeout maior
        response = session.get(url, headers=headers, timeout=30)
        
        # Log do status da resposta
        logging.info(f"📡 Status da resposta IPCA: {response.status_code}")
        
        response.raise_for_status()  # Levanta exceção para códigos de erro HTTP
        
        # Verifica se a resposta não está vazia
        if not response.text.strip():
            logging.warning("Resposta da API de IPCA vazia")
            return None
        
        # Log do conteúdo da resposta para diagnóstico
        response_json = response.json()
        logging.info(f"📊 Conteúdo da resposta de IPCA (primeiros 5 itens): {json.dumps(response_json[:5], ensure_ascii=False, indent=2)}")
        logging.info(f"📊 Total de itens na resposta: {len(response_json)}")
        
        # Converte para DataFrame
        try:
            df = pd.DataFrame(response_json)
            logging.info(f"📊 DataFrame criado com sucesso. Colunas: {df.columns.tolist()}")
            logging.info(f"📊 Primeiras 5 linhas do DataFrame:\n{df.head().to_string()}")
        except Exception as e:
            logging.error(f"Erro ao criar DataFrame a partir da resposta de IPCA: {e}")
            logging.error(f"Tipo de dados da resposta: {type(response_json)}")
            if isinstance(response_json, list) and len(response_json) > 0:
                logging.error(f"Tipo do primeiro item: {type(response_json[0])}")
                logging.error(f"Primeiro item: {response_json[0]}")
            return None
        
        try:
            # Log dos dados brutos para diagnóstico
            logging.info("📊 Dados brutos antes da conversão:")
            logging.info(f"Primeira linha: data={df.iloc[0]['data']}, valor={df.iloc[0]['valor']}")
            logging.info(f"Tipo de dados: data={type(df.iloc[0]['data'])}, valor={type(df.iloc[0]['valor'])}")
            
            # Converte a coluna 'data' para datetime
            if not pd.api.types.is_datetime64_any_dtype(df['data']):
                df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
            
            # Converte a coluna 'valor' para numérico, tratando vírgula como separador decimal
            if not pd.api.types.is_numeric_dtype(df['valor']):
                # Tenta converter para string, substituir vírgula por ponto e depois para float
                df['valor'] = pd.to_numeric(
                    df['valor'].astype(str).str.replace(',', '.'), 
                    errors='coerce'
                )
            
            # Remove linhas com valores nulos
            initial_count = len(df)
            df = df.dropna(subset=['data', 'valor'])
            if len(df) < initial_count:
                logging.warning(f"⚠️ Removidas {initial_count - len(df)} linhas com valores nulos")
            
            # Ordena por data
            df = df.sort_values('data')
            
            # Log dos dados convertidos
            logging.info("📊 Dados após conversão:")
            logging.info(f"Primeira linha: data={df.iloc[0]['data']}, valor={df.iloc[0]['valor']}")
            logging.info(f"Tipo de dados: data={type(df.iloc[0]['data'])}, valor={type(df.iloc[0]['valor'])}")
            
            # Prepara o resultado para o gráfico
            result = {
                'dates': [d.date() for d in df['data']],  # Converte para date (sem hora)
                'values': df['valor'].tolist(),
                'label': 'IPCA - Índice Nacional de Preços ao Consumidor Amplo',
                'unit': '%'
            }
        except Exception as e:
            logging.error(f"❌ Erro ao processar dados do IPCA: {e}")
            logging.error(f"Colunas disponíveis: {df.columns.tolist()}")
            if 'data' in df.columns:
                logging.error(f"Valores únicos em 'data': {df['data'].unique()[:5]}")
            if 'valor' in df.columns:
                logging.error(f"Valores únicos em 'valor': {df['valor'].astype(str).unique()[:5]}")
            return None
        
        # Log de diagnóstico
        logging.info(f"✅ Dados de IPCA processados:")
        logging.info(f"   Número de registros: {len(result['dates'])}")
        logging.info(f"   Período: {result['dates'][0]} a {result['dates'][-1]}")
        logging.info(f"   Primeiro valor: {result['values'][0]}")
        logging.info(f"   Último valor: {result['values'][-1]}")
        
        return result
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro de requisição na API de IPCA: {e}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado ao buscar dados de IPCA: {e}")
        return None



# ----------------- SELIC -------- ------------------------------------------

def get_selic_data(period_start=None, period_end=None):
    """
    Obtém dados da Taxa SELIC do Banco Central do Brasil
    """
    try:
        logging.info("Iniciando busca de dados da SELIC")
        
        # URL para dados da SELIC mensal
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json"
        
        # Adicionar headers para evitar bloqueios
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        logging.info(f"Status da resposta SELIC: {response.status_code}")
        logging.info(f"Conteúdo da resposta: {response.text[:500]}...")  # Mostra os primeiros 500 caracteres
        
        if response.status_code != 200:
            logging.error(f"Erro na requisição da SELIC: {response.status_code}")
            return None
        
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as json_err:
            logging.error(f"Erro de decodificação JSON: {json_err}")
            logging.error(f"Conteúdo da resposta: {response.text}")
            return None
        
        # Processamento dos dados
        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        
        # Filtrar dados a partir de 2012
        df = df[df['data'] >= '2012-01-01']
        
        # Agrupar por mês (média mensal)
        #df_monthly = df.groupby(pd.Grouper(key='data', freq='M')).mean().reset_index()
        
        result = {
             'dates': df['data'].dt.strftime('%Y-%m-01').tolist(),
             'values': df['valor'].tolist(),
             'label': 'Taxa SELIC Mensal',
             'unit': '%'
         }
        
        # result = {
        #     'dates': df_monthly['data'].dt.strftime('%Y-%m-01').tolist(),
        #     'values': df_monthly['valor'].tolist(),
        #     'label': 'Taxa SELIC Mensal',
        #     'unit': '%'
        # }
        
        logging.info(f"Dados da SELIC processados: {len(result['dates'])} registros")
        return result
    
    except Exception as e:
        logging.error(f"Erro ao buscar dados da SELIC: {e}", exc_info=True)
        return None



# ------------------------ CAMBIO ---------------------------------------

def get_cambio_data(start_date=None, end_date=None):
    """
    Obtém dados da Taxa de Câmbio do Brasil
    Série 1 - Taxa acumulada no mês
    """
    try:
        # Se não foi especificada uma data final, usa a data atual
        if end_date is None:
            end_date = date.today()
        else:
            end_date = pd.to_datetime(end_date).date()
            
        # Converte as datas para o formato da API
        if start_date is None:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = pd.to_datetime(start_date).date()

        start = pd.to_datetime(start_date).strftime("%d/%m/%Y")
        end = pd.to_datetime(end_date).strftime("%d/%m/%Y")
            
        # URL da API do BCB
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados?formato=json&dataInicial={start}&dataFinal={end}"
        
        # Faz a requisição com timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Levanta exceção para códigos de erro HTTP
        
        # Verifica se a resposta não está vazia
        if not response.text.strip():
            logging.warning("Resposta da API de Câmbio vazia")
            return None
        
        # Converte para DataFrame
        try:
            df = pd.DataFrame(response.json())
        except json.JSONDecodeError:
            logging.error("Erro ao decodificar JSON da resposta de Câmbio")
            return None
        
        # Converte data e valor
        df['data'] = pd.to_datetime(df['data'], format="%d/%m/%Y")
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        
        # Remove valores nulos
        df = df.dropna()
        
        # Ordena por data
        df = df.sort_values('data')
        
        # Prepara o resultado para o gráfico
        result = {
            'dates': [pd.to_datetime(date).date() for date in df['data']],
            'values': df['valor'].tolist(),
            'label': 'Taxa de Câmbio Livre - PTAX, diária (venda)',
            'unit': 'R/US'
        }
        
        # Log de diagnóstico
        logging.info(f"✅ Dados de Câmbio processados:")
        logging.info(f"   Número de registros: {len(result['dates'])}")
        logging.info(f"   Período: {result['dates'][0]} a {result['dates'][-1]}")
        logging.info(f"   Primeiro valor: {result['values'][0]}")
        logging.info(f"   Último valor: {result['values'][-1]}")
        
        return result
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro de requisição na API de Câmbio: {e}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado ao buscar dados de Câmbio: {e}")
        return None

# ----------------- SALDO BC da PARAÍBA---------------- ------------------------------------------

def get_bcpb_data(period_start=None, period_end=None):
    """
    Obtém dados da Balança comercial da Paraíba
    """
    try:
        logging.info("Iniciando busca de dados do BCPB")
        
        # URL para dados do BCPB mensal
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.13352/dados?formato=json"
        
        # Adicionar headers para evitar bloqueios
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        logging.info(f"Status da resposta BCPB: {response.status_code}")
        logging.info(f"Conteúdo da resposta: {response.text[:500]}...")  # Mostra os primeiros 500 caracteres
        
        if response.status_code != 200:
            logging.error(f"Erro na requisição do BCPB: {response.status_code}")
            return None
        
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as json_err:
            logging.error(f"Erro de decodificação JSON: {json_err}")
            logging.error(f"Conteúdo da resposta: {response.text}")
            return None
        
        # Processamento dos dados
        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        
        # Filtrar dados a partir de 2002
        df = df[df['data'] >= '2002-01-01']
        
        df.set_index('data', inplace=True)
        
        # Ordenar por data
        df = df.sort_index()
        
        result = {
            'dates': df.index.strftime('%Y%m%d'),  # Formato YYYYMMDD
            'values': df['valor'],
            'label': 'Saldo da Balança Comercial da Paraíba',
            'unit': 'Milhões de Reais'
        }
        
        logging.info(f"Dados do BCPB processados: {len(result['dates'])} registros")
        return result
    
    except Exception as e:
        logging.error(f"Erro ao buscar dados do BCPB: {e}", exc_info=True)
        return None



# ----------------- Dívida líquida do Governo da PB ---------------------------------------

def get_divliq_data(period_start=None, period_end=None):
    """
    Obtém dados da Dívida Líquida do Governo do Estado da Paraíba
    
    Args:
        period_start (str, optional): Data de início do período
        period_end (str, optional): Data de fim do período
    
    Returns:
        dict: Dicionário com dados processados ou None em caso de erro
    """
    # Configurar headers para evitar bloqueios
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.bcb.gov.br/'
    }
    
    # URL para dados do DIVLIQ mensal
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.15543/dados?formato=json"
    
    logging.info("🔍 Iniciando busca de dados do DIVLIQ")
    logging.info(f"🌐 URL de requisição: {url}")
    
    try:

        # Realizar requisição à API com retry
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry

        retry_strategy = Retry(
            total=3,  # Número total de tentativas
            status_forcelist=[429, 500, 502, 503, 504],  # Códigos de status para retry
            allowed_methods=["GET"],
            backoff_factor=1  # Tempo entre as tentativas aumenta exponencialmente
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)    


        # Realizar requisição à API
        response = session.get(url, headers=headers, timeout=30)
        
        # Registrar detalhes da resposta
        logging.info(f"📡 Status da resposta DIVLIQ: {response.status_code}")
        
        # Verificação de conteúdo
        if response.status_code != 200:
            logging.error(f"❌ Erro na requisição do DIVLIQ: {response.status_code}")
            logging.error(f"🔍 Detalhes da resposta: {response.text[:500]}")
            return None
        
        # Decodificar JSON com tratamento de erro
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as json_err:
            logging.error(f"❌ Erro de decodificação JSON: {json_err}")
            logging.error(f"📄 Conteúdo da resposta: {response.text[:1000]}")
            return None
        
        # Validação dos dados recebidos
        if not isinstance(data, list):
            logging.error(f"❌ Dados recebidos não são uma lista: {type(data)}")
            return None
        
        # Verificação de registros
        if not data:
            logging.warning("⚠️ Nenhum registro recebido")
            return None
        
        # Criar DataFrame com validação
        try:
            df = pd.DataFrame(data)
            
            # Verificar e renomear colunas
            if set(df.columns) != {'data', 'valor'}:
                logging.warning(f"⚠️ Colunas inesperadas: {df.columns}")
                df = df.rename(columns={'data': 'data', 'valor': 'valor'})
            
            # Conversão de tipos
            df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
            
            # Ordenar por data
            df = df.sort_values('data')
            
            # Preparar resultado
            result = {
                'dates': df['data'].dt.date.tolist(),
                'values': df['valor'].tolist(),
                'label': 'Dívida Líquida do Governo do Estado da Paraíba',
                'unit': 'Milhões de Reais',
                'data_inicio': df['data'].min().strftime('%Y-%m-%d'),
                'data_fim': df['data'].max().strftime('%Y-%m-%d')
            }
            
            # Logs de diagnóstico
            logging.info(f"✅ Dados processados:")
            logging.info(f"   Número de registros: {len(result['dates'])}")
            logging.info(f"   Período: {result['data_inicio']} a {result['data_fim']}")
            logging.info(f"   Primeiro valor: {result['values'][0]}")
            logging.info(f"   Último valor: {result['values'][-1]}")
            
            return result
        
        except Exception as e:
            logging.error(f"❌ Erro no processamento dos dados: {e}")
            return None
    
    except requests.RequestException as req_err:
        logging.error(f"❌ Erro de requisição: {req_err}")
        return None
    except Exception as e:
        logging.error(f"❌ Erro inesperado: {e}")
        return None