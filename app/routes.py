# app/routes.py

# 1. Imports Corrigidos
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

# Importa as variáveis principais do __init__.py
from app import app, db, login_manager 
# Importa os formulários do ficheiro forms.py
from app.forms import LoginForm, RegistrationForm, CategoryForm, AnnouncementForm 
# Importa os modelos do ficheiro models.py
from app.models import User, Category, Announcement 


# 2. Função Essencial para o Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Rotas de Autenticação (Com Lógica Completa) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Utilizador ou senha inválidos.', 'danger')
            return redirect(url_for('login'))
        
        login_user(user)
        return redirect(url_for('index'))
        
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sessão terminada com sucesso.', 'success')
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    # Se o utilizador já estiver logado, não pode aceder à página de registo
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Cria um novo User com os dados do formulário
        user = User(username=form.username.data, email=form.email.data)
        # Define a senha 
        user.set_password(form.password.data)
        # Adiciona o novo utilizador à sessão da base de dados
        db.session.add(user)
        # Grava as alterações na base de dados
        db.session.commit()

        flash('Parabéns, o seu registo foi efetuado com sucesso!', 'success')
        return redirect(url_for('login')) # Redireciona para a página de login

    return render_template('cadastro.html', title='Registar', form=form)


# --- Rotas Principais e Protegidas ---

@app.route('/')
@app.route('/index')
@login_required # Protege a página inicial
def index():
    return render_template('index.html')

# --- ROTAS DE CATEGORIA (CRUD) ---

@app.route('/categorias')
@login_required # Protege a rota
def list_categories():
    categories = Category.query.all()
    return render_template('category/list.html', categories=categories) # Supondo que o seu HTML está em templates/category/list.html

@app.route('/categorias/nova', methods=['GET', 'POST'])
@login_required # Protege a rota
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        new_category = Category(name=form.name.data)
        db.session.add(new_category)
        db.session.commit()
        flash('Categoria criada com sucesso!', 'success')
        return redirect(url_for('list_categories'))
    return render_template('category/create_edit.html', form=form, title='Nova Categoria')

@app.route('/categorias/editar/<int:id>', methods=['GET', 'POST'])
@login_required # Protege a rota
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('list_categories'))
    return render_template('category/create_edit.html', form=form, title='Editar Categoria')

@app.route('/categorias/deletar/<int:id>', methods=['POST'])
@login_required # Protege a rota
def delete_category(id):
    category = Category.query.get_or_404(id)
    if category.announcements.count() > 0:
        flash('Não é possível excluir uma categoria que possui anúncios vinculados.', 'danger')
        return redirect(url_for('list_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Categoria excluída com sucesso!', 'success')
    return redirect(url_for('list_categories'))


# --- ROTAS DE ANÚNCIO (CRUD) ---

@app.route('/anuncios')
@login_required # Protege a rota
def list_announcements():
    announcements = Announcement.query.all()
    return render_template('announcement/list.html', announcements=announcements)

@app.route('/anuncios/novo', methods=['GET', 'POST'])
@login_required # Protege a rota
def create_announcement():
    form = AnnouncementForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]
    
    if form.validate_on_submit():
        new_announcement = Announcement(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            category_id=form.category.data
        )
        db.session.add(new_announcement)
        db.session.commit()
        flash('Anúncio criado com sucesso!', 'success')
        return redirect(url_for('list_announcements'))
        
    return render_template('announcement/create_edit.html', form=form, title='Novo Anúncio')

@app.route('/anuncios/editar/<int:id>', methods=['GET', 'POST'])
@login_required # Protege a rota
def edit_announcement(id):
    announcement = Announcement.query.get_or_404(id)
    form = AnnouncementForm(obj=announcement)
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]
    
    if form.validate_on_submit():
        announcement.title = form.title.data
        announcement.description = form.description.data
        announcement.price = form.price.data
        announcement.category_id = form.category.data
        db.session.commit()
        flash('Anúncio atualizado com sucesso!', 'success')
        return redirect(url_for('list_announcements'))
    
    # ..categoria correta esteja selecionada ao carregar
    form.category.data = announcement.category_id
    return render_template('announcement/create_edit.html', form=form, title='Editar Anúncio')

@app.route('/anuncios/deletar/<int:id>', methods=['POST'])
@login_required # Protege a rota
def delete_announcement(id):
    announcement = Announcement.query.get_or_404(id)
    db.session.delete(announcement)
    db.session.commit()
    flash('Anúncio excluído com sucesso!', 'success')
    return redirect(url_for('list_announcements'))