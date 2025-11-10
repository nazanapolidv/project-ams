from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from dotenv import load_dotenv
from models import db, Usuario, Pedido, Producto, Contenedor, Revision, RegestionEnvios
from datetime import date
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

        usuario = Usuario.query.filter_by(
            email=email, contraseña=contraseña).first()

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

    todos_los_pedidos = Pedido.query.order_by(Pedido.fecha.desc()).all()
    contenedores = Contenedor.query.all()
    todos_los_envios = RegestionEnvios.query.all()

    return render_template('gerente.html', usuario=g.user, pedidos=todos_los_pedidos, contenedores=contenedores, regestionenvios=todos_los_envios)


@app.route('/rechazar_pedido/<int:pedido_id>', methods=['POST'])
def rechazar_pedido(pedido_id):
    if not g.user or g.user.rol.lower() != 'gerente':
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('login'))

    pedido = Pedido.query.get(pedido_id)
    if pedido:
        if pedido.estado == 'pendiente':
            pedido.estado = 'cancelado'
            db.session.commit()
            flash(f'Pedido #{pedido.id_pedido} ha sido cancelado.', 'danger')
        else:
            flash(
                f'El pedido #{pedido.id_pedido} ya no estaba pendiente.', 'warning')
    else:
        flash('Pedido no encontrado.', 'danger')

    return redirect(url_for('gerente'))


@app.route('/aprobar_pedido/<int:pedido_id>', methods=['POST'])
def aprobar_pedido(pedido_id):
    if not g.user or g.user.rol.lower() != 'gerente':
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('login'))

    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        flash('Pedido no encontrado.', 'danger')
        return redirect(url_for('gerente'))

    if pedido.estado != 'pendiente':
        flash(
            f'El pedido #{pedido.id_pedido} ya no estaba pendiente.', 'warning')
        return redirect(url_for('gerente'))
    volumen_pedido = getattr(pedido, 'volumen_total_m3', 0)
    contenedor_disponible = Contenedor.query.filter(
        Contenedor.estado == 'disponible',
        Contenedor.capacidad - Contenedor.ocupacion_actual >= volumen_pedido
    ).order_by(Contenedor.capacidad - Contenedor.ocupacion_actual).first()

    if contenedor_disponible:
        pedido.estado = 'aprobado'
        pedido.id_contenedor = contenedor_disponible.id_contenedor

        contenedor_disponible.ocupacion_actual += volumen_pedido
        if contenedor_disponible.ocupacion_actual >= contenedor_disponible.capacidad:
            contenedor_disponible.estado = 'ocupado'

        nueva_revision = Revision(
            fecha=date.today(),
            resultado='aprobado',
            observaciones='Aprobado por gerente y asignado a contenedor.',
            id_pedido=pedido.id_pedido,
            id_usuario=g.user.id_usuario
        )
        db.session.add(nueva_revision)

        db.session.flush()

        nuevo_envio = RegestionEnvios(
            fecha=date.today(),
            tracking='Pendiente',
            estado_envio='en_preparacion',
            transportista='A definir',
            id_pedido=pedido.id_pedido,
            id_revision=nueva_revision.id_revision
        )
        db.session.add(nuevo_envio)

        db.session.commit()
        flash(
            f'Pedido #{pedido.id_pedido} aprobado. Revisión y envío inicial creados.', 'success')
    else:
        flash(
            f'No hay contenedores disponibles para el pedido #{pedido.id_pedido}.', 'danger')

    return redirect(url_for('gerente'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Cerraste sesión exitosamente.', 'success')
    return redirect(url_for('login'))
