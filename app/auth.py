from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, db
from .models import Product

auth = Blueprint('auth', __name__)

@auth.route('/cadastro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        user_existente = User.query.filter_by(email=email).first()
        if user_existente:
            flash('Email já cadastrado.')
            return redirect(url_for('auth.register'))

        senha_hash = generate_password_hash(senha)

        novo_user = User(nome=nome, email=email, senha=senha_hash)
        db.session.add(novo_user)
        db.session.commit()

        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('auth.login'))

    return render_template("cadastro.html")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Email ou senha incorretos.')

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))