# app/cache.py
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def cached_data_retrieval(data_type, last_updated=None):
    """
    Cacheia resultados de consultas frequentes
    """
    current_time = time.time()
    # Lógica para buscar e cachear dados
    return data