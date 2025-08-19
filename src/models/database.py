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
# Many-to-many relationship table for images and categories
image_categories = db.Table('image_categories',
    db.Column('image_id', db.Integer, db.ForeignKey('portfolio_images.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

# Update your existing PortfolioImage class to include the relationship
# ADD THIS LINE to your PortfolioImage class:
# categories = db.relationship('Category', secondary=image_categories, back_populates='images')

# Update your existing Category class to include the relationship  
# ADD THIS LINE to your Category class:
# images = db.relationship('PortfolioImage', secondary=image_categories, back_populates='categories')

# ===== SECOND: ADD TO src/routes/admin.py =====
# Add these routes to the END of your admin.py file

@admin_bp.route('/admin/categories')
def category_management():
    """Category management interface"""
    try:
        # Get all categories
        categories = Category.query.order_by(Category.id.asc()).all()
        
        # Get category statistics
        total_categories = len(categories)
        categories_with_images = len([cat for cat in categories if len(cat.images) > 0])
        
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
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .header { text-align: center; margin-bottom: 30px; }
                .header h1 { color: #ff6b35; font-size: 2em; margin-bottom: 10px; }
                .back-btn { display: inline-block; margin-bottom: 20px; padding: 8px 16px; background: #555; color: white; text-decoration: none; border-radius: 4px; }
                .back-btn:hover { background: #666; }
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
                .stat-box { background: #2a2a2a; padding: 20px; border-radius: 8px; text-align: center; border-left: 5px solid #ff6b35; }
                .stat-box h3 { color: #ff6b35; font-size: 2em; margin-bottom: 5px; }
                .stat-box p { color: #ccc; }
                .section { background: #2a2a2a; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .section h3 { color: #ff6b35; margin-bottom: 15px; }
                .btn { padding: 12px 24px; margin: 5px; background: #ff6b35; color: white; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
                .btn:hover { background: #e55a2b; }
                .btn.success { background: #28a745; }
                .btn.success:hover { background: #218838; }
                .btn.danger { background: #dc3545; }
                .btn.danger:hover { background: #c82333; }
                .status { padding: 15px; margin: 15px 0; border-radius: 5px; }
                .status.success { background: #28a745; }
                .status.error { background: #dc3545; }
                .status.info { background: #17a2b8; }
                .form-group { margin-bottom: 15px; }
                .form-group label { display: block; margin-bottom: 5px; color: #ff6b35; font-weight: bold; }
                .form-group input, .form-group textarea { width: 100%; padding: 10px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; }
                .category-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; margin-top: 20px; }
                .category-item { background: #333; padding: 15px; border-radius: 8px; }
                .category-item h4 { color: #ff6b35; margin-bottom: 10px; }
                .category-item p { color: #ccc; margin-bottom: 10px; }
                .category-stats { font-size: 0.9em; color: #888; margin-bottom: 10px; }
                .category-actions { display: flex; gap: 5px; }
                .category-actions button { padding: 6px 12px; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="container">
                <a href="/admin" class="back-btn">← Back to Admin</a>
                <div class="header">
                    <h1>Category Management</h1>
                    <p>Organize your portfolio with categories</p>
                </div>
                
                <div class="stats">
                    <div class="stat-box">
                        <h3>{{ total_categories }}</h3>
                        <p>Total Categories</p>
                    </div>
                    <div class="stat-box">
                        <h3>{{ categories_with_images }}</h3>
                        <p>Categories with Images</p>
                    </div>
                </div>
                
                <div class="section">
                    <h3>➕ Add New Category</h3>
                    <form id="add-category-form">
                        <div style="display: grid; grid-template-columns: 1fr 2fr 1fr; gap: 15px; align-items: end;">
                            <div class="form-group">
                                <label for="category-name">Category Name</label>
                                <input type="text" id="category-name" name="name" placeholder="e.g., Portraits" required>
                            </div>
                            <div class="form-group">
                                <label for="category-description">Description (Optional)</label>
                                <input type="text" id="category-description" name="description" placeholder="Brief description of this category">
                            </div>
                            <div class="form-group">
                                <button type="submit" class="btn success">Add Category</button>
                            </div>
                        </div>
                    </form>
                </div>
                
                {% if not categories %}
                <div class="section">
                    <h3>🎯 No Categories Yet</h3>
                    <p>Let's create some standard photography categories to get started!</p>
                    <button class="btn success" onclick="createDefaultCategories()">Create Default Categories</button>
                    <p style="margin-top: 10px; color: #ccc; font-size: 0.9em;">
                        This will create: Portraits, Landscapes, Events, Commercial, Street, Nature
                    </p>
                </div>
                {% else %}
                <div class="section">
                    <h3>🏷️ Existing Categories</h3>
                    <div class="category-grid">
                        {% for category in categories %}
                        <div class="category-item">
                            <h4>{{ category.name }}</h4>
                            <p>{{ category.description or 'No description' }}</p>
                            <div class="category-stats">
                                📸 {{ category.images|length }} images
                            </div>
                            <div class="category-actions">
                                <button class="btn" onclick="editCategory({{ category.id }}, '{{ category.name }}', '{{ category.description or '' }}')">Edit</button>
                                <button class="btn danger" onclick="deleteCategory({{ category.id }}, '{{ category.name }}')">Delete</button>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}
                
                <div id="status"></div>
            </div>
            
            <script>
            // Add new category
            document.getElementById('add-category-form').addEventListener('submit', async function(e) {
                e.preventDefault();
                const statusDiv = document.getElementById('status');
                const formData = new FormData(this);
                
                statusDiv.innerHTML = '<div class="status info">Creating category...</div>';
                
                try {
                    const response = await fetch('/api/admin/categories', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        statusDiv.innerHTML = `<div class="status success">✅ Category "${result.name}" created successfully!</div>`;
                        setTimeout(() => window.location.reload(), 1500);
                    } else {
                        const error = await response.json();
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            });
            
            // Create default categories
            async function createDefaultCategories() {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">Creating default categories...</div>';
                
                try {
                    const response = await fetch('/api/admin/categories/defaults', {
                        method: 'POST'
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        statusDiv.innerHTML = `<div class="status success">✅ Created ${result.created_count} default categories!</div>`;
                        setTimeout(() => window.location.reload(), 1500);
                    } else {
                        const error = await response.json();
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            // Edit category
            function editCategory(id, name, description) {
                const newName = prompt('Category Name:', name);
                if (newName && newName !== name) {
                    const newDescription = prompt('Description:', description);
                    updateCategory(id, newName, newDescription);
                }
            }
            
            async function updateCategory(id, name, description) {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">Updating category...</div>';
                
                try {
                    const response = await fetch(`/api/admin/categories/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: name, description: description })
                    });
                    
                    if (response.ok) {
                        statusDiv.innerHTML = '<div class="status success">✅ Category updated successfully!</div>';
                        setTimeout(() => window.location.reload(), 1500);
                    } else {
                        const error = await response.json();
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            // Delete category
            function deleteCategory(id, name) {
                if (confirm(`Are you sure you want to delete the category "${name}"?\\n\\nThis will remove the category from all images but won't delete the images themselves.`)) {
                    performDeleteCategory(id);
                }
            }
            
            async function performDeleteCategory(id) {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">Deleting category...</div>';
                
                try {
                    const response = await fetch(`/api/admin/categories/${id}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        statusDiv.innerHTML = '<div class="status success">✅ Category deleted successfully!</div>';
                        setTimeout(() => window.location.reload(), 1500);
                    } else {
                        const error = await response.json();
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            </script>
        </body>
        </html>
        ''', 
        categories=categories,
        total_categories=total_categories,
        categories_with_images=categories_with_images)
        
    except Exception as e:
        return f"Error loading category management: {str(e)}", 500

# API endpoints for category management
@admin_bp.route('/api/admin/categories', methods=['POST'])
def create_category():
    """Create a new category"""
    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            return jsonify({'error': 'Category name is required'}), 400
        
        # Check if category already exists
        existing = Category.query.filter_by(name=name).first()
        if existing:
            return jsonify({'error': f'Category "{name}" already exists'}), 400
        
        new_category = Category(
            name=name,
            description=description if description else None
        )
        
        db.session.add(new_category)
        db.session.commit()
        
        return jsonify({
            'id': new_category.id,
            'name': new_category.name,
            'description': new_category.description,
            'message': f'Category "{name}" created successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/categories/defaults', methods=['POST'])
def create_default_categories():
    """Create default photography categories"""
    try:
        default_categories = [
            {'name': 'Portraits', 'description': 'Portrait photography - people and headshots'},
            {'name': 'Landscapes', 'description': 'Landscape and nature photography'},
            {'name': 'Events', 'description': 'Event photography - weddings, parties, celebrations'},
            {'name': 'Commercial', 'description': 'Commercial and business photography'},
            {'name': 'Street', 'description': 'Street photography and urban scenes'},
            {'name': 'Nature', 'description': 'Wildlife and nature photography'}
        ]
        
        created_count = 0
        for cat_data in default_categories:
            # Check if category already exists
            existing = Category.query.filter_by(name=cat_data['name']).first()
            if not existing:
                new_category = Category(
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(new_category)
                created_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Created {created_count} default categories',
            'created_count': created_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update a category"""
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'error': 'Category name is required'}), 400
        
        # Check if new name conflicts with existing category (excluding current one)
        existing = Category.query.filter(Category.name == name, Category.id != category_id).first()
        if existing:
            return jsonify({'error': f'Category "{name}" already exists'}), 400
        
        category.name = name
        category.description = description if description else None
        
        db.session.commit()
        
        return jsonify({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'message': f'Category "{name}" updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category"""
    try:
        category = Category.query.get_or_404(category_id)
        category_name = category.name
        
        # Remove category from all images (many-to-many relationship handles this)
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'message': f'Category "{category_name}" deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
