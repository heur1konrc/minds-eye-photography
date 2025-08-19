from flask import Blueprint, jsonify, request
from models.database import db, PortfolioImage, Category

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/portfolio')
def get_portfolio():
    """Get all active portfolio images"""
    try:
        images = PortfolioImage.query.filter_by(is_active=True).all()
        return jsonify({
            'images': [image.to_dict() for image in images]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/categories')
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

