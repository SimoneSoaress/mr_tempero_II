import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, DateField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from .models import User # novo modelo User
from wtforms import PasswordField # formulário de login


# ====================================
# CONFIGURAÇÃO DA APLICAÇÃO FLASK
# ====================================

# Configuração base do projeto
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # rota de login
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "Espere"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.config['SECRET_KEY'] = 'TOLEDO-FRAMEWORK-FLASK'

# Configuração do banco de dados SQLite para simplicidade
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ecommerce.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# =========================================
# ESTRUTURA DO BANCO DE DADOS
# =========================================

class Category(db.Model):
    """Modelo para Categorias de Produtos."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    products = db.relationship('Product', backref='category', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    """Modelo para Produtos (Temperos)."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    sku = db.Column(db.String(50), nullable=False, unique=True)
    origin = db.Column(db.String(100), nullable=True)
    spiciness_level = db.Column(db.Integer, nullable=True) # Escala de 1 a 5
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

class Customer(db.Model):
    """Modelo para Clientes."""
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Customer {self.first_name} {self.last_name}>'

class Coupon(db.Model):
    """Modelo para Cupons de Desconto."""
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_type = db.Column(db.String(20), nullable=False, default='percentage') # 'percentage' or 'fixed'
    value = db.Column(db.Float, nullable=False)
    expiration_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Coupon {self.code}>'

# ===========================
# FORMULÁRIOS (WTForms)
# ===========================

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])

