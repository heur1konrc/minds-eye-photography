# UPDATED DATABASE MODELS
# Replace your entire src/models/database.py file with this content

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Many-to-many relationship table for images and categories
image_categories = db.Table('image_categories',
    db.Column('image_id', db.Integer, db.ForeignKey('portfolio_images.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class PortfolioImage(db.Model):
    __tablename__ = 'portfolio_images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Many-to-many relationship with categories
    categories = db.relationship('Category', secondary=image_categories, back_populates='images')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'title': self.title,
            'description': self.description,
            'is_active': self.is_active,
            'image_url': f'/static/assets/{self.filename}',
            'categories': [cat.to_dict() for cat in self.categories],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Many-to-many relationship with images
    images = db.relationship('PortfolioImage', secondary=image_categories, back_populates='categories')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'image_count': len(self.images),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BackgroundImage(db.Model):
    __tablename__ = 'background_images'
    
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('portfolio_images.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to portfolio image
    image = db.relationship('PortfolioImage', backref='background_settings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'image_url': f'/static/assets/{self.image.filename}' if self.image else None,
            'image_title': self.image.title if self.image else None
        }
