#__init__.py --> Configuração do app

from flask import Flask

app = Flask(__name__)

# Importa as rotas depois de criar o app para evitar importação circular
from app import routes
