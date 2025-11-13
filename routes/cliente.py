from datetime import date
from decimal import Decimal

from flask import Blueprint, render_template, request, redirect, url_for, flash, g

from models import db, Cliente, Pedido, Producto, ItemPedido, Deposito


cliente_bp = Blueprint('cliente', __name__)


@cliente_bp.route('/cliente')
def dashboard():
    if not g.user or g.user.rol.lower() != 'cliente':
        flash('Debes iniciar sesión como cliente para ver esta página.', 'warning')
        return redirect(url_for('auth.login'))

    cliente = Cliente.query.filter_by(email="ana.gomez@hotmail.com").first()

    if not cliente:
        flash('No se encontró el cliente asociado al usuario.', 'danger')
        return redirect(url_for('auth.logout'))

    pedidos = Pedido.query.filter_by(
        id_cliente=cliente.id_cliente).order_by(Pedido.fecha.desc()).all()

    return render_template('cliente.html', usuario=g.user, cliente=cliente, pedidos=pedidos)


@cliente_bp.route('/cliente/nuevo_pedido', methods=['GET', 'POST'])
def nuevo_pedido():
    if not g.user or g.user.rol.lower() != 'cliente':
        flash('Debes iniciar sesión como cliente para crear pedidos.', 'warning')
        return redirect(url_for('auth.login'))

    cliente = Cliente.query.filter_by(email="ana.gomez@hotmail.com").first()
    productos = Producto.query.all()
    deposito = Deposito.query.first()

    if request.method == 'POST':
        nuevo_pedido = Pedido(
            fecha=date.today(),
            estado='pendiente',
            id_cliente=cliente.id_cliente,
            id_usuario=g.user.id_usuario,
            id_deposito=deposito.id_deposito,
            total=Decimal('0.0'),
            volumen_total_m3=Decimal('0.0')
        )
        db.session.add(nuevo_pedido)
        db.session.flush()

        for producto in productos:
            cantidad = request.form.get(f'cantidad_{producto.sku}')
            if cantidad and int(cantidad) > 0:
                item = ItemPedido(
                    id_pedido=nuevo_pedido.id_pedido,
                    sku=producto.sku,
                    cantidad=int(cantidad),
                    precio=producto.precio_unitario
                )
                db.session.add(item)

        db.session.commit()
        flash('Pedido creado exitosamente.', 'success')
        return redirect(url_for('cliente.dashboard'))

    return render_template('nuevo_pedido.html', usuario=g.user, productos=productos)
