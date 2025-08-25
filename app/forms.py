from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField, SelectField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User

class CategoryForm(FlaskForm):
    name = StringField('Nome da Categoria', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Salvar Categoria')

class AnnouncementForm(FlaskForm):
    title = StringField('Título do Anúncio', validators=[DataRequired(), Length(min=5, max=120)])
    description = TextAreaField('Descrição')
    price = FloatField('Preço', validators=[DataRequired()])

    # O campo de categoria 
    category = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Salvar Anúncio')
    
class RegistrationForm(FlaskForm):
    username = StringField('Nome de Utilizador', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    password2 = PasswordField(
        'Repetir Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')])
    submit = SubmitField('Registar')

    # Funções que verificam se o username e o email já existem na base de dados
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Este nome de utilizador já existe. Por favor, escolha outro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Este email já está a ser utilizado. Por favor, escolha outro.')