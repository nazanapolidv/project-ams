from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from dotenv import load_dotenv
from models import db, Usuario
import os

load_dotenv()

app = Flask(__name__)

user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
db_name = os.getenv("MYSQL_DB")

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{user}:{password}@{host}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'clave_secreta_muy_dificil' 

db.init_app(app)

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None 
    else:
        g.user = Usuario.query.get(user_id)


@app.route('/', methods=['GET', 'POST'])
def login():
    if g.user:
        if g.user.rol.lower() == 'cliente':
            return redirect(url_for('cliente'))
        elif g.user.rol.lower() == 'gerente':
            return redirect(url_for('gerente'))

    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']

        usuario = Usuario.query.filter_by(email=email, contraseña=contraseña).first()

        if usuario:
            session.clear()
            session['user_id'] = usuario.id_usuario
            if usuario.rol.lower() == 'cliente':
                return redirect(url_for('cliente'))
            elif usuario.rol.lower() == 'gerente':
                return redirect(url_for('gerente'))
            else:
                flash('Rol no reconocido', 'danger')
        else:
            flash('Email o contraseña incorrectos', 'danger')

    return render_template('login.html')


@app.route('/cliente')
def cliente():
    if not g.user or g.user.rol.lower() != 'cliente':
        flash('Debes iniciar sesión como cliente para ver esta página.', 'warning')
        return redirect(url_for('login'))

    return render_template('cliente.html', usuario=g.user)


@app.route('/gerente')
def gerente():
    if not g.user or g.user.rol.lower() != 'gerente':
        flash('Debes iniciar sesión como gerente para ver esta página.', 'warning')
        return redirect(url_for('login'))

    return render_template('gerente.html', usuario=g.user)


@app.route('/logout')
def logout():
    session.clear()
    flash('Cerraste sesión exitosamente.', 'success')
    return redirect(url_for('login'))