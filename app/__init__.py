from flask import Flask
from flask_login import LoginManager
from .models import db, User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)

    # ===== IMPORTAR BLUEPRINTS =====
    from .auth import auth
    from .routes import main
    from .admin import admin   # <<< IMPORTANTE

    # ===== REGISTRAR BLUEPRINTS =====
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(admin)  # <<< IMPORTANTE

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app