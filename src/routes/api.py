from flask import Blueprint, jsonify, request
from src.models.user import db, PortfolioImage, Category, FeaturedImage, BackgroundImage, ContactSubmission

api_bp = Blueprint('api', __name__)

@api_bp.route('/portfolio')
def get_portfolio():
    """Get all portfolio images"""
    try:
        category_filter = request.args.get('category')
        
        query = PortfolioImage.query.filter_by(is_active=True)
        
        if category_filter and category_filter != 'all':
            category = Category.query.filter_by(name=category_filter).first()
            if category:
                query = query.filter(PortfolioImage.categories.contains(category))
        
        images = query.order_by(PortfolioImage.sort_order, PortfolioImage.created_at.desc()).all()
        
        return jsonify({
            'images': [image.to_dict() for image in images]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/categories')
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.order_by(Category.sort_order).all()
        
        return jsonify({
            'categories': [category.to_dict() for category in categories]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/featured')
def get_featured():
    """Get current featured image"""
    try:
        featured = FeaturedImage.query.filter_by(is_active=True).first()
        
        if not featured:
            return jsonify({'featured': None})
        
        return jsonify({
            'featured': featured.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/background')
def get_background():
    """Get current background image"""
    try:
        background = BackgroundImage.query.filter_by(is_active=True).first()
        
        if not background:
            return jsonify({'background': None})
        
        return jsonify({
            'background': background.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/contact', methods=['POST'])
def submit_contact():
    """Submit contact form"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.title()} is required'}), 400
        
        contact = ContactSubmission(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            subject=data.get('subject', ''),
            message=data['message']
        )
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            'message': 'Contact form submitted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

