from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Association table for many-to-many relationship between images and categories
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
    categories = db.relationship('Category', secondary=image_categories, lazy='subquery',
                               backref=db.backref('images', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'title': self.title,
            'description': self.description,
            'is_active': self.is_active,
            'image_url': f'/static/assets/{self.filename}',
            'categories': [cat.to_dict() for cat in self.categories]
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active
        }

class FeaturedImage(db.Model):
    __tablename__ = 'featured_images'
    
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('portfolio_images.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to portfolio image
    image = db.relationship('PortfolioImage', backref='featured_entries')
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'is_active': self.is_active,
            'image': self.image.to_dict() if self.image else None
        }

class BackgroundImage(db.Model):
    __tablename__ = 'background_images'
    
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('portfolio_images.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to portfolio image
    image = db.relationship('PortfolioImage', backref='background_entries')
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'is_active': self.is_active,
            'image': self.image.to_dict() if self.image else None
        }

class ContactSubmission(db.Model):
    __tablename__ = 'contact_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'created_at': self.created_at.isoformat()
        }
