from flask import Flask
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Import Blueprints
    from .routes.main import main_bp
    # from .routes.auth import auth_bp      # Uncomment when you fill these files
    # from .routes.booking import booking_bp
    # from .routes.admin import admin_bp
    # from .routes.health import health_bp

    # Register Blueprints
    app.register_blueprint(main_bp)
    # app.register_blueprint(auth_bp)
    # app.register_blueprint(booking_bp)
    # app.register_blueprint(admin_bp)
    # app.register_blueprint(health_bp)

    return app