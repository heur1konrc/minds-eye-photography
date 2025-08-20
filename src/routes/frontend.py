"""
Frontend routes for TheMindsEyeStudio.com photography portfolio website
"""

from flask import Blueprint, render_template, jsonify, request
from models.database import db, PortfolioImage, Category
from sqlalchemy import desc
import os

# Create frontend blueprint
frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def home():
    """Home page with hero background and branding"""
    # Get hero background image (admin-selectable)
    hero_image = get_hero_background()
    
    # Get featured portfolio images for preview
    featured_images = PortfolioImage.query.filter_by(is_active=True).limit(6).all()
    
    return render_template('frontend/home.html', 
                         hero_image=hero_image,
                         featured_images=featured_images)

@frontend_bp.route('/portfolio')
def portfolio():
    """Portfolio/Gallery page with category filtering"""
    # Get all active categories
    categories = Category.query.filter_by(is_active=True).all()
    
    # Get category filter from query params
    category_filter = request.args.get('category')
    
    # Filter images by category if specified
    if category_filter:
        images = PortfolioImage.query.join(PortfolioImage.categories).filter(
            Category.name == category_filter,
            PortfolioImage.is_active == True
        ).all()
    else:
        images = PortfolioImage.query.filter_by(is_active=True).all()
    
    return render_template('frontend/portfolio.html',
                         images=images,
                         categories=categories,
                         current_category=category_filter)

@frontend_bp.route('/featured')
def weekly_featured():
    """Weekly Featured Image page"""
    # Get most recent portfolio image as featured
    featured_image = PortfolioImage.query.filter_by(is_active=True).order_by(desc(PortfolioImage.created_at)).first()
    
    return render_template('frontend/featured.html', 
                         featured_image=featured_image)

@frontend_bp.route('/featured/<slug>')
def featured_share(slug):
    """Shareable URL for specific featured image"""
    # Get featured image by slug (using title as slug for now)
    featured = PortfolioImage.query.filter(
        PortfolioImage.title.contains(slug.replace('-', ' ')),
        PortfolioImage.is_active == True
    ).first()
    
    if not featured:
        return render_template('frontend/featured_not_found.html'), 404
    
    # This page is optimized for social media sharing
    return render_template('frontend/featured_share.html', 
                         featured=featured,
                         is_share_page=True)

@frontend_bp.route('/about')
def about():
    """About page with photography vision and bio"""
    # Get some portfolio images to showcase
    showcase_images = PortfolioImage.query.filter_by(is_active=True).limit(4).all()
    
    return render_template('frontend/about.html',
                         showcase_images=showcase_images)

@frontend_bp.route('/contact')
def contact():
    """Contact page with form and business information"""
    return render_template('frontend/contact.html')

@frontend_bp.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handle contact form submission"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'message']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field.title()} is required'}), 400
    
    # TODO: Implement email sending with SMTP
    # For now, just return success
    return jsonify({'success': True, 'message': 'Thank you for your message! We\'ll get back to you soon.'})

@frontend_bp.route('/api/portfolio')
def api_portfolio():
    """API endpoint for portfolio images"""
    category = request.args.get('category')
    
    if category:
        images = PortfolioImage.query.join(PortfolioImage.categories).filter(
            Category.name == category,
            PortfolioImage.is_active == True
        ).all()
    else:
        images = PortfolioImage.query.filter_by(is_active=True).all()
    
    return jsonify([{
        'id': img.id,
        'title': img.title,
        'description': img.description,
        'filename': img.filename,
        'url': f'/static/assets/{img.filename}',
        'categories': [cat.name for cat in img.categories],
        'created_at': img.created_at.isoformat() if img.created_at else None
    } for img in images])

@frontend_bp.route('/api/categories')
def api_categories():
    """API endpoint for active categories"""
    categories = Category.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': cat.id,
        'name': cat.name,
        'description': cat.description
    } for cat in categories])

def get_hero_background():
    """Get the current hero background image"""
    # Use the most recent portfolio image as hero background
    hero = PortfolioImage.query.filter_by(is_active=True).order_by(desc(PortfolioImage.created_at)).first()
    return hero.filename if hero else None

