import os
from flask import Flask, render_template, jsonify
from models.database import db
from routes.admin import admin_bp
from routes.api import api_bp
from routes.frontend import frontend_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Use persistent storage for database
    # *** IMPORTANT: This path must match your Railway Volume Mount Path ***
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////mnt/data/app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = "src/static/assets"
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
    
    # Ensure data directory exists
    data_dir = "/mnt/data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(frontend_bp)  # Frontend routes (public website)
    app.register_blueprint(admin_bp, url_prefix='/admin')  # Admin routes
    app.register_blueprint(api_bp)  # API routes
    
    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "message": "TheMindsEyeStudio.com - Live!"})
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
        print(f"Database location: {app.config["SQLALCHEMY_DATABASE_URI"]}")
    
    return app

if __name__ == "__main__":
    app = create_app()
    # Port is set by Railway's PORT env var, so this is for local testing
    port = int(os.environ.get("PORT", 5001))
    # Debug should be False in production
    app.run(host="0.0.0.0", port=port, debug=True)
