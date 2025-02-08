from ipeadatapy import get_series

def get_inflation_data():
    try:
        # IPCA - índice (dez. 1993 = 100)
        ipca = get_series('PRECOS12_IPCA12')
        return ipca
    except Exception as e:
        print(f"Erro ao buscar dados do IPEA: {e}")
        return None