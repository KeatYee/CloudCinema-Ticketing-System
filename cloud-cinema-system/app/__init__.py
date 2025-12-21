from flask import Flask
from .config import Config
import pymysql

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Database connection helper
    def get_db_connection():
        return pymysql.connect(
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME'],
            cursorclass=pymysql.cursors.DictCursor  # Returns results as dictionaries
        )

    # Attach it to the app object for easy access in routes
    app.get_db_connection = get_db_connection

    from .routes.main import main_bp
    app.register_blueprint(main_bp)

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from .routes.booking import booking_bp
    app.register_blueprint(booking_bp)
    
    from .routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    return app