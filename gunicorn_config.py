# gunicorn_config.py
import multiprocessing

# Número de workers (geralmente 2-4 * número de núcleos de CPU)
workers = multiprocessing.cpu_count() * 2

# Tipo de worker (gevent para I/O bound, sync para CPU bound)
worker_class = 'gevent'

# Porta para bind
bind = "0.0.0.0:8000"

# Tempo limite para requisições
timeout = 120

# Máximo de requisições antes de reiniciar o worker
max_requests = 1000

# Logging
accesslog = '-'  # stdout
errorlog = '-'   # stderr
loglevel = 'info'