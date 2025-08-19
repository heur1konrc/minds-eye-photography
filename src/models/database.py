# Complete Database Models for Portfolio Management
# Replace your src/models/database.py with this content

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

# Association table for many-to-many relationship between images and categories
image_categories = db.Table('image_categories',
    db.Column('image_id', db.Integer, db.ForeignKey('portfolio_image.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class Category(db.Model):
    """Category model for organizing portfolio images"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to images
    images = db.relationship('PortfolioImage', secondary=image_categories, back_populates='categories')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'image_count': len(self.images),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PortfolioImage(db.Model):
    """Portfolio image model with comprehensive metadata"""
    id = db.Column(db.Integer, primary_key=True)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    
    # Image metadata
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    alt_text = db.Column(db.String(255))
    
    # Camera/EXIF data
    camera_make = db.Column(db.String(100))
    camera_model = db.Column(db.String(100))
    lens = db.Column(db.String(100))
    aperture = db.Column(db.String(20))
    shutter_speed = db.Column(db.String(20))
    iso = db.Column(db.String(20))
    focal_length = db.Column(db.String(20))
    date_taken = db.Column(db.DateTime)
    
    # Location data
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Organization
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    categories = db.relationship('Category', secondary=image_categories, back_populates='images')
    
    def __repr__(self):
        return f'<PortfolioImage {self.filename}>'
    
    @property
    def image_url(self):
        """Generate the URL for this image"""
        return f'/static/assets/{self.filename}'
    
    @property
    def aspect_ratio(self):
        """Calculate aspect ratio"""
        if self.width and self.height:
            return self.width / self.height
        return None
    
    @property
    def file_size_mb(self):
        """File size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'title': self.title,
            'description': self.description,
            'alt_text': self.alt_text,
            'image_url': self.image_url,
            'width': self.width,
            'height': self.height,
            'aspect_ratio': self.aspect_ratio,
            'file_size': self.file_size,
            'file_size_mb': self.file_size_mb,
            'camera_make': self.camera_make,
            'camera_model': self.camera_model,
            'lens': self.lens,
            'aperture': self.aperture,
            'shutter_speed': self.shutter_speed,
            'iso': self.iso,
            'focal_length': self.focal_length,
            'date_taken': self.date_taken.isoformat() if self.date_taken else None,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'categories': [cat.to_dict() for cat in self.categories],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SiteSettings(db.Model):
    """Site-wide settings and configuration"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False, unique=True)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SiteSettings {self.key}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BackupLog(db.Model):
    """Log of backup operations"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    backup_type = db.Column(db.String(50), nullable=False)  # 'local', 'github'
    file_size = db.Column(db.Integer)
    status = db.Column(db.String(20), default='completed')  # 'completed', 'failed'
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BackupLog {self.filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'backup_type': self.backup_type,
            'file_size': self.file_size,
            'file_size_mb': round(self.file_size / (1024 * 1024), 2) if self.file_size else None,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Helper functions for database operations

def init_database(app):
    """Initialize database with app context"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default categories if they don't exist
        create_default_categories()
        
        # Create default site settings
        create_default_settings()

def create_default_categories():
    """Create default portfolio categories"""
    default_categories = [
        {'name': 'Portraits', 'slug': 'portraits', 'description': 'Portrait photography', 'sort_order': 1},
        {'name': 'Landscapes', 'slug': 'landscapes', 'description': 'Landscape photography', 'sort_order': 2},
        {'name': 'Events', 'slug': 'events', 'description': 'Event photography', 'sort_order': 3},
        {'name': 'Commercial', 'slug': 'commercial', 'description': 'Commercial photography', 'sort_order': 4},
        {'name': 'Street', 'slug': 'street', 'description': 'Street photography', 'sort_order': 5},
        {'name': 'Nature', 'slug': 'nature', 'description': 'Nature photography', 'sort_order': 6}
    ]
    
    for cat_data in default_categories:
        existing = Category.query.filter_by(slug=cat_data['slug']).first()
        if not existing:
            category = Category(**cat_data)
            db.session.add(category)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating default categories: {e}")

def create_default_settings():
    """Create default site settings"""
    default_settings = [
        {'key': 'site_title', 'value': "Mind's Eye Photography", 'description': 'Site title'},
        {'key': 'site_description', 'value': 'Professional Photography Portfolio', 'description': 'Site description'},
        {'key': 'contact_email', 'value': '', 'description': 'Contact email address'},
        {'key': 'featured_image_id', 'value': '', 'description': 'ID of featured homepage image'},
        {'key': 'background_image_id', 'value': '', 'description': 'ID of background image'},
        {'key': 'images_per_page', 'value': '12', 'description': 'Number of images per page'},
        {'key': 'default_category', 'value': 'all', 'description': 'Default category filter'},
        {'key': 'enable_exif_display', 'value': 'true', 'description': 'Show EXIF data on images'},
        {'key': 'enable_lightbox', 'value': 'true', 'description': 'Enable lightbox for images'},
        {'key': 'backup_retention_days', 'value': '30', 'description': 'Days to keep backup files'}
    ]
    
    for setting_data in default_settings:
        existing = SiteSettings.query.filter_by(key=setting_data['key']).first()
        if not existing:
            setting = SiteSettings(**setting_data)
            db.session.add(setting)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating default settings: {e}")

def get_setting(key, default=None):
    """Get a site setting value"""
    setting = SiteSettings.query.filter_by(key=key).first()
    return setting.value if setting else default

def set_setting(key, value, description=None):
    """Set a site setting value"""
    setting = SiteSettings.query.filter_by(key=key).first()
    if setting:
        setting.value = value
        setting.updated_at = datetime.utcnow()
        if description:
            setting.description = description
    else:
        setting = SiteSettings(key=key, value=value, description=description)
        db.session.add(setting)
    
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error setting {key}: {e}")
        return False

# Utility functions for file operations

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """Generate a unique filename while preserving extension"""
    if not original_filename:
        return f"{uuid.uuid4()}.jpg"
    
    file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    return f"{uuid.uuid4()}.{file_extension}"

