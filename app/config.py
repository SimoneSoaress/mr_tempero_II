# config.py
import os

# Pega o caminho absoluto do diretório do arquivo atual.
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Chave secreta para proteger contra ataques CSRF. Mude para algo aleatório.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'voce-nunca-vai-adivinhar'

    # Configuração do banco de dados SQLAlchemy.
    # Isso cria um arquivo de banco de dados chamado 'app.db' na raiz do projeto.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

    # Desativa um recurso do SQLAlchemy que não usaremos e que emite avisos.
    SQLALCHEMY_TRACK_MODIFICATIONS = False