from flask import Flask
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Criar aplicação Flask
app = Flask(__name__)

# Importar rotas
from app.utils import routes
routes.init_routes(app)  # Inicializa as rotas
