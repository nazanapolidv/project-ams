from flask import Flask, render_template, request, redirect, url_for, flash
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
app.config['SECRET_KEY'] = 'clave_secreta'


db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']

        usuario = Usuario.query.filter_by(email=email, contraseña=contraseña).first()

        if usuario:
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
    return render_template('cliente.html')


@app.route('/gerente')
def gerente():
    return render_template('gerente.html')
