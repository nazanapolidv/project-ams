from base_datos.conexion import Conexion
from flask import Flask, request, render_template

# def main() -> None:
# 	db = Conexion("clientes.db")
# 	db.crear_tabla_cliente()
# 	db.agregar_cliente("Juan", "Perez", "12345678")
# 	db.agregar_cliente("Maria", "Gomez", "87654321")
# 	print(db.mostrar_clientes())
# 	db.cerrar_conexion()


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
     nombre = request.form['nombre']
     apellido = request.form['apellido']
     return render_template('resultado.html', nombre=nombre, apellido=apellido)
    return render_template('index.html')
 
 