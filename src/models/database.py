from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

class PortfolioImage(db.Model):
    __tablename__ = 'portfolio_images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    
    # EXIF data
    camera_make = db.Column(db.String(100), nullable=True)
    camera_model = db.Column(db.String(100), nullable=True)
    lens = db.Column(db.String(100), nullable=True)
    aperture = db.Column(db.String(20), nullable=True)
    shutter_speed = db.Column(db.String(20), nullable=True)
    iso = db.Column(db.String(20), nullable=True)
    focal_length = db.Column(db.String(20), nullable=True)
    date_taken = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    categories = db.relationship('Category', secondary='image_categories', back_populates='images')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'title': self.title,
            'description': self.description,
            'file_size': self.file_size,
            'width': self.width,
            'height': self.height,
            'camera_make': self.camera_make,
            'camera_model': self.camera_model,
            'lens': self.lens,
            'aperture': self.aperture,
            'shutter_speed': self.shutter_speed,
            'iso': self.iso,
            'focal_length': self.focal_length,
            'date_taken': self.date_taken.isoformat() if self.date_taken else None,
            'is_active': self.is_active,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'categories': [cat.to_dict() for cat in self.categories],
            'image_url': f'/assets/{self.filename}'
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    images = db.relationship('PortfolioImage', secondary='image_categories', back_populates='categories')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_default': self.is_default,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'image_count': len(self.images)
        }

# Association table for many-to-many relationship
image_categories = db.Table('image_categories',
    db.Column('image_id', db.Integer, db.ForeignKey('portfolio_images.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class FeaturedImage(db.Model):
    __tablename__ = 'featured_images'
    
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('portfolio_images.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    image = db.relationship('PortfolioImage', backref='featured_settings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'image_url': f'/assets/{self.image.filename}' if self.image else None
        }

class BackgroundImage(db.Model):
    __tablename__ = 'background_images'
    
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('portfolio_images.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    image = db.relationship('PortfolioImage', backref='background_settings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'image_url': f'/assets/{self.image.filename}' if self.image else None
        }

class ContactSubmission(db.Model):
    __tablename__ = 'contact_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }

def init_db():
    """Initialize database with tables and default data"""
    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(os.path.abspath('database/app.db'))
    os.makedirs(db_dir, exist_ok=True)
    
    # Create all tables
    db.create_all()
    
    # Create default category if none exist
    if not Category.query.first():
        default_category = Category(
            name='General',
            description='General photography',
            is_default=True,
            sort_order=0
        )
        db.session.add(default_category)
        db.session.commit()
        print("✅ Created default category")

