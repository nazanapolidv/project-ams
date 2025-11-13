from datetime import date

from flask import Blueprint, render_template, redirect, url_for, flash, g

from models import db, Pedido, Contenedor, Revision, RegestionEnvios


gerente_bp = Blueprint('gerente', __name__)


@gerente_bp.route('/gerente')
def dashboard():
    if not g.user or g.user.rol.lower() != 'gerente':
        flash('Debes iniciar sesión como gerente para ver esta página.', 'warning')
        return redirect(url_for('auth.login'))

    todos_los_pedidos = Pedido.query.order_by(Pedido.fecha.desc()).all()
    contenedores = Contenedor.query.all()
    todos_los_envios = RegestionEnvios.query.all()

    return render_template(
        'gerente.html',
        usuario=g.user,
        pedidos=todos_los_pedidos,
        contenedores=contenedores,
        regestionenvios=todos_los_envios,
    )


@gerente_bp.route('/rechazar_pedido/<int:pedido_id>', methods=['POST'])
def rechazar_pedido(pedido_id):
    if not g.user or g.user.rol.lower() != 'gerente':
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('auth.login'))

    pedido = db.session.get(Pedido, pedido_id)
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

    return redirect(url_for('gerente.dashboard'))


@gerente_bp.route('/aprobar_pedido/<int:pedido_id>', methods=['POST'])
def aprobar_pedido(pedido_id):
    if not g.user or g.user.rol.lower() != 'gerente':
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('auth.login'))

    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        flash('Pedido no encontrado.', 'danger')
        return redirect(url_for('gerente.dashboard'))

    if pedido.estado != 'pendiente':
        flash(
            f'El pedido #{pedido.id_pedido} ya no estaba pendiente.', 'warning')
        return redirect(url_for('gerente.dashboard'))

    volumen_pedido = getattr(pedido, 'volumen_total_m3', 0)
    contenedor_disponible = Contenedor.query.filter(
        Contenedor.estado == 'disponible',
        Contenedor.capacidad - Contenedor.ocupacion_actual >= volumen_pedido,
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
            id_usuario=g.user.id_usuario,
        )
        db.session.add(nueva_revision)

        db.session.flush()

        nuevo_envio = RegestionEnvios(
            fecha=date.today(),
            tracking='Pendiente',
            estado_envio='en_preparacion',
            transportista='A definir',
            id_pedido=pedido.id_pedido,
            id_revision=nueva_revision.id_revision,
        )
        db.session.add(nuevo_envio)

        db.session.commit()
        flash(
            f'Pedido #{pedido.id_pedido} aprobado. Revisión y envío inicial creados.', 'success')
    else:
        flash(
            f'No hay contenedores disponibles para el pedido #{pedido.id_pedido}.', 'danger')

    return redirect(url_for('gerente.dashboard'))
