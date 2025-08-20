from flask import Blueprint, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
from PIL import Image
from PIL.ExifTags import TAGS
import os
import uuid
from datetime import datetime
from src.models.user import db, PortfolioImage, Category, FeaturedImage, BackgroundImage, ContactSubmission

admin_bp = Blueprint('admin', __name__)

UPLOAD_FOLDER = 'src/static/assets'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_exif_data(image_path):
    """Extract EXIF data from image"""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if exif_data is None:
            return {}
            
        exif = {}
        for key, value in exif_data.items():
            if key in TAGS:
                exif[TAGS[key]] = value
                
        return {
            'camera_make': exif.get('Make', ''),
            'camera_model': exif.get('Model', ''),
            'lens': exif.get('LensModel', ''),
            'aperture': str(exif.get('FNumber', '')),
            'shutter_speed': str(exif.get('ExposureTime', '')),
            'iso': str(exif.get('ISOSpeedRatings', '')),
            'focal_length': str(exif.get('FocalLength', '')),
            'date_taken': exif.get('DateTime', '')
        }
    except Exception as e:
        print(f"Error extracting EXIF: {e}")
        return {}

@admin_bp.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mind's Eye Photography - Admin</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { color: #ff6b35; font-size: 2.5em; margin-bottom: 10px; }
            .admin-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .admin-card { background: #2a2a2a; padding: 30px; border-radius: 10px; text-align: center; }
            .admin-card h3 { color: #ff6b35; margin-bottom: 15px; }
            .admin-card p { margin-bottom: 20px; color: #ccc; }
            .btn { display: inline-block; padding: 12px 24px; background: #ff6b35; color: white; text-decoration: none; border-radius: 5px; transition: background 0.3s; }
            .btn:hover { background: #e55a2b; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Mind's Eye Photography</h1>
                <p>Admin Dashboard</p>
            </div>
            <div class="admin-grid">
                <div class="admin-card">
                    <h3>Portfolio Management</h3>
                    <p>Upload, organize, and manage your photography portfolio</p>
                    <a href="/admin/portfolio" class="btn">Manage Portfolio</a>
                </div>
                <div class="admin-card">
                    <h3>Featured Image</h3>
                    <p>Set and manage the featured image on your homepage</p>
                    <a href="/admin/featured" class="btn">Manage Featured</a>
                </div>
                <div class="admin-card">
                    <h3>Categories</h3>
                    <p>Create and organize image categories</p>
                    <a href="/admin/categories" class="btn">Manage Categories</a>
                </div>
                <div class="admin-card">
                    <h3>Background Images</h3>
                    <p>Manage website background images</p>
                    <a href="/admin/backgrounds" class="btn">Manage Backgrounds</a>
                </div>
                <div class="admin-card">
                    <h3>Contact Messages</h3>
                    <p>View and manage contact form submissions</p>
                    <a href="/admin/contacts" class="btn">View Messages</a>
                </div>
                <div class="admin-card">
                    <h3>Back to Site</h3>
                    <p>Return to the main website</p>
                    <a href="/" class="btn">View Site</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

@admin_bp.route('/admin/portfolio')
def portfolio_management():
    """Portfolio management interface"""
    images = PortfolioImage.query.filter_by(is_active=True).order_by(PortfolioImage.sort_order).all()
    categories = Category.query.order_by(Category.sort_order).all()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Portfolio Management - Mind's Eye Photography</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #ff6b35; font-size: 2em; margin-bottom: 10px; }
            .upload-section { background: #2a2a2a; padding: 20px; border-radius: 10px; margin-bottom: 30px; }
            .upload-form { display: flex; gap: 15px; align-items: end; flex-wrap: wrap; }
            .form-group { display: flex; flex-direction: column; }
            .form-group label { margin-bottom: 5px; color: #ccc; }
            .form-group input, .form-group select { padding: 8px; border: 1px solid #555; background: #333; color: #fff; border-radius: 4px; }
            .btn { padding: 10px 20px; background: #ff6b35; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .btn:hover { background: #e55a2b; }
            .images-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
            .image-card { background: #2a2a2a; border-radius: 10px; overflow: hidden; }
            .image-card img { width: 100%; height: 200px; object-fit: cover; }
            .image-info { padding: 15px; }
            .image-info h4 { color: #ff6b35; margin-bottom: 5px; }
            .image-info p { color: #ccc; font-size: 0.9em; margin-bottom: 5px; }
            .exif-badges { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; }
            .exif-badge { background: #ff6b35; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; }
            .back-btn { display: inline-block; margin-bottom: 20px; padding: 8px 16px; background: #555; color: white; text-decoration: none; border-radius: 4px; }
            .back-btn:hover { background: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <div class="header">
                <h1>Portfolio Management</h1>
                <p>Upload and manage your photography portfolio</p>
            </div>
            
            <div class="upload-section">
                <h3 style="color: #ff6b35; margin-bottom: 15px;">Upload New Image</h3>
                <form class="upload-form" enctype="multipart/form-data" onsubmit="uploadImage(event)">
                    <div class="form-group">
                        <label>Image File</label>
                        <input type="file" name="image" accept="image/*" required>
                    </div>
                    <div class="form-group">
                        <label>Title</label>
                        <input type="text" name="title" placeholder="Image title">
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <input type="text" name="description" placeholder="Image description">
                    </div>
                    <div class="form-group">
                        <label>Category</label>
                        <select name="category_id">
                            <option value="">Select category</option>
                            {% for category in categories %}
                            <option value="{{ category.id }}">{{ category.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <button type="submit" class="btn">Upload Image</button>
                    </div>
                </form>
            </div>
            
            <div class="images-grid">
                {% for image in images %}
                <div class="image-card">
                    <img src="/assets/{{ image.filename }}" alt="{{ image.title or image.original_filename }}">
                    <div class="image-info">
                        <h4>{{ image.title or image.original_filename }}</h4>
                        {% if image.description %}
                        <p>{{ image.description }}</p>
                        {% endif %}
                        <div class="exif-badges">
                            <span class="exif-badge">📷 {{ image.camera_make or 'Not Available' }} {{ image.camera_model or '' }}</span>
                            <span class="exif-badge">🔍 {{ image.lens or 'Not Available' }}</span>
                            <span class="exif-badge">⚙️ {{ image.aperture or 'N/A' }}, {{ image.shutter_speed or 'N/A' }}, ISO {{ image.iso or 'N/A' }}</span>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <script>
        async function uploadImage(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            
            try {
                const response = await fetch('/api/admin/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    alert('Image uploaded successfully!');
                    location.reload();
                } else {
                    const error = await response.json();
                    alert('Upload failed: ' + error.message);
                }
            } catch (error) {
                alert('Upload failed: ' + error.message);
            }
        }
        </script>
    </body>
    </html>
    ''', images=images, categories=categories)

@admin_bp.route('/api/admin/upload', methods=['POST'])
def upload_image():
    """Handle image upload"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Extract EXIF data
        exif_data = extract_exif_data(file_path)
        
        # Get image dimensions
        with Image.open(file_path) as img:
            width, height = img.size
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create database entry
        portfolio_image = PortfolioImage(
            filename=unique_filename,
            original_filename=secure_filename(file.filename),
            title=request.form.get('title', ''),
            description=request.form.get('description', ''),
            camera_make=exif_data.get('camera_make', ''),
            camera_model=exif_data.get('camera_model', ''),
            lens=exif_data.get('lens', ''),
            aperture=exif_data.get('aperture', ''),
            shutter_speed=exif_data.get('shutter_speed', ''),
            iso=exif_data.get('iso', ''),
            focal_length=exif_data.get('focal_length', ''),
            file_size=file_size,
            width=width,
            height=height
        )
        
        # Parse date_taken if available
        if exif_data.get('date_taken'):
            try:
                portfolio_image.date_taken = datetime.strptime(exif_data['date_taken'], '%Y:%m:%d %H:%M:%S')
            except:
                pass
        
        db.session.add(portfolio_image)
        
        # Add to category if specified
        category_id = request.form.get('category_id')
        if category_id:
            category = Category.query.get(category_id)
            if category:
                portfolio_image.categories.append(category)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Image uploaded successfully',
            'image': portfolio_image.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/categories')
def category_management():
    """Category management interface"""
    categories = Category.query.order_by(Category.sort_order).all()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Category Management - Mind's Eye Photography</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #ff6b35; font-size: 2em; margin-bottom: 10px; }
            .form-section { background: #2a2a2a; padding: 20px; border-radius: 10px; margin-bottom: 30px; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; color: #ccc; }
            .form-group input, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #555; background: #333; color: #fff; border-radius: 4px; }
            .btn { padding: 10px 20px; background: #ff6b35; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .btn:hover { background: #e55a2b; }
            .categories-list { background: #2a2a2a; padding: 20px; border-radius: 10px; }
            .category-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #444; }
            .category-item:last-child { border-bottom: none; }
            .category-info h4 { color: #ff6b35; }
            .category-info p { color: #ccc; font-size: 0.9em; }
            .back-btn { display: inline-block; margin-bottom: 20px; padding: 8px 16px; background: #555; color: white; text-decoration: none; border-radius: 4px; }
            .back-btn:hover { background: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <div class="header">
                <h1>Category Management</h1>
                <p>Create and organize image categories</p>
            </div>
            
            <div class="form-section">
                <h3 style="color: #ff6b35; margin-bottom: 15px;">Add New Category</h3>
                <form onsubmit="addCategory(event)">
                    <div class="form-group">
                        <label>Category Name</label>
                        <input type="text" name="name" required>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea name="description" rows="3"></textarea>
                    </div>
                    <button type="submit" class="btn">Add Category</button>
                </form>
            </div>
            
            <div class="categories-list">
                <h3 style="color: #ff6b35; margin-bottom: 15px;">Existing Categories</h3>
                {% for category in categories %}
                <div class="category-item">
                    <div class="category-info">
                        <h4>{{ category.name }}</h4>
                        {% if category.description %}
                        <p>{{ category.description }}</p>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <script>
        async function addCategory(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            
            try {
                const response = await fetch('/api/admin/categories', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    alert('Category added successfully!');
                    location.reload();
                } else {
                    const error = await response.json();
                    alert('Failed to add category: ' + error.message);
                }
            } catch (error) {
                alert('Failed to add category: ' + error.message);
            }
        }
        </script>
    </body>
    </html>
    ''', categories=categories)

@admin_bp.route('/api/admin/categories', methods=['POST'])
def add_category():
    """Add new category"""
    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            return jsonify({'error': 'Category name is required'}), 400
        
        # Check if category already exists
        existing = Category.query.filter_by(name=name).first()
        if existing:
            return jsonify({'error': 'Category already exists'}), 400
        
        category = Category(
            name=name,
            description=description,
            sort_order=Category.query.count()
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category added successfully',
            'category': category.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

