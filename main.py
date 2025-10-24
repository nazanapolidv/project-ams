from flask import Flask, request, render_template, redirect, url_for
from base_datos.conexion import Conexion

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/deposito-principal', methods=['POST'])
def manejar_deposito():
    try:
        nombre_deposito = request.form['nombre']
        cantidad = request.form['contenedores']

        print("---------------------------------")
        print(
            f"Datos recibidos del form: Nombre={nombre_deposito}, Cantidad={cantidad}")
        print("---------------------------------")

        db = Conexion("bd.db")
        db.agregar_deposito(nombre_deposito, cantidad)
        db.cerrar_conexion()
    except Exception as e:
        print(f"Error al agregar depósito: {e}")

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
