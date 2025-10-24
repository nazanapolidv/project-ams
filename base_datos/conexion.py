import sqlite3

class Conexion:

  def __init__(self, nombre_bd):
    self.conexion = sqlite3.connect(nombre_bd)
    self.cursor = self.conexion.cursor()

  def crear_tabla_cliente(self):
    self.cursor.execute(
        "CREATE TABLE IF NOT EXISTS cliente(nombre TEXT, apellido TEXT, dni TEXT)"
    )
    self.conexion.commit()

  def agregar_cliente(self, nombre, apellido, dni):
    self.cursor.execute("INSERT INTO cliente VALUES(?,?,?)",
                        (nombre, apellido, dni))
    self.conexion.commit()

  def editar_cliente(self, nombre, apellido, dni):
    self.cursor.execute(
        "UPDATE cliente SET nombre=?, apellido=?, dni=? WHERE dni=?",
        (nombre, apellido, dni, dni))
    self.conexion.commit()

  def mostrar_clientes(self):
    self.cursor.execute("SELECT * FROM cliente")
    clientes = self.cursor.fetchall()
    return clientes

  def eliminar_cliente(self, dni):
    self.cursor.execute("DELETE FROM cliente WHERE dni=?", (dni, ))
    self.conexion.commit()

  def crear_tabla_deposito(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS deposito (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cantidad_contenedores INTEGER NOT NULL
            )
            """
        )
        self.conexion.commit()

  def agregar_deposito(self, nombre, cantidad_contenedores):
      self.cursor.execute(
          "INSERT INTO deposito (nombre, cantidad_contenedores) VALUES (?, ?)",
          (nombre, cantidad_contenedores)
      )
      self.conexion.commit()
  
  def cerrar_conexion(self):
    self.cursor.close()
    self.conexion.close()
