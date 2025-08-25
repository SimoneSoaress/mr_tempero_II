# app/models.py

from app import db, login_manager # Importa db e login_manager do __init__.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Esta função diz ao Flask-Login como encontrar um utilizador
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Suas Classes de Modelo ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    announcements = db.relationship('Announcement', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    # Chave estrangeira para a categoria
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # ..chave estrangeira para o usuário
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Announcement {self.title}>'