import os

from flask import Flask, g, session
from dotenv import load_dotenv

from models import db, Usuario

load_dotenv()


def create_app(config_override: dict | None = None):
    app = Flask(__name__)

    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    host = os.getenv("MYSQL_HOST")
    db_name = os.getenv("MYSQL_DB")

    if all([user, host, db_name]):
        uri = f"mysql+pymysql://{user}:{password}@{host}/{db_name}"
    else:
        uri = 'sqlite:///app.db'

    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv(
        'SECRET_KEY', 'clave-defecto')

    if config_override:
        app.config.update(config_override)

    db.init_app(app)

    @app.before_request
    def load_logged_in_user():
        user_id = session.get('user_id')
        g.user = db.session.get(Usuario, user_id) if user_id else None

    from routes.auth import auth_bp
    from routes.cliente import cliente_bp
    from routes.gerente import gerente_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(gerente_bp)

    return app


app = create_app()


if __name__ == '__main__':
    app.run()
