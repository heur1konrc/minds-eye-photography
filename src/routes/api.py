from flask import Blueprint, jsonify, request
from models.database import db, PortfolioImage, Category, FeaturedImage, BackgroundImage, ContactSubmission

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/portfolio')
def get_portfolio():
    """Get all active portfolio images"""
    try:
        images = PortfolioImage.query.filter_by(is_active=True).order_by(PortfolioImage.sort_order).all()
        return jsonify({
            'images': [image.to_dict() for image in images]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/categories')
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.order_by(Category.sort_order).all()
        return jsonify([category.to_dict() for category in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/featured')
def get_featured():
    """Get current featured image"""
    try:
        featured = FeaturedImage.query.filter_by(is_active=True).first()
        if featured:
            return jsonify(featured.to_dict())
        else:
            return jsonify({'message': 'No featured image set'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/background')
def get_background():
    """Get current background image"""
    try:
        background = BackgroundImage.query.filter_by(is_active=True).first()
        if background:
            return jsonify(background.to_dict())
        else:
            return jsonify({'message': 'No background image set'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/contact', methods=['POST'])
def submit_contact():
    """Submit contact form"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('name', 'email', 'message')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        submission = ContactSubmission(
            name=data['name'],
            email=data['email'],
            message=data['message']
        )
        
        db.session.add(submission)
        db.session.commit()
        
        return jsonify({'message': 'Contact form submitted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

