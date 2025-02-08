import logging
import pandas as pd
import requests
import itertools
from datetime import date, timedelta
from tenacity import retry, stop_after_attempt, wait_fixed



# ----------------- IPCA ---------------- ------------------------------------------

def get_ipca_data(period_start=None, period_end=None):
    """
    Obtém dados do IPCA do Banco Central do Brasil
    """
    try:
        logging.info("Iniciando busca de dados do IPCA")
        
        # URL para dados do IPCA mensal
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json"
        
        # Adicionar headers para evitar bloqueios
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        logging.info(f"Status da resposta IPCA: {response.status_code}")
        logging.info(f"Conteúdo da resposta: {response.text[:500]}...")  # Mostra os primeiros 500 caracteres
        
        if response.status_code != 200:
            logging.error(f"Erro na requisição do IPCA: {response.status_code}")
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
        df = df[df['data'] >= '01/01/2012']
        
        df.set_index('data', inplace=True)
        
        # Ordenar por data
        df = df.sort_index()
        
        result = {
            'dates': df.index.strftime('%Y%m'),  # Formato YYYYMM
            'ipca': df['valor'],
            }
        
        logging.info(f"Dados do IPCA processados: {len(result['dates'])} registros")
        return df
    
    except Exception as e:
        logging.error(f"Erro ao buscar dados do IPCA: {e}", exc_info=True)
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
        df_monthly = df.groupby(pd.Grouper(key='data', freq='M')).mean().reset_index()
        
        result = {
            'dates': df_monthly['data'].dt.strftime('%Y-%m').tolist(),
            'values': df_monthly['valor'].tolist(),
            'label': 'Taxa SELIC Mensal',
            'unit': '%'
        }
        
        logging.info(f"Dados da SELIC processados: {len(result['dates'])} registros")
        return result
    
    except Exception as e:
        logging.error(f"Erro ao buscar dados da SELIC: {e}", exc_info=True)
        return None



# ------------------------ CAMBIO ---------------------------------------

def get_cambio_data(start_date=None, end_date=None): #get_elic_data(start_date="2000-01-01", end_date=None):
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
        
        # Faz a requisição
        response = requests.get(url)
        response.raise_for_status()
        
        # Converte para DataFrame
        df = pd.DataFrame(response.json())
        
        # Converte data e valor
        df['data'] = pd.to_datetime(df['data'], format="%d/%m/%Y")
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        
        # Remove valores nulos
        df = df.dropna()
        
        # Ordena por data
        df = df.sort_values('data')
        
        # Prepara o resultado para o gráfico
        result = {
            'dates': df['data'].dt.strftime('%Y-%m-%d').tolist(),
            'values': df['valor'].tolist(),
            'label': 'Taxa de Câmbio Livre - PTAX, diária (venda)',
            'unit': 'R/US'
        }
        
        return result
    
    except Exception as e:
        print(f"Erro ao buscar dados da Câmbio {str(e)}")
        # return {
        #     'dates': [],
        #     'values': [],
        #     'label': 'Taxa SELIC',
        #     'unit': '% ao mês'
        # }
        return None
    r
    #linhas adicionadas
    
    cache_key_str = cache_key('cambio', start=start_date, end=end_date), cache_key('ipca', start=start_date, end=end_date)
    return get_cached_data(cache_key_str, fetch_data, expires_in=3600)      


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