class CategoryForm(FlaskForm):
    """Formulário para criar/editar Categorias."""
    name = StringField('Nome da Categoria', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Descrição', validators=[Optional(), Length(max=500)])

class ProductForm(FlaskForm):
    """Formulário para criar/editar Produtos."""
    name = StringField('Nome do Produto', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Descrição', validators=[DataRequired()])
    price = FloatField('Preço', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Estoque', validators=[DataRequired(), NumberRange(min=0)])
    sku = StringField('SKU (Código)', validators=[DataRequired(), Length(max=50)])
    origin = StringField('Origem', validators=[Optional(), Length(max=100)])
    spiciness_level = SelectField('Nível de Picância', choices=[(0, 'N/A')] + [(i, str(i)) for i in range(1, 6)], coerce=int, validators=[Optional()])
    category_id = SelectField('Categoria', coerce=int, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]

class CustomerForm(FlaskForm):
    """Formulário para criar/editar Clientes."""
    first_name = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Sobrenome', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Length(max=120)])
    phone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    address = StringField('Endereço', validators=[Optional(), Length(max=255)])
    city = StringField('Cidade', validators=[Optional(), Length(max=100)])
    state = StringField('Estado', validators=[Optional(), Length(max=50)])
    zip_code = StringField('CEP', validators=[Optional(), Length(max=20)])

class CouponForm(FlaskForm):
    """Formulário para criar/editar Cupons."""
    code = StringField('Código do Cupom', validators=[DataRequired(), Length(max=50)])
    discount_type = SelectField('Tipo de Desconto', choices=[('percentage', 'Percentual (%)'), ('fixed', 'Valor Fixo (R$)')], validators=[DataRequired()])
    value = FloatField('Valor', validators=[DataRequired(), NumberRange(min=0)])
    expiration_date = DateField('Data de Expiração', format='%Y-%m-%d', validators=[Optional()])
    is_active = BooleanField('Ativo', default=True)

# =================
# ROTAS (VIEWS)
# =================

# --- Rotas de Autenticação ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    # usuário logado, redireciona para a página principal
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # formulário 
    form = LoginForm()

    # o formulário foi enviado e é válido...
    if form.validate_on_submit():
        # Busca o usuário no banco de dados pelo username digitado
        user = User.query.filter_by(username=form.username.data).first()

        # verifica se o usuário existe OU se a senha está incorreta
        if user is None or not user.check_password(form.password.data):
            flash('Usuário ou senha inválidos.', 'danger') # Mostrar mensagem de erro
            return redirect(url_for('login')) # Envia de volta para a página de login

        # se tudo estiver correto, loga o usuário no sistema
        login_user(user)
        # redireciona para a página principal 
        return redirect(url_for('index'))

    # primeiro acesso à página, mostra o HTML do login
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required 
def logout():
    logout_user() 
    flash('Você foi desconectado com sucesso.', 'success') 
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Página inicial do painel administrativo."""
    product_count = Product.query.count()
    category_count = Category.query.count()
    customer_count = Customer.query.count()
    return render_template_string(
        HOME_TEMPLATE, 
        product_count=product_count,
        category_count=category_count,
        customer_count=customer_count
    )

# --- CRUD Categorias ---
@app.route('/categories')
def list_categories():
    categories = Category.query.all()
    return render_template_string(LIST_TEMPLATE, title='Categorias', items=categories, fields=['id', 'name', 'description'], endpoint='category')

@app.route('/category/new', methods=['GET', 'POST'])
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        new_category = Category(name=form.name.data, description=form.description.data)
        db.session.add(new_category)
        db.session.commit()
        flash('Categoria criada com sucesso!', 'success')
        return redirect(url_for('list_categories'))
    return render_template_string(FORM_TEMPLATE, form=form, title='Nova Categoria')

@app.route('/category/edit/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('list_categories'))
    return render_template_string(FORM_TEMPLATE, form=form, title='Editar Categoria')

@app.route('/category/delete/<int:id>', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Categoria excluída com sucesso!', 'danger')
    return redirect(url_for('list_categories'))

# --- CRUD Produtos ---
@app.route('/products')
def list_products():
    products = Product.query.all()
    return render_template_string(LIST_TEMPLATE, title='Produtos', items=products, fields=['id', 'name', 'price', 'stock', 'sku', 'category'], endpoint='product')

@app.route('/product/new', methods=['GET', 'POST'])
def create_product():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            sku=form.sku.data,
            origin=form.origin.data,
            spiciness_level=form.spiciness_level.data,
            category_id=form.category_id.data
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Produto criado com sucesso!', 'success')
        return redirect(url_for('list_products'))
    return render_template_string(FORM_TEMPLATE, form=form, title='Novo Produto')

@app.route('/product/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.sku = form.sku.data
        product.origin = form.origin.data
        product.spiciness_level = form.spiciness_level.data
        product.category_id = form.category_id.data
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('list_products'))
    return render_template_string(FORM_TEMPLATE, form=form, title='Editar Produto')

@app.route('/product/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produto excluído com sucesso!', 'danger')
    return redirect(url_for('list_products'))

# --- CRUD Clientes ---
@app.route('/customers')
def list_customers():
    customers = Customer.query.all()
    return render_template_string(LIST_TEMPLATE, title='Clientes', items=customers, fields=['id', 'first_name', 'last_name', 'email', 'phone'], endpoint='customer')

@app.route('/customer/new', methods=['GET', 'POST'])
def create_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        new_customer = Customer(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data
        )
        db.session.add(new_customer)
        db.session.commit()
        flash('Cliente criado com sucesso!', 'success')
        return redirect(url_for('list_customers'))
    return render_template_string(FORM_TEMPLATE, form=form, title='Novo Cliente')

@app.route('/customer/edit/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        customer.first_name = form.first_name.data
        customer.last_name = form.last_name.data
        customer.email = form.email.data
        customer.phone = form.phone.data
        customer.address = form.address.data
        customer.city = form.city.data
        customer.state = form.state.data
        customer.zip_code = form.zip_code.data
        db.session.commit()
        flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('list_customers'))
    return render_template_string(FORM_TEMPLATE, form=form, title='Editar Cliente')

@app.route('/customer/delete/<int:id>', methods=['POST'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('Cliente excluído com sucesso!', 'danger')
    return redirect(url_for('list_customers'))

# --- CRUD Cupons ---
@app.route('/coupons')
def list_coupons():
    coupons = Coupon.query.all()
    return render_template_string(LIST_TEMPLATE, title='Cupons', items=coupons, fields=['id', 'code', 'discount_type', 'value', 'is_active'], endpoint='coupon')

@app.route('/coupon/new', methods=['GET', 'POST'])
def create_coupon():
    form = CouponForm()
    if form.validate_on_submit():
        new_coupon = Coupon(
            code=form.code.data,
            discount_type=form.discount_type.data,
            value=form.value.data,
            expiration_date=form.expiration_date.data,
            is_active=form.is_active.data
        )
        db.session.add(new_coupon)
        db.session.commit()
        flash('Cupom criado com sucesso!', 'success')
        return redirect(url_for('list_coupons'))
    return render_template_string(FORM_TEMPLATE, form=form, title='Novo Cupom')

@app.route('/coupon/edit/<int:id>', methods=['GET', 'POST'])
def edit_coupon(id):
    coupon = Coupon.query.get_or_404(id)
    form = CouponForm(obj=coupon)
    if form.validate_on_submit():
        coupon.code = form.code.data
        coupon.discount_type = form.discount_type.data
        coupon.value = form.value.data
        coupon.expiration_date = form.expiration_date.data
        coupon.is_active = form.is_active.data
        db.session.commit()
        flash('Cupom atualizado com sucesso!', 'success')
        return redirect(url_for('list_coupons'))
    return render_template_string(FORM_TEMPLATE, form=form, title='Editar Cupom')

@app.route('/coupon/delete/<int:id>', methods=['POST'])
def delete_coupon(id):
    coupon = Coupon.query.get_or_404(id)
    db.session.delete(coupon)
    db.session.commit()
    flash('Cupom excluído com sucesso!', 'danger')
    return redirect(url_for('list_coupons'))

# ===============================================
# TEMPLATES.. HTML COMO STRINGS
# ===============================================

# --- Template Base ---
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Admin Aroma & Sabor</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 font-sans leading-normal tracking-normal">
    <div class="flex md:flex-row-reverse flex-wrap">
        <!-- Main Content -->
        <div class="w-full md:w-4/5 bg-gray-100">
            <div class="container bg-gray-100 pt-16 px-6 mx-auto">
                <!-- Flash Messages -->
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="p-4 mb-4 text-sm rounded-lg 
                                {% if category == 'success' %} bg-green-100 text-green-700 {% endif %}
                                {% if category == 'danger' %} bg-red-100 text-red-700 {% endif %}
                                {% if category == 'warning' %} bg-yellow-100 text-yellow-700 {% endif %}"
                                role="alert">
                                <span class="font-medium">{{ message }}</span>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                {% block content %}{% endblock %}
            </div>
        </div>

        <!-- Sidebar -->
        <div class="w-full md:w-1/5 bg-gray-800 md:min-h-screen">
            <div class="md:relative mx-auto lg:float-right lg:px-6">
                <ul class="list-reset flex flex-row md:flex-col text-center md:text-left">
                    <li class="mr-3 flex-1">
                        <a href="{{ url_for('index') }}" class="block py-4 px-4 align-middle text-gray-400 no-underline hover:text-white border-b-2 border-gray-800 hover:border-pink-500">
                            <i class="fas fa-tachometer-alt pr-0 md:pr-3"></i><span class="pb-1 md:pb-0 text-sm">Dashboard</span>
                        </a>
                    </li>
                    <li class="mr-3 flex-1">
                        <a href="{{ url_for('list_categories') }}" class="block py-4 px-4 align-middle text-gray-400 no-underline hover:text-white border-b-2 border-gray-800 hover:border-purple-500">
                            <i class="fa fa-tags pr-0 md:pr-3"></i><span class="pb-1 md:pb-0 text-sm">Categorias</span>
                        </a>
                    </li>
                    <li class="mr-3 flex-1">
                        <a href="{{ url_for('list_products') }}" class="block py-4 px-4 align-middle text-gray-400 no-underline hover:text-white border-b-2 border-gray-800 hover:border-green-500">
                            <i class="fa fa-pepper-hot pr-0 md:pr-3"></i><span class="pb-1 md:pb-0 text-sm">Produtos</span>
                        </a>
                    </li>
                    <li class="mr-3 flex-1">
                        <a href="{{ url_for('list_customers') }}" class="block py-4 px-4 align-middle text-gray-400 no-underline hover:text-white border-b-2 border-gray-800 hover:border-blue-500">
                            <i class="fa fa-users pr-0 md:pr-3"></i><span class="pb-1 md:pb-0 text-sm">Clientes</span>
                        </a>
                    </li>
                    <li class="mr-3 flex-1">
                        <a href="{{ url_for('list_coupons') }}" class="block py-4 px-4 align-middle text-gray-400 no-underline hover:text-white border-b-2 border-gray-800 hover:border-yellow-500">
                            <i class="fa fa-ticket-alt pr-0 md:pr-3"></i><span class="pb-1 md:pb-0 text-sm">Cupons</span>
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
"""

# --- Template da Home ---
HOME_TEMPLATE = """
{% extends "BASE_TEMPLATE" %}
{% block content %}
<h1 class="text-3xl text-black pb-6">Dashboard</h1>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center">
            <div class="bg-green-500 rounded-full p-3">
                <i class="fa fa-pepper-hot text-white fa-2x"></i>
            </div>
            <div class="ml-4">
                <p class="text-gray-600">Total de Produtos</p>
                <p class="text-2xl font-bold">{{ product_count }}</p>
            </div>
        </div>
    </div>
    <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center">
            <div class="bg-purple-500 rounded-full p-3">
                <i class="fa fa-tags text-white fa-2x"></i>
            </div>
            <div class="ml-4">
                <p class="text-gray-600">Total de Categorias</p>
                <p class="text-2xl font-bold">{{ category_count }}</p>
            </div>
        </div>
    </div>
    <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center">
            <div class="bg-blue-500 rounded-full p-3">
                <i class="fa fa-users text-white fa-2x"></i>
            </div>
            <div class="ml-4">
                <p class="text-gray-600">Total de Clientes</p>
                <p class="text-2xl font-bold">{{ customer_count }}</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# --- Template de Lista ---
LIST_TEMPLATE = """
{% extends "BASE_TEMPLATE" %}
{% block content %}
<div class="flex justify-between items-center pb-6">
    <h1 class="text-3xl text-black">{{ title }}</h1>
    <a href="{{ url_for('create_' + endpoint) }}" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg shadow">
        <i class="fas fa-plus mr-2"></i> Adicionar Novo
    </a>
</div>
<div class="w-full mt-6">
    <div class="bg-white overflow-auto">
        <table class="min-w-full bg-white">
            <thead class="bg-gray-800 text-white">
                <tr>
                    {% for field in fields %}
                    <th class="w-1/4 text-left py-3 px-4 uppercase font-semibold text-sm">{{ field.replace('_', ' ')|title }}</th>
                    {% endfor %}
                    <th class="text-left py-3 px-4 uppercase font-semibold text-sm">Ações</th>
                </tr>
            </thead>
            <tbody class="text-gray-700">
                {% for item in items %}
                <tr class="border-b border-gray-200 hover:bg-gray-100">
                    {% for field in fields %}
                    <td class="py-3 px-4">
                        {% set value = item[field] if field in item else getattr(item, field) %}
                        {% if field == 'category' %}
                            {{ value.name if value else 'N/A' }}
                        {% elif field == 'is_active' %}
                            <span class="{{ 'bg-green-200 text-green-600' if value else 'bg-red-200 text-red-600' }} py-1 px-3 rounded-full text-xs">
                                {{ 'Sim' if value else 'Não' }}
                            </span>
                        {% else %}
                            {{ value }}
                        {% endif %}
                    </td>
                    {% endfor %}
                    <td class="py-3 px-4">
                        <div class="flex item-center space-x-2">
                            <a href="{{ url_for('edit_' + endpoint, id=item.id) }}" class="text-yellow-500 hover:text-yellow-700">
                                <i class="fas fa-pencil-alt"></i>
                            </a>
                            <form action="{{ url_for('delete_' + endpoint, id=item.id) }}" method="POST" onsubmit="return confirm('Tem certeza que deseja excluir este item?');">
                                <button type="submit" class="text-red-500 hover:text-red-700">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </form>
                        </div>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
"""

# --- Template de Formulário ---
FORM_TEMPLATE = """
{% extends "BASE_TEMPLATE" %}
{% block content %}
<h1 class="text-3xl text-black pb-6">{{ title }}</h1>
<div class="w-full mt-6">
    <div class="bg-white p-8 rounded-lg shadow-lg">
        <form method="POST" action="">
            {{ form.hidden_tag() }}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {% for field in form if field.widget.input_type != 'hidden' %}
                <div class="mb-4">
                    {{ field.label(class="block text-gray-700 text-sm font-bold mb-2") }}
                    {% if field.type == 'TextAreaField' %}
                        {{ field(class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-32") }}
                    {% elif field.type == 'BooleanField' %}
                        <div class="mt-2">
                           {{ field(class="mr-2 leading-tight") }} <span class="text-sm">{{ field.label.text }}</span>
                        </div>
                    {% else %}
                        {{ field(class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline") }}
                    {% endif %}
                    {% for error in field.errors %}
                        <p class="text-red-500 text-xs italic">{{ error }}</p>
                    {% endfor %}
                </div>
                {% endfor %}
            </div>
            <div class="flex items-center justify-start mt-6">
                <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                    Salvar
                </button>
                <a href="{{ request.referrer or url_for('index') }}" class="ml-4 inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800">
                    Cancelar
                </a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
"""

# Substitui a referência 
HOME_TEMPLATE = HOME_TEMPLATE.replace('{% extends "BASE_TEMPLATE" %}', '{% extends "base" %}').replace('base', BASE_TEMPLATE)
LIST_TEMPLATE = LIST_TEMPLATE.replace('{% extends "BASE_TEMPLATE" %}', '{% extends "base" %}').replace('base', BASE_TEMPLATE)
FORM_TEMPLATE = FORM_TEMPLATE.replace('{% extends "BASE_TEMPLATE" %}', '{% extends "base" %}').replace('base', BASE_TEMPLATE)


if __name__ == '__main__':
    # Cria o banco de dados e as tabelas se não existirem
    with app.app_context():
        db.create_all()
    app.run(debug=True)
