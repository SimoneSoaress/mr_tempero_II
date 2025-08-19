#routes.py --> Definição das rotas

from flask import render_template
from app import app

# Rotas para usuários deslogados
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')
    
@app.route('/logout')
def logout():
    # Aqui iria a lógica de logout
    return "Usuário deslogado! <a href='/'>Voltar</a>"

# Rotas principais da plataforma
@app.route('/anuncios')
def anuncios():
    return render_template('anuncios.html')

# Rotas da área "Minha Conta"
@app.route('/meus-anuncios')
def meus_anuncios():
    return render_template('meus_anuncios.html')

@app.route('/meus-anuncios/novo')
def novo_anuncio():
    # Usamos o mesmo template, mas aqui iria a lógica de criação
    return f"<h1>Criar Novo Anúncio</h1><a href='/meus-anuncios'>Voltar</a>"

@app.route('/minhas-compras')
def minhas_compras():
    return render_template('minhas_compras.html')

@app.route('/minhas-vendas')
def minhas_vendas():
    return render_template('minhas_vendas.html')

@app.route('/meus-favoritos')
def meus_favoritos():
    return render_template('meus_favoritos.html')

@app.route('/perfil')
def perfil():
    return "<h1>Meu Perfil</h1>"