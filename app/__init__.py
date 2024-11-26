import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv



import string
import random



# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()



def create_app():
    app = Flask(__name__)
    #app.config.from_object('config.Config')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    # Set the SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLITE_DB_URI')#, 'sqlite:///site.db')  # Use environment variable or default to SQLite

    # Initialize extensions
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'login'

    Bootstrap5(app)

    # Register the `user_loader` function
    from .models import User

    oauth.init_app(app)

    #Initialize DB
    with app.app_context():
        db.create_all()  # Ensure database tables are created

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    # Import routes
    from app.routes import register_routes
    register_routes(app)

    return app
