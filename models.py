from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contraseña = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'Usuario {self.nombre} - {self.rol}>'
    

    
