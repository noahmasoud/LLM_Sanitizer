from flask import Flask
from extensions import db, mail
from routes.home import home_bp
from routes.hub import hub_bp
from routes.login import login_bp
from routes.register import register_bp
from routes.about import about_bp
from routes.apps import apps_bp
from routes.notes import notes_bp
from routes.admin import admin_bp, init_admin_db
from routes.files import files_bp
from routes.captcha import captcha_bp
from routes.retirement import retirement_bp
from routes.contact import contact_bp
from routes.news import news_bp
from models.user import User
from models.note import Note
from models.admin import Admin
from models.file import File
from sqlalchemy import inspect
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
import os.path


load_dotenv()
# Noah 2/28/2025
########################################################
# database setup
# email setup
# flask migrate setup
# flask secret key
# upload folder
# register blueprints
# setup database
########################################################


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, "boko_hacks.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['MAIL_SERVER'] = os.environ.get(
        'MAIL_SERVER', 'sandbox.smtp.mailtrap.io')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 2525))
    app.config['MAIL_USERNAME'] = os.environ.get(
        'MAIL_USERNAME', '5ba07344d285d1')
    app.config['MAIL_PASSWORD'] = os.environ.get(
        'MAIL_PASSWORD', '')  # No default password
    app.config['MAIL_USE_TLS'] = os.environ.get(
        'MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USE_SSL'] = os.environ.get(
        'MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get(
        'MAIL_DEFAULT_SENDER', 'noreply@yourapplication.com')

    db.init_app(app)
    mail.init_app(app)

    migrate = Migrate(app, db)

    app.secret_key = "supersecretkey"

    UPLOAD_FOLDER = 'uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Register Blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(hub_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(apps_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(captcha_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(retirement_bp)
    app.register_blueprint(contact_bp)

    return app


def setup_database():
    """Setup database and print debug info"""
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        if not existing_tables:
            print("No existing tables found. Creating new tables...")
            db.create_all()

            init_admin_db()
        else:
            print("Existing tables found:", existing_tables)

            db.create_all()
            print("Updated schema with any new tables")

        for table in ['users', 'notes', 'admin_credentials', 'files']:
            if table in inspector.get_table_names():
                print(f"\n{table.capitalize()} table columns:")
                for column in inspector.get_columns(table):
                    print(f"- {column['name']}: {column['type']}")
            else:
                print(f"\n{table} table does not exist!")


if __name__ == "__main__":
    app = create_app()
    setup_database()
    app.run(debug=True)
