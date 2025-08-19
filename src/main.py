# src/main.py
# FINAL, CORRECTED VERSION

import os
import click
from flask import Flask, render_template, jsonify
from flask.cli import with_appcontext

# --- Database and Blueprint Imports ---
# Assuming your models and routes are structured correctly
from src.models.database import db
from src.routes.admin import admin_bp
from src.routes.api import api_bp

# --- Database Initialization Command ---
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clears existing data and creates new tables."""
    db.create_all()
    click.echo('Initialized the database.')

# --- Application Factory ---
def create_app():
    """
    Creates and configures the Flask application.
    This is the standard pattern for robust Flask apps.
    """
    # Create the Flask app instance
    # The static_url_path='' makes /static/assets/ accessible via /assets/
    app = Flask(__name__, instance_relative_config=True)

    # --- Configuration ---
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY='dev', # Default secret key, override in production
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # Place the database in the instance folder, which is not tracked by git
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'app.db')}",
    )

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Already exists

    # --- Initialize Extensions ---
    db.init_app(app)

    # --- Register Blueprints (Routes) ---
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # --- Register CLI Commands ---
    app.cli.add_command(init_db_command)

    # --- Main Application Routes ---
    @app.route('/')
    def index():
        # This should eventually render your main portfolio page
        return render_template('index.html')

    @app.route('/health')
    def health():
        """A simple health check endpoint for monitoring."""
        return jsonify({'status': 'healthy'})

    return app

# This block is for local development and will not be used by Gunicorn on Railway
if __name__ == '__main__':
    app = create_app()
    # The port is set by Railway's PORT env var, so this is for local testing
    port = int(os.environ.get("PORT", 5001))
    # Debug should be False in production
    app.run(host='0.0.0.0', port=port, debug=True)
