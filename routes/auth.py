from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models import Usuario


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if g.user:
        if g.user.rol.lower() == 'cliente':
            return redirect(url_for('cliente.dashboard'))
        if g.user.rol.lower() == 'gerente':
            return redirect(url_for('gerente.dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']

        usuario = Usuario.query.filter_by(
            email=email, contraseña=contraseña).first()

        if usuario:
            session.clear()
            session['user_id'] = usuario.id_usuario
            if usuario.rol.lower() == 'cliente':
                return redirect(url_for('cliente.dashboard'))
            if usuario.rol.lower() == 'gerente':
                return redirect(url_for('gerente.dashboard'))
            flash('Rol no reconocido', 'danger')
        else:
            flash('Email o contraseña incorrectos', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Cerraste sesión exitosamente.', 'success')
    return redirect(url_for('auth.login'))
