from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Association table for many-to-many relationship between images and categories
image_categories = db.Table('image_categories',
    db.Column('image_id', db.Integer, db.ForeignKey('portfolio_image.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Category {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PortfolioImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    # EXIF Data
    camera_make = db.Column(db.String(100))
    camera_model = db.Column(db.String(100))
    lens = db.Column(db.String(200))
    aperture = db.Column(db.String(20))
    shutter_speed = db.Column(db.String(20))
    iso = db.Column(db.String(20))
    focal_length = db.Column(db.String(20))
    date_taken = db.Column(db.DateTime)
    
    # File metadata
    file_size = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    
    # Management fields
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    categories = db.relationship('Category', secondary=image_categories, backref=db.backref('images', lazy='dynamic'))

    def __repr__(self):
        return f'<PortfolioImage {self.filename}>'

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'title': self.title,
            'description': self.description,
            'camera_make': self.camera_make,
            'camera_model': self.camera_model,
            'lens': self.lens,
            'aperture': self.aperture,
            'shutter_speed': self.shutter_speed,
            'iso': self.iso,
            'focal_length': self.focal_length,
            'date_taken': self.date_taken.isoformat() if self.date_taken else None,
            'file_size': self.file_size,
            'width': self.width,
            'height': self.height,
            'is_active': self.is_active,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'categories': [cat.to_dict() for cat in self.categories]
        }

class FeaturedImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_image_id = db.Column(db.Integer, db.ForeignKey('portfolio_image.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    story = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    portfolio_image = db.relationship('PortfolioImage', backref=db.backref('featured_entries', lazy='dynamic'))

    def __repr__(self):
        return f'<FeaturedImage {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'portfolio_image_id': self.portfolio_image_id,
            'title': self.title,
            'story': self.story,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'portfolio_image': self.portfolio_image.to_dict() if self.portfolio_image else None
        }

class BackgroundImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BackgroundImage {self.filename}>'

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'title': self.title,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ContactSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContactSubmission {self.name} - {self.subject}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'subject': self.subject,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

