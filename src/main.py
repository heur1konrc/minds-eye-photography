import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.admin import admin_bp
from src.routes.api import api_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'minds-eye-photography-secret-key-2025'

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db.init_app(app)

# Create database tables and initial data
with app.app_context():
    db.create_all()
    
    # Create default categories if they don't exist
    from src.models.user import Category
    default_categories = [
        {'name': 'Nature', 'description': 'Natural landscapes and wildlife photography'},
        {'name': 'Portrait', 'description': 'Portrait and people photography'},
        {'name': 'Architecture', 'description': 'Buildings and architectural photography'},
        {'name': 'Street', 'description': 'Street photography and urban scenes'},
        {'name': 'Miscellaneous', 'description': 'Other photography work'}
    ]
    
    for i, cat_data in enumerate(default_categories):
        existing = Category.query.filter_by(name=cat_data['name']).first()
        if not existing:
            category = Category(
                name=cat_data['name'],
                description=cat_data['description'],
                sort_order=i
            )
            db.session.add(category)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

