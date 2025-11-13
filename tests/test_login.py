import unittest

from app import create_app
from models import db, Usuario


class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite://',
            'SQLALCHEMY_ENGINE_OPTIONS': {'connect_args': {'check_same_thread': False}},
            'SECRET_KEY': 'clave-test',
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        self.usuario = Usuario(
            nombre='Gerente Test',
            email='gerente@test.com',
            contraseña='contra123',
            rol='gerente',
        )
        db.session.add(self.usuario)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_aprobado(self):
        response = self.client.post('/', data={
            'email': self.usuario.email,
            'contraseña': self.usuario.contraseña,
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Pantalla Gerente'.encode('utf-8'), response.data)

    def test_login_fallido(self):
        response = self.client.post('/', data={
            'email': 'cualqcosa@test.com',
            'contraseña': 'hola',
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Email o contraseña incorrectos'.encode(
            'utf-8'), response.data)
