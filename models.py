import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)

    pedidos_gestionados = db.relationship(
        'Pedido', backref='gestor', lazy=True)
    notificaciones_enviadas = db.relationship(
        'Notificacion', backref='usuario_gestor', lazy=True)
    revisiones_hechas = db.relationship(
        'Revision', backref='usuario_revisor', lazy=True)


class Cliente(db.Model):
    __tablename__ = 'cliente'
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100))
    email = db.Column(db.String(255), unique=True, nullable=False)
    telefono = db.Column(db.String(50))
    direccion = db.Column(db.Text)

    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)


class Producto(db.Model):
    __tablename__ = 'producto'
    sku = db.Column(db.String(50), primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    alto = db.Column(db.DECIMAL(10, 2))
    ancho = db.Column(db.DECIMAL(10, 2))
    profundidad = db.Column(db.DECIMAL(10, 2))
    peso = db.Column(db.DECIMAL(10, 2))
    precio_unitario = db.Column(db.DECIMAL(10, 2))

    items_pedido = db.relationship('ItemPedido', backref='producto', lazy=True)


class Deposito(db.Model):
    __tablename__ = 'deposito'
    id_deposito = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    capacidad_contenedores = db.Column(db.Integer)

    contenedores = db.relationship('Contenedor', backref='deposito', lazy=True)
    pedidos_asignados = db.relationship(
        'Pedido', backref='deposito', lazy=True)


class Contenedor(db.Model):
    __tablename__ = 'contenedor'
    id_contenedor = db.Column(db.Integer, primary_key=True)
    capacidad = db.Column(db.Integer)
    ocupacion_actual = db.Column(db.Integer, default=0)
    estado = db.Column(db.String(20))

    id_deposito = db.Column(db.Integer, db.ForeignKey(
        'deposito.id_deposito'), nullable=False)


class Pedido(db.Model):
    __tablename__ = 'pedido'
    id_pedido = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DATE, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    total = db.Column(db.DECIMAL(10, 2), nullable=False)

    id_cliente = db.Column(db.Integer, db.ForeignKey(
        'cliente.id_cliente'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey(
        'usuario.id_usuario'), nullable=False)
    id_deposito = db.Column(db.Integer, db.ForeignKey(
        'deposito.id_deposito'), nullable=False)

    items = db.relationship('ItemPedido', backref='pedido', lazy=True)
    notificaciones = db.relationship(
        'Notificacion', backref='pedido', lazy=True)
    revisiones = db.relationship('Revision', backref='pedido', lazy=True)
    gestiones_envio = db.relationship(
        'RegestionEnvios', backref='pedido', lazy=True)


class ItemPedido(db.Model):
    __tablename__ = 'itempedido'
    id_item = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.DECIMAL(10, 2), nullable=False)

    id_pedido = db.Column(db.Integer, db.ForeignKey(
        'pedido.id_pedido'), nullable=False)
    sku = db.Column(db.String(50), db.ForeignKey(
        'producto.sku'), nullable=False)


class Notificacion(db.Model):
    __tablename__ = 'notificacion'
    id_notif = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    mensaje = db.Column(db.Text)
    fecha = db.Column(db.DATE)

    leido = db.Column(db.Boolean, default=False)

    id_pedido = db.Column(db.Integer, db.ForeignKey(
        'pedido.id_pedido'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey(
        'usuario.id_usuario'), nullable=False)


class Revision(db.Model):
    __tablename__ = 'revision'
    id_revision = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DATE)
    resultado = db.Column(db.String(20))
    observaciones = db.Column(db.Text)

    id_pedido = db.Column(db.Integer, db.ForeignKey(
        'pedido.id_pedido'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey(
        'usuario.id_usuario'), nullable=False)  # Usuario que revisa

    gestion_envio = db.relationship(
        'RegestionEnvios', backref='revision', lazy=True)


class RegestionEnvios(db.Model):
    __tablename__ = 'regestionenvios'
    id_envio = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DATE)
    tracking = db.Column(db.String(100))
    estado_envio = db.Column(db.String(20))
    transportista = db.Column(db.String(100))

    id_pedido = db.Column(db.Integer, db.ForeignKey(
        'pedido.id_pedido'), nullable=False)
    id_revision = db.Column(db.Integer, db.ForeignKey(
        'revision.id_revision'), nullable=False)


app = Flask(__name__)

user = os.environ.get('MYSQL_USER')
password = os.environ.get('MYSQL_PASSWORD') or ''
host = os.environ.get('MYSQL_HOST')
db_name = os.environ.get('MYSQL_DB')

if not all([user, host, db_name]):
    raise ValueError(
        "Faltan variables (MYSQL_USER, MYSQL_HOST, MYSQL_DB) en el archivo .env")

db_uri = f"mysql+pymysql://{user}:{password}@{host}/{db_name}"

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def setup_database():
    print("Conectando a la base de datos...")
    with app.app_context():
        # db.drop_all()
        db.create_all()
        print("¡Tablas creadas exitosamente!")
        print("Sembrando datos iniciales (usuarios y clientes)...")

        gerente_user = Usuario.query.filter_by(
            email="gerente@barcco.com").first()
        if not gerente_user:
            gerente_user = Usuario(
                nombre="Gerente",
                email="gerente@barcco.com",
                rol="gerente",
                contraseña="contra123"
            )
            db.session.add(gerente_user)
            print("  -> Usuario 'gerente@barcco.com' creado.")

        cliente_user = Usuario.query.filter_by(
            email="cliente@barcco.com").first()
        if not cliente_user:
            cliente_user = Usuario(
                nombre="Cliente",
                email="cliente@barcco.com",
                rol="cliente",
                contraseña="contra123"
            )
            db.session.add(cliente_user)
            print("  -> Usuario 'cliente@barcco.com' creado.")

        cliente_juan = Cliente.query.filter_by(
            email="juan.perez@gmail.com").first()
        if not cliente_juan:
            cliente_juan = Cliente(
                nombre="Juan",
                apellido="Perez",
                email="juan.perez@gmail.com",
                telefono="11-2233-4455",
                direccion="Av. Siempre Viva 123"
            )
            db.session.add(cliente_juan)
            print("  -> Cliente 'Juan Perez' creado.")

        cliente_ana = Cliente.query.filter_by(
            email="ana.gomez@hotmail.com").first()
        if not cliente_ana:
            cliente_ana = Cliente(
                nombre="Ana",
                apellido="Gomez",
                email="ana.gomez@hotmail.com",
                telefono="11-6677-8899",
                direccion="Calle Falsa 456"
            )
            db.session.add(cliente_ana)
            print("  -> Cliente 'Ana Gomez' creado.")

        deposito_principal = Deposito.query.filter_by(
            nombre="Depósito Central").first()
        if not deposito_principal:
            deposito_principal = Deposito(
                nombre="Depósito Central",
                capacidad_contenedores=100
            )
            db.session.add(deposito_principal)
            print("  -> Depósito 'Depósito Central' creado.")
            try:
                db.session.flush()
            except Exception as e:
                db.session.rollback()
                print(f"Error al hacer flush de depósito: {e}")
                return

        contenedor_a1 = Contenedor.query.filter_by(id_contenedor=1).first()
        if not contenedor_a1:
            contenedor_a1 = Contenedor(
                capacidad=76,
                ocupacion_actual=0,
                estado='disponible',
                id_deposito=deposito_principal.id_deposito
            )
            db.session.add(contenedor_a1)
            print("  -> Contenedor 'A1' creado.")

        contenedor_a2 = Contenedor.query.filter_by(id_contenedor=2).first()
        if not contenedor_a2:
            contenedor_a2 = Contenedor(
                capacidad=78,
                ocupacion_actual=0,
                estado='mantenimiento',
                id_deposito=deposito_principal.id_deposito
            )
            db.session.add(contenedor_a2)
            print("  -> Contenedor 'A2' creado.")

        productos_a_crear = [
            {'sku': 'SKU001', 'nombre': 'Notebook Gamer',
                'precio': 1500.00, 'peso': 2.5},
            {'sku': 'SKU002', 'nombre': 'Monitor LED 24"',
                'precio': 250.00, 'peso': 3.0},
            {'sku': 'SKU003', 'nombre': 'Teclado Mecánico RGB',
                'precio': 120.00, 'peso': 1.1},
            {'sku': 'SKU004', 'nombre': 'Mouse Inalámbrico',
                'precio': 45.00, 'peso': 0.2},
            {'sku': 'SKU005', 'nombre': 'Auriculares Bluetooth',
                'precio': 80.00, 'peso': 0.3},
            {'sku': 'SKU006', 'nombre': 'Silla de Oficina Ergonómica',
                'precio': 300.00, 'peso': 15.0},
            {'sku': 'SKU007', 'nombre': 'Impresora Multifunción',
                'precio': 180.00, 'peso': 8.5},
            {'sku': 'SKU008', 'nombre': 'Disco SSD 1TB',
                'precio': 100.00, 'peso': 0.1},
            {'sku': 'SKU009', 'nombre': 'Router WiFi 6',
                'precio': 90.00, 'peso': 0.7},
            {'sku': 'SKU010', 'nombre': 'Webcam Full HD',
                'precio': 60.00, 'peso': 0.2}
        ]

        for prod_data in productos_a_crear:
            producto = Producto.query.filter_by(sku=prod_data['sku']).first()
            if not producto:
                producto = Producto(
                    sku=prod_data['sku'],
                    nombre=prod_data['nombre'],
                    precio_unitario=prod_data['precio'],
                    peso=prod_data['peso'],
                    descripcion=f"Descripción de {prod_data['nombre']}",
                    alto=10,
                    ancho=10,
                    profundidad=10
                )
                db.session.add(producto)
                print(f"  -> Producto '{prod_data['nombre']}' creado.")

        try:
            db.session.commit()
            print("Setup creado")
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar setup: {e}")


if __name__ == '__main__':
    setup_database()
