from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.employees import employees_bp
    from app.routes.doctors import doctors_bp
    from app.routes.patients import patients_bp
    from app.routes.appointments import appointments_bp

    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(employees_bp, url_prefix='/')
    app.register_blueprint(doctors_bp, url_prefix='/')
    app.register_blueprint(patients_bp, url_prefix='/')
    app.register_blueprint(appointments_bp, url_prefix='/')

    return app
