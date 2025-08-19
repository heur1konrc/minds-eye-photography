from flask import Blueprint, render_template_string, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
import os
import json
import tarfile
import tempfile
from datetime import datetime
import uuid

admin_bp = Blueprint('admin', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_local_backup(custom_filename=None):
    """Create comprehensive local backup as tar.gz file with custom filename"""
    try:
        # Use custom filename or generate timestamp-based one
        if custom_filename:
            # Sanitize the filename
            safe_filename = secure_filename(custom_filename)
            if not safe_filename.endswith('.tar.gz'):
                safe_filename += '.tar.gz'
            backup_filename = safe_filename
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"minds_eye_backup_{timestamp}.tar.gz"
        
        # Create backup in a temporary directory
        temp_dir = tempfile.mkdtemp()
        backup_path = os.path.join(temp_dir, backup_filename)
        
        # Create tar.gz file
        with tarfile.open(backup_path, 'w:gz') as tar:
            # Add database
            db_path = '/mnt/data/app.db'
            if os.path.exists(db_path):
                tar.add(db_path, arcname='database/app.db')
                print(f"Added database: {db_path}")
            
            # Add all images
            assets_path = 'src/static/assets'
            if os.path.exists(assets_path):
                tar.add(assets_path, arcname='assets')
                print(f"Added assets: {assets_path}")
        
        # Get file size
        file_size = os.path.getsize(backup_path)
        size_mb = round(file_size / (1024 * 1024), 2)
        
        print(f"Backup created: {backup_path} ({size_mb} MB)")
        
        return True, {
            'filename': backup_filename,
            'path': backup_path,
            'size': f"{size_mb} MB",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        print(f"Backup error: {e}")
        return False, f"❌ Local backup failed: {str(e)}"

# Store backup files temporarily for download
backup_files = {}

@admin_bp.route('/admin')
def admin_dashboard():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard</title>
        <style>
            body { background: #1a1a1a; color: white; font-family: Arial; padding: 20px; }
            h1 { color: #ff6b35; }
            .subtitle { color: #ccc; margin-bottom: 30px; }
            .nav-links { margin: 20px 0; }
            .nav-links a { display: inline-block; margin: 10px; padding: 10px 20px; background: #ff6b35; color: white; text-decoration: none; border-radius: 5px; }
            .nav-links a:hover { background: #e55a2b; }
        </style>
    </head>
    <body>
        <h1>Mind's Eye Photography - Admin</h1>
        <p class="subtitle">Complete admin system with enhanced portfolio management</p>
        <div class="nav-links">
            <a href="/admin/backup">Backup System</a>
            <a href="/admin/portfolio">Portfolio Management</a>
            <a href="/admin/upload">Upload Images</a>
            <a href="/admin/categories">Category Management</a>
            <a href="/api/portfolio">View API</a>
        </div>
    </body>
    </html>
    """)

@admin_bp.route('/admin/portfolio')
def portfolio_management():
    try:
        from models.database import db, PortfolioImage, Category
        
        # Get filter parameters
        category_filter = request.args.get('category', '')
        
        # Get statistics
        total_images_db = PortfolioImage.query.count()
        active_images_db = PortfolioImage.query.filter_by(is_active=True).count()
        
        # Get all categories for the interface
        categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
        
        # Detect orphaned files
        assets_path = os.path.join(current_app.static_folder, 'assets')
        orphaned_files = []
        
        if os.path.exists(assets_path):
            # Get all image files from disk
            disk_files = set()
            for file in os.listdir(assets_path):
                if allowed_file(file):
                    disk_files.add(file)
            
            # Get all filenames from database
            db_files = {img.filename for img in PortfolioImage.query.all()}
            
            # Find orphaned files
            orphaned_files = list(disk_files - db_files)
        
        # Get portfolio images with optional category filter
        query = PortfolioImage.query
        
        if category_filter:
            # Filter by category
            category = Category.query.filter_by(name=category_filter).first()
            if category:
                query = query.filter(PortfolioImage.categories.contains(category))
        
        portfolio_images = query.order_by(PortfolioImage.id.desc()).all()
        
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Portfolio Management</title>
            <style>
                body { 
                    background: #1a1a1a; 
                    color: white; 
                    font-family: Arial; 
                    padding: 20px; 
                    line-height: 1.6; 
                }
                h1 { color: #ff6b35; margin-bottom: 10px; }
                .back-btn { 
                    background: #555; 
                    color: white; 
                    padding: 8px 16px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    margin-bottom: 20px; 
                    display: inline-block; 
                }
                .back-btn:hover { background: #666; }
                .stats { 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 20px; 
                    margin: 20px 0; 
                }
                .stat-box { 
                    background: #2a2a2a; 
                    padding: 20px; 
                    border-radius: 8px; 
                    text-align: center; 
                    border-left: 5px solid #ff6b35; 
                }
                .stat-box h3 { color: #ff6b35; font-size: 2em; margin: 0; }
                .stat-box p { color: #ccc; margin: 5px 0 0 0; }
                .section { 
                    background: #2a2a2a; 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin: 20px 0; 
                }
                .section h3 { color: #ff6b35; margin-bottom: 15px; }
                .btn { 
                    padding: 12px 24px; 
                    margin: 5px; 
                    background: #ff6b35; 
                    color: white; 
                    border: none; 
                    border-radius: 5px; 
                    cursor: pointer; 
                    text-decoration: none; 
                    display: inline-block; 
                }
                .btn:hover { background: #e55a2b; }
                .btn.success { background: #28a745; }
                .btn.success:hover { background: #218838; }
                .btn.secondary { background: #6c757d; }
                .btn.secondary:hover { background: #5a6268; }
                .btn.danger { background: #dc3545; }
                .btn.danger:hover { background: #c82333; }
                
                .filter-section { 
                    background: #2a2a2a; 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin: 20px 0; 
                }
                .filter-controls { 
                    display: flex; 
                    align-items: center; 
                    gap: 15px; 
                    flex-wrap: wrap; 
                }
                .filter-select { 
                    padding: 10px; 
                    background: #333; 
                    color: white; 
                    border: 1px solid #555; 
                    border-radius: 4px; 
                    min-width: 200px; 
                }
                
                .portfolio-grid { 
                    display: grid; 
                    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); 
                    gap: 20px; 
                    margin-top: 20px; 
                }
                .image-card { 
                    background: #333; 
                    border-radius: 10px; 
                    overflow: hidden; 
                    transition: transform 0.2s; 
                    position: relative; 
                }
                .image-card:hover { transform: translateY(-5px); }
                .image-card.selected { border: 3px solid #ff6b35; }
                
                .image-header { 
                    position: relative; 
                    height: 200px;
                    background: #222;
                }
                .image-header img { 
                    width: 100%; 
                    height: 100%; 
                    object-fit: cover; 
                    display: block;
                }
                .image-select { 
                    position: absolute; 
                    top: 10px; 
                    left: 10px; 
                    width: 20px; 
                    height: 20px; 
                }
                .image-id { 
                    position: absolute; 
                    top: 10px; 
                    right: 10px; 
                    background: rgba(0,0,0,0.7); 
                    color: white; 
                    padding: 4px 8px; 
                    border-radius: 4px; 
                    font-size: 0.8em; 
                }
                
                .image-content { padding: 15px; }
                .image-title { 
                    font-size: 1.1em; 
                    font-weight: bold; 
                    color: #ff6b35; 
                    margin-bottom: 5px; 
                }
                .image-description { 
                    color: #ccc; 
                    margin-bottom: 15px; 
                    font-size: 0.9em; 
                }
                
                .current-categories h5 { 
                    color: #ff6b35; 
                    margin: 10px 0 5px 0; 
                    font-size: 0.9em; 
                }
                .category-badges { margin-bottom: 15px; }
                .category-badge { 
                    background: #ff6b35; 
                    color: white; 
                    padding: 4px 8px; 
                    border-radius: 4px; 
                    font-size: 0.8em; 
                    margin: 2px; 
                    display: inline-block; 
                    cursor: pointer; 
                }
                .category-badge:hover { background: #e55a2b; }
                .no-categories { 
                    color: #888; 
                    font-style: italic; 
                    font-size: 0.8em; 
                }
                
                .update-categories h5 { 
                    color: #ff6b35; 
                    margin: 10px 0 5px 0; 
                    font-size: 0.9em; 
                }
                .category-checkboxes { margin-bottom: 15px; }
                .category-checkbox { 
                    display: block; 
                    margin: 5px 0; 
                    color: #ccc; 
                    font-size: 0.9em; 
                }
                .category-checkbox input { margin-right: 8px; }
                
                .image-actions { 
                    display: flex; 
                    gap: 5px; 
                    flex-wrap: wrap; 
                }
                .image-actions .btn { 
                    padding: 8px 12px; 
                    font-size: 0.8em; 
                }
                
                .status { 
                    padding: 15px; 
                    margin: 15px 0; 
                    border-radius: 5px; 
                }
                .status.success { background: #28a745; }
                .status.error { background: #dc3545; }
                .status.info { background: #17a2b8; }
                
                .orphaned-list { 
                    background: #333; 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin: 15px 0; 
                }
                .orphaned-list ul { 
                    margin: 10px 0; 
                    padding-left: 20px; 
                }
                .orphaned-list li { 
                    color: #ccc; 
                    margin: 5px 0; 
                }
                
                .bulk-actions { 
                    background: #2a2a2a; 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin: 20px 0; 
                }
                .bulk-controls { 
                    display: flex; 
                    align-items: center; 
                    gap: 10px; 
                    flex-wrap: wrap; 
                }
                .bulk-category-select { 
                    padding: 8px; 
                    background: #333; 
                    color: white; 
                    border: 1px solid #555; 
                    border-radius: 4px; 
                }
            </style>
        </head>
        <body>
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <h1>Portfolio Management</h1>
            <p>Professional portfolio management with category assignment and bulk operations</p>
            
            <div class="stats">
                <div class="stat-box">
                    <h3>{{ total_images_db }}</h3>
                    <p>Images in Database</p>
                </div>
                <div class="stat-box">
                    <h3>{{ active_images_db }}</h3>
                    <p>Active Images</p>
                </div>
                <div class="stat-box">
                    <h3>{{ orphaned_files|length }}</h3>
                    <p>Orphaned Files</p>
                </div>
                <div class="stat-box">
                    <h3>{{ portfolio_images|length }}</h3>
                    <p>{{ 'Filtered' if category_filter else 'Displayed' }} Images</p>
                </div>
            </div>
            
            <div class="filter-section">
                <h3>🔍 Filter Portfolio</h3>
                <div class="filter-controls">
                    <select id="categoryFilter" class="filter-select" onchange="filterByCategory()">
                        <option value="">Show All Categories</option>
                        {% for category in categories %}
                        <option value="{{ category.name }}" {{ 'selected' if category_filter == category.name else '' }}>
                            {{ category.name }}
                        </option>
                        {% endfor %}
                    </select>
                    <button class="btn secondary" onclick="clearFilter()">Clear Filter</button>
                    {% if category_filter %}
                    <span style="color: #ff6b35; font-weight: bold;">Showing: {{ category_filter }}</span>
                    {% endif %}
                </div>
            </div>
            
            {% if orphaned_files %}
            <div class="section">
                <h3>🔍 Orphaned Images Detected</h3>
                <p>Found {{ orphaned_files|length }} images on disk that aren't in the database yet.</p>
                
                <div class="orphaned-list">
                    <strong>Files found:</strong>
                    <ul>
                    {% for file in orphaned_files %}
                        <li>📸 {{ file }}</li>
                    {% endfor %}
                    </ul>
                </div>
                
                <button class="btn success" onclick="addOrphanedImages()">
                    Add All {{ orphaned_files|length }} Images to Database
                </button>
                <p style="color: #ccc; font-size: 0.9em; margin-top: 10px;">
                    This will create database records for all orphaned images with basic titles.
                </p>
            </div>
            {% endif %}
            
            <div class="bulk-actions">
                <h3>🔧 Bulk Operations</h3>
                <div class="bulk-controls">
                    <button class="btn secondary" onclick="selectAllImages()">Select All</button>
                    <button class="btn secondary" onclick="deselectAllImages()">Deselect All</button>
                    <span style="margin: 0 10px;">|</span>
                    <select id="bulkCategorySelect" class="bulk-category-select">
                        <option value="">Choose category to add...</option>
                        {% for category in categories %}
                        <option value="{{ category.id }}">{{ category.name }}</option>
                        {% endfor %}
                    </select>
                    <button class="btn" onclick="bulkAddCategory()">Add Category to Selected</button>
                    <button class="btn danger" onclick="bulkRemoveCategory()">Remove Category from Selected</button>
                </div>
                <p style="color: #ccc; font-size: 0.9em; margin-top: 10px;">
                    <span id="selectedCount">0</span> images selected
                </p>
            </div>
            
            {% if portfolio_images %}
            <div class="section">
                <h3>📸 {{ 'Filtered Portfolio' if category_filter else 'Current Portfolio' }} ({{ portfolio_images|length }} images)</h3>
                <div class="portfolio-grid">
                    {% for image in portfolio_images %}
                    <div class="image-card" data-image-id="{{ image.id }}">
                        <div class="image-header">
                            <img src="/static/assets/{{ image.filename }}" 
                                 alt="{{ image.title or 'Untitled' }}"
                                 onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                            <div style="display:none; padding: 20px; text-align: center; color: #ff6b35;">
                                📷 Image: {{ image.filename }}
                            </div>
                            <input type="checkbox" class="image-select" onchange="updateSelectedCount()">
                            <div class="image-id">#{{ image.id }}</div>
                        </div>
                        <div class="image-content">
                            <div class="image-title">{{ image.title or 'Untitled' }}</div>
                            <div class="image-description">{{ image.description or 'No description' }}</div>
                            
                            <div class="current-categories">
                                <h5>Current Categories:</h5>
                                <div class="category-badges" data-image-id="{{ image.id }}">
                                    {% if image.categories %}
                                        {% for cat in image.categories %}
                                        <span class="category-badge" onclick="filterByBadgeClick('{{ cat.name }}')">{{ cat.name }}</span>
                                        {% endfor %}
                                    {% else %}
                                    <span class="no-categories">No categories assigned</span>
                                    {% endif %}
                                </div>
                            </div>
                            
                            <div class="update-categories">
                                <h5>Update Categories:</h5>
                                <div class="category-checkboxes">
                                    {% for category in categories %}
                                    <label class="category-checkbox">
                                        <input type="checkbox" 
                                               name="category_{{ image.id }}" 
                                               value="{{ category.id }}"
                                               {{ 'checked' if category in image.categories else '' }}>
                                        {{ category.name }}
                                    </label>
                                    {% endfor %}
                                </div>
                            </div>
                            
                            <div class="image-actions">
                                <button class="btn" onclick="updateImageCategories({{ image.id }})">Update Categories</button>
                                <button class="btn secondary" onclick="editImage({{ image.id }}, '{{ (image.title or '') | replace("'", "\\'") }}', '{{ (image.description or '') | replace("'", "\\'") }}')">Edit Title/Description</button>
                                <button class="btn danger" onclick="deleteImage({{ image.id }}, '{{ (image.title or 'Untitled') | replace("'", "\\'") }}')">Delete</button>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            <div id="status"></div>
            
            <script>
            // Update selected count on page load
            document.addEventListener('DOMContentLoaded', function() {
                updateSelectedCount();
            });
            
            function filterByCategory() {
                const categoryFilter = document.getElementById('categoryFilter').value;
                const url = new URL(window.location);
                if (categoryFilter) {
                    url.searchParams.set('category', categoryFilter);
                } else {
                    url.searchParams.delete('category');
                }
                window.location.href = url.toString();
            }
            
            function clearFilter() {
                const url = new URL(window.location);
                url.searchParams.delete('category');
                window.location.href = url.toString();
            }
            
            function filterByBadgeClick(categoryName) {
                const url = new URL(window.location);
                url.searchParams.set('category', categoryName);
                window.location.href = url.toString();
            }
            
            function selectAllImages() {
                const checkboxes = document.querySelectorAll('.image-select');
                checkboxes.forEach(cb => {
                    cb.checked = true;
                    cb.closest('.image-card').classList.add('selected');
                });
                updateSelectedCount();
            }
            
            function deselectAllImages() {
                const checkboxes = document.querySelectorAll('.image-select');
                checkboxes.forEach(cb => {
                    cb.checked = false;
                    cb.closest('.image-card').classList.remove('selected');
                });
                updateSelectedCount();
            }
            
            function updateSelectedCount() {
                const checkboxes = document.querySelectorAll('.image-select:checked');
                document.getElementById('selectedCount').textContent = checkboxes.length;
                
                // Update visual selection
                document.querySelectorAll('.image-select').forEach(cb => {
                    if (cb.checked) {
                        cb.closest('.image-card').classList.add('selected');
                    } else {
                        cb.closest('.image-card').classList.remove('selected');
                    }
                });
            }
            
            async function updateImageCategories(imageId) {
                const statusDiv = document.getElementById('status');
                const imageCard = document.querySelector(`[data-image-id="${imageId}"]`).closest('.image-card');
                const checkboxes = imageCard.querySelectorAll('input[name^="category_"]');
                
                const selectedCategories = Array.from(checkboxes)
                    .filter(cb => cb.checked)
                    .map(cb => parseInt(cb.value));
                
                statusDiv.innerHTML = '<div class="status info">Updating categories...</div>';
                
                try {
                    const response = await fetch(`/api/admin/portfolio/images/${imageId}/categories`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ category_ids: selectedCategories })
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        statusDiv.innerHTML = `<div class="status success">
                            ✅ Categories updated for "${result.title}"! Refreshing page...
                        </div>`;
                        
                        // Refresh page to show updated categories
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    } else {
                        const error = await response.json();
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message || error.error}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function bulkAddCategory() {
                const categoryId = document.getElementById('bulkCategorySelect').value;
                if (!categoryId) {
                    alert('Please select a category first');
                    return;
                }
                
                const selectedImages = Array.from(document.querySelectorAll('.image-select:checked'))
                    .map(cb => parseInt(cb.closest('.image-card').dataset.imageId));
                
                if (selectedImages.length === 0) {
                    alert('Please select at least one image');
                    return;
                }
                
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">Adding category to selected images...</div>';
                
                try {
                    const response = await fetch('/api/admin/portfolio/bulk-add-category', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            image_ids: selectedImages,
                            category_id: parseInt(categoryId)
                        })
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        statusDiv.innerHTML = `<div class="status success">
                            ✅ Category added to ${result.updated_count} images! Refreshing page...
                        </div>`;
                        
                        // Refresh page to show updated categories
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    } else {
                        const error = await response.json();
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message || error.error}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function bulkRemoveCategory() {
                const categoryId = document.getElementById('bulkCategorySelect').value;
                if (!categoryId) {
                    alert('Please select a category first');
                    return;
                }
                
                const selectedImages = Array.from(document.querySelectorAll('.image-select:checked'))
                    .map(cb => parseInt(cb.closest('.image-card').dataset.imageId));
                
                if (selectedImages.length === 0) {
                    alert('Please select at least one image');
                    return;
                }
                
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">Removing category from selected images...</div>';
                
                try {
                    const response = await fetch('/api/admin/portfolio/bulk-remove-category', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            image_ids: selectedImages,
                            category_id: parseInt(categoryId)
                        })
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        statusDiv.innerHTML = `<div class="status success">
                            ✅ Category removed from ${result.updated_count} images! Refreshing page...
                        </div>`;
                        
                        // Refresh page to show updated categories
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    } else {
                        const error = await response.json();
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message || error.error}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            function editImage(imageId, title, description) {
                const newTitle = prompt('Enter new title:', title);
                if (newTitle === null) return; // User cancelled
                
                const newDescription = prompt('Enter new description:', description);
                if (newDescription === null) return; // User cancelled
                
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">Saving changes...</div>';
                
                fetch(`/api/admin/portfolio/images/${imageId}/edit`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        title: newTitle.trim(), 
                        description: newDescription.trim() 
                    })
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        statusDiv.innerHTML = '<div class="status success">✅ Image details updated! Refreshing page...</div>';
                        setTimeout(() => window.location.reload(), 1500);
                    } else {
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${result.error}</div>`;
                    }
                })
                .catch(error => {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                });
            }
            
            async function deleteImage(imageId, title) {
                if (!confirm(`Are you sure you want to delete "${title}"? This action cannot be undone.`)) {
                    return;
                }
                
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">Deleting image...</div>';
                
                try {
                    const response = await fetch(`/api/admin/portfolio/images/${imageId}/delete`, {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        statusDiv.innerHTML = `<div class="status success">
                            ✅ Image "${result.title}" deleted successfully! Refreshing page...
                        </div>`;
                        
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    } else {
                        const error = await response.json();
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message || error.error}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function addOrphanedImages() {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">Adding orphaned images to database...</div>';
                
                try {
                    const response = await fetch('/api/admin/portfolio/add-orphaned', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        statusDiv.innerHTML = `<div class="status success">
                            ✅ ${result.added_count} orphaned images added to database! Refreshing page...
                        </div>`;
                        
                        // Reload the page to show the new images
                        setTimeout(() => {
                            window.location.reload();
                        }, 2000);
                    } else {
                        const error = await response.json();
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message || error.error}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            </script>
        </body>
        </html>
        """, 
        total_images_db=total_images_db,
        active_images_db=active_images_db,
        orphaned_files=orphaned_files,
        portfolio_images=portfolio_images,
        categories=categories,
        category_filter=category_filter)
        
    except Exception as e:
        return f"Error loading portfolio management: {str(e)}"

# ===== API ROUTES =====

@admin_bp.route('/api/admin/portfolio/images/<int:image_id>/categories', methods=['POST'])
def update_image_categories(image_id):
    """Update categories for a specific image"""
    try:
        from models.database import db, PortfolioImage, Category
        
        data = request.get_json()
        category_ids = data.get('category_ids', [])
        
        # Get the image
        image = PortfolioImage.query.get_or_404(image_id)
        
        # Clear existing categories
        image.categories.clear()
        
        # Add new categories
        for cat_id in category_ids:
            category = Category.query.get(cat_id)
            if category:
                image.categories.append(category)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'title': image.title or 'Untitled',
            'categories': [{'id': cat.id, 'name': cat.name} for cat in image.categories]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/portfolio/bulk-add-category', methods=['POST'])
def bulk_add_category():
    """Add a category to multiple images"""
    try:
        from models.database import db, PortfolioImage, Category
        
        data = request.get_json()
        image_ids = data.get('image_ids', [])
        category_id = data.get('category_id')
        
        if not category_id:
            return jsonify({'error': 'Category ID is required'}), 400
        
        category = Category.query.get_or_404(category_id)
        updated_count = 0
        
        for image_id in image_ids:
            image = PortfolioImage.query.get(image_id)
            if image and category not in image.categories:
                image.categories.append(category)
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'updated_count': updated_count,
            'category_name': category.name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/portfolio/bulk-remove-category', methods=['POST'])
def bulk_remove_category():
    """Remove a category from multiple images"""
    try:
        from models.database import db, PortfolioImage, Category
        
        data = request.get_json()
        image_ids = data.get('image_ids', [])
        category_id = data.get('category_id')
        
        if not category_id:
            return jsonify({'error': 'Category ID is required'}), 400
        
        category = Category.query.get_or_404(category_id)
        updated_count = 0
        
        for image_id in image_ids:
            image = PortfolioImage.query.get(image_id)
            if image and category in image.categories:
                image.categories.remove(category)
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'updated_count': updated_count,
            'category_name': category.name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/portfolio/images/<int:image_id>/edit', methods=['POST'])
def edit_image_details(image_id):
    """Edit image title and description"""
    try:
        from models.database import db, PortfolioImage
        
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        image = PortfolioImage.query.get_or_404(image_id)
        image.title = title if title else None
        image.description = description if description else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'title': image.title,
            'description': image.description
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/portfolio/images/<int:image_id>/delete', methods=['DELETE'])
def delete_image(image_id):
    """Delete an image from database and filesystem"""
    try:
        from models.database import db, PortfolioImage
        
        image = PortfolioImage.query.get_or_404(image_id)
        title = image.title or 'Untitled'
        filename = image.filename
        
        # Delete from database
        db.session.delete(image)
        db.session.commit()
        
        # Delete file from filesystem
        try:
            file_path = os.path.join(current_app.static_folder, 'assets', filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not delete file {filename}: {e}")
        
        return jsonify({
            'success': True,
            'title': title
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/portfolio/add-orphaned', methods=['POST'])
def add_orphaned_images():
    """Add orphaned images from filesystem to database"""
    try:
        from models.database import db, PortfolioImage
        
        assets_path = os.path.join(current_app.static_folder, 'assets')
        if not os.path.exists(assets_path):
            return jsonify({'error': 'Assets directory does not exist'}), 400
        
        # Get all image files from disk
        disk_files = set()
        for file in os.listdir(assets_path):
            if allowed_file(file):
                disk_files.add(file)
        
        # Get all filenames from database
        db_files = {img.filename for img in PortfolioImage.query.all()}
        
        # Find orphaned files
        orphaned_files = list(disk_files - db_files)
        
        added_count = 0
        for filename in orphaned_files:
            # Create a clean title from filename
            title = os.path.splitext(filename)[0]
            # Remove UUID-like patterns and clean up
            if len(title) > 32 and '-' in title:
                # This looks like a UUID filename, create a generic title
                title = f"Image {added_count + 1}"
            else:
                # Clean up the filename for display
                title = title.replace('_', ' ').replace('-', ' ').title()
            
            new_image = PortfolioImage(
                filename=filename,
                title=title,
                is_active=True
            )
            db.session.add(new_image)
            added_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'added_count': added_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/upload', methods=['POST'])
def upload_image():
    """Upload a single image file"""
    try:
        from models.database import db, PortfolioImage, Category
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Save file
        assets_path = os.path.join(current_app.static_folder, 'assets')
        if not os.path.exists(assets_path):
            os.makedirs(assets_path)
        
        file_path = os.path.join(assets_path, unique_filename)
        file.save(file_path)
        
        # Create database entry
        title_prefix = request.form.get('title_prefix', '').strip()
        category_id = request.form.get('category_id')
        
        # Create title
        if title_prefix:
            title = f"{title_prefix} - {os.path.splitext(original_filename)[0]}"
        else:
            title = os.path.splitext(original_filename)[0].replace('_', ' ').title()
        
        new_image = PortfolioImage(
            filename=unique_filename,
            title=title,
            is_active=True
        )
        
        # Add category if specified
        if category_id:
            category = Category.query.get(category_id)
            if category:
                new_image.categories.append(category)
        
        db.session.add(new_image)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'title': title,
            'id': new_image.id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== EXISTING ROUTES (Upload, Backup, Categories) =====

@admin_bp.route('/admin/upload')
def upload_interface():
    try:
        from models.database import Category
        
        # Get all active categories for the dropdown
        categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
        
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload Images</title>
            <style>
                body { background: #1a1a1a; color: white; font-family: Arial; padding: 20px; line-height: 1.6; }
                h1 { color: #ff6b35; margin-bottom: 10px; }
                .back-btn { background: #555; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; margin-bottom: 20px; display: inline-block; }
                .back-btn:hover { background: #666; }
                .upload-section { background: #2a2a2a; padding: 20px; border-radius: 10px; margin: 20px 0; }
                .upload-section h3 { color: #ff6b35; margin-bottom: 15px; }
                .drop-zone { border: 3px dashed #555; border-radius: 10px; padding: 40px; text-align: center; margin: 20px 0; transition: all 0.3s; cursor: pointer; }
                .drop-zone:hover, .drop-zone.dragover { border-color: #ff6b35; background: rgba(255, 107, 53, 0.1); }
                .drop-zone p { color: #ccc; margin: 10px 0; }
                .file-input { display: none; }
                .btn { padding: 12px 24px; margin: 5px; background: #ff6b35; color: white; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
                .btn:hover { background: #e55a2b; }
                .btn:disabled { background: #666; cursor: not-allowed; }
                .btn.secondary { background: #6c757d; }
                .btn.secondary:hover { background: #5a6268; }
                .form-group { margin: 15px 0; }
                .form-group label { display: block; color: #ff6b35; margin-bottom: 5px; font-weight: bold; }
                .form-input, .form-select { padding: 10px; background: #333; color: white; border: 1px solid #555; border-radius: 4px; width: 100%; max-width: 400px; }
                .file-list { margin: 20px 0; }
                .file-item { background: #333; padding: 15px; border-radius: 5px; margin: 10px 0; display: flex; justify-content: space-between; align-items: center; }
                .file-info { flex: 1; }
                .file-actions { margin-left: 15px; }
                .remove-btn { background: #dc3545; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
                .remove-btn:hover { background: #c82333; }
                .progress-container { display: none; margin: 20px 0; }
                .progress-bar { background: #333; border-radius: 10px; overflow: hidden; height: 20px; }
                .progress-fill { background: #ff6b35; height: 100%; width: 0%; transition: width 0.3s; }
                .progress-text { text-align: center; margin: 10px 0; color: #ccc; }
                .status { padding: 15px; margin: 15px 0; border-radius: 5px; }
                .status.success { background: #28a745; }
                .status.error { background: #dc3545; }
                .status.info { background: #17a2b8; }
            </style>
        </head>
        <body>
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <h1>Upload Images</h1>
            <p>Upload multiple images to your portfolio with drag & drop or file selection</p>
            
            <div class="upload-section">
                <h3>📁 Upload Settings</h3>
                <div class="form-group">
                    <label for="defaultTitle">Title Prefix (optional):</label>
                    <input type="text" id="defaultTitle" class="form-input" placeholder="e.g., Wedding 2025">
                    <small style="color: #aaa; display: block; margin-top: 5px;">Will be added to the beginning of each image title</small>
                </div>
                <div class="form-group">
                    <label for="defaultCategory">Default Category (optional):</label>
                    <select id="defaultCategory" class="form-select">
                        <option value="">No default category</option>
                        {% for category in categories %}
                        <option value="{{ category.id }}">{{ category.name }}</option>
                        {% endfor %}
                    </select>
                    <small style="color: #aaa; display: block; margin-top: 5px;">All uploaded images will be assigned to this category</small>
                </div>
            </div>
            
            <div class="upload-section">
                <h3>📸 Select Images</h3>
                <div class="drop-zone" id="dropZone">
                    <p style="font-size: 1.2em; color: #ff6b35;">📁 Drag & Drop Images Here</p>
                    <p>or</p>
                    <button class="btn" onclick="document.getElementById('fileInput').click()">Choose Files</button>
                    <p style="font-size: 0.9em; margin-top: 15px;">Supported formats: JPG, PNG, GIF, WebP</p>
                </div>
                <input type="file" id="fileInput" class="file-input" multiple accept="image/*">
                
                <div id="fileList" class="file-list"></div>
                
                <div class="progress-container" id="uploadProgress">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <div class="progress-text" id="progressText">Preparing upload...</div>
                </div>
                
                <button id="uploadButton" class="btn" onclick="uploadFiles()" style="display: none;">
                    Upload Selected Images
                </button>
            </div>
            
            <div id="status"></div>
            
            <script>
            let selectedFiles = [];
            
            const dropZone = document.getElementById('dropZone');
            const fileInput = document.getElementById('fileInput');
            
            // Drag and drop functionality
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('dragover');
            });
            
            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('dragover');
            });
            
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('dragover');
                const files = Array.from(e.dataTransfer.files);
                addFiles(files);
            });
            
            fileInput.addEventListener('change', (e) => {
                const files = Array.from(e.target.files);
                addFiles(files);
            });
            
            function addFiles(files) {
                const validFiles = files.filter(file => {
                    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
                    return validTypes.includes(file.type);
                });
                
                selectedFiles = [...selectedFiles, ...validFiles];
                updateFileList();
                
                if (validFiles.length !== files.length) {
                    document.getElementById('status').innerHTML = 
                        '<div class="status error">Some files were skipped. Only image files are allowed.</div>';
                }
            }
            
            function removeFile(index) {
                selectedFiles.splice(index, 1);
                updateFileList();
            }
            
            function updateFileList() {
                const fileList = document.getElementById('fileList');
                const uploadButton = document.getElementById('uploadButton');
                
                if (selectedFiles.length === 0) {
                    fileList.innerHTML = '';
                    uploadButton.style.display = 'none';
                    return;
                }
                
                uploadButton.style.display = 'block';
                
                fileList.innerHTML = selectedFiles.map((file, index) => `
                    <div class="file-item">
                        <div class="file-info">
                            <strong>${file.name}</strong> (${(file.size / 1024 / 1024).toFixed(2)} MB)
                        </div>
                        <div class="file-actions">
                            <button class="remove-btn" onclick="removeFile(${index})">Remove</button>
                        </div>
                    </div>
                `).join('');
            }
            
            async function uploadFiles() {
                if (selectedFiles.length === 0) return;
                
                const statusDiv = document.getElementById('status');
                const progressDiv = document.getElementById('uploadProgress');
                const progressFill = document.getElementById('progressFill');
                const progressText = document.getElementById('progressText');
                const uploadButton = document.getElementById('uploadButton');
                
                uploadButton.disabled = true;
                progressDiv.style.display = 'block';
                statusDiv.innerHTML = '';
                
                const defaultTitle = document.getElementById('defaultTitle').value.trim();
                const defaultCategory = document.getElementById('defaultCategory').value;
                
                let uploadedCount = 0;
                let failedCount = 0;
                
                for (let i = 0; i < selectedFiles.length; i++) {
                    const file = selectedFiles[i];
                    const formData = new FormData();
                    formData.append('file', file);
                    formData.append('title_prefix', defaultTitle);
                    formData.append('category_id', defaultCategory);
                    
                    try {
                        progressText.textContent = `Uploading ${file.name} (${i + 1}/${selectedFiles.length})...`;
                        progressFill.style.width = `${(i / selectedFiles.length) * 100}%`;
                        
                        const response = await fetch('/api/admin/upload', {
                            method: 'POST',
                            body: formData
                        });
                        
                        if (response.ok) {
                            uploadedCount++;
                        } else {
                            failedCount++;
                            console.error(`Failed to upload ${file.name}`);
                        }
                    } catch (error) {
                        failedCount++;
                        console.error(`Error uploading ${file.name}:`, error);
                    }
                }
                
                progressFill.style.width = '100%';
                progressText.textContent = 'Upload complete!';
                
                statusDiv.innerHTML = `
                    <div class="status success">
                        ✅ Upload complete!<br>
                        <strong>Uploaded:</strong> ${uploadedCount} images<br>
                        ${failedCount > 0 ? `<strong>Failed:</strong> ${failedCount} images<br>` : ''}
                        <strong>Images are now available in your portfolio!</strong>
                    </div>
                `;
                
                // Reset form
                selectedFiles = [];
                updateFileList();
                document.getElementById('defaultTitle').value = '';
                document.getElementById('defaultCategory').value = '';
                uploadButton.disabled = false;
                
                setTimeout(() => {
                    progressDiv.style.display = 'none';
                }, 3000);
            }
            </script>
        </body>
        </html>
        """, categories=categories)
        
    except Exception as e:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload Images</title>
            <style>
                body { background: #1a1a1a; color: white; font-family: Arial; padding: 20px; }
                h1 { color: #ff6b35; }
                .back-btn { background: #555; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; margin-bottom: 20px; display: inline-block; }
                .error { background: #dc3545; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <h1>Upload Images</h1>
            <div class="error">
                <strong>Error loading upload interface:</strong> {{ error }}
            </div>
        </body>
        </html>
        """, error=str(e))

@admin_bp.route('/admin/backup')
def backup_management():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Backup Management</title>
        <style>
            body { background: #1a1a1a; color: white; font-family: Arial; padding: 20px; }
            h1 { color: #ff6b35; }
            .back-btn { background: #555; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; margin-bottom: 20px; display: inline-block; }
            .back-btn:hover { background: #666; }
            .backup-section { background: #2a2a2a; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .backup-section h3 { color: #ff6b35; margin-bottom: 15px; }
            .backup-section p { color: #ccc; margin-bottom: 15px; }
            .btn { padding: 12px 24px; margin: 5px; background: #ff6b35; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .btn:hover { background: #e55a2b; }
            .status { padding: 15px; margin: 15px 0; border-radius: 5px; }
            .status.success { background: #28a745; }
            .status.error { background: #dc3545; }
            .status.info { background: #17a2b8; }
            .filename-input { padding: 10px; margin: 10px 5px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; width: 300px; }
            .filename-input::placeholder { color: #aaa; }
            .input-group { margin: 15px 0; }
            .input-group label { display: block; margin-bottom: 5px; color: #ff6b35; font-weight: bold; }
        </style>
    </head>
    <body>
        <a href="/admin" class="back-btn">← Back to Admin</a>
        <h1>Backup Management</h1>
        <p>Create comprehensive backups of your portfolio system</p>
        
        <div class="backup-section">
            <h3>🔧 Create Local Backup</h3>
            <p>Create a comprehensive backup including database and all portfolio images</p>
            
            <div class="input-group">
                <label for="backupFilename">Custom Backup Filename (optional):</label>
                <input type="text" id="backupFilename" class="filename-input" placeholder="e.g., portfolio_backup_2025">
                <small style="color: #aaa; display: block; margin-top: 5px;">Leave empty for automatic timestamp filename</small>
            </div>
            
            <button class="btn" onclick="createLocalBackup()">Create & Download Backup</button>
        </div>
        
        <div id="status"></div>
        
        <script>
        async function createLocalBackup() {
            const statusDiv = document.getElementById('status');
            const filenameInput = document.getElementById('backupFilename');
            const customFilename = filenameInput.value.trim();
            
            statusDiv.innerHTML = '<div class="status info">Creating backup... This may take a moment.</div>';
            
            try {
                const response = await fetch('/api/admin/backup/local', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        filename: customFilename
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    statusDiv.innerHTML = `<div class="status success">
                        ✅ Backup created successfully!<br>
                        <strong>File:</strong> ${result.filename}<br>
                        <strong>Size:</strong> ${result.size}<br>
                        <strong>Created:</strong> ${result.timestamp}<br>
                        <a href="${result.download_url}" class="btn" style="margin-top: 10px; text-decoration: none;">Download Backup Now</a>
                    </div>`;
                    
                    // Automatically start download
                    window.location.href = result.download_url;
                } else {
                    const error = await response.json();
                    statusDiv.innerHTML = `<div class="status error">❌ Backup failed: ${error.message}</div>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="status error">❌ Backup failed: ${error.message}</div>`;
            }
        }
        </script>
    </body>
    </html>
    """)

@admin_bp.route('/api/admin/backup/local', methods=['POST'])
def create_backup():
    """Create and return local backup"""
    try:
        data = request.get_json()
        custom_filename = data.get('filename') if data else None
        
        success, result = create_local_backup(custom_filename)
        
        if success:
            # Store backup info for download
            backup_id = str(uuid.uuid4())
            backup_files[backup_id] = result
            
            return jsonify({
                'success': True,
                'filename': result['filename'],
                'size': result['size'],
                'timestamp': result['timestamp'],
                'download_url': f'/api/admin/backup/download/{backup_id}'
            })
        else:
            return jsonify({'success': False, 'message': result}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/api/admin/backup/download/<backup_id>')
def download_backup(backup_id):
    """Download backup file"""
    try:
        if backup_id not in backup_files:
            return "Backup not found", 404
        
        backup_info = backup_files[backup_id]
        backup_path = backup_info['path']
        
        if not os.path.exists(backup_path):
            return "Backup file not found", 404
        
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=backup_info['filename'],
            mimetype='application/gzip'
        )
        
    except Exception as e:
        return f"Download error: {str(e)}", 500

@admin_bp.route('/admin/categories')
def category_management():
    try:
        from models.database import db, Category
        
        # Get all categories
        categories = Category.query.order_by(Category.name).all()
        total_categories = len(categories)
        active_categories = len([c for c in categories if c.is_active])
        
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Category Management</title>
            <style>
                body { background: #1a1a1a; color: white; font-family: Arial; padding: 20px; }
                h1 { color: #ff6b35; }
                .back-btn { background: #555; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; margin-bottom: 20px; display: inline-block; }
                .back-btn:hover { background: #666; }
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
                .stat-box { background: #2a2a2a; padding: 20px; border-radius: 8px; text-align: center; border-left: 5px solid #ff6b35; }
                .stat-box h3 { color: #ff6b35; font-size: 2em; margin: 0; }
                .stat-box p { color: #ccc; margin: 5px 0 0 0; }
                .section { background: #2a2a2a; padding: 20px; border-radius: 10px; margin: 20px 0; }
                .section h3 { color: #ff6b35; margin-bottom: 15px; }
                .btn { padding: 12px 24px; margin: 5px; background: #ff6b35; color: white; border: none; border-radius: 5px; cursor: pointer; }
                .btn:hover { background: #e55a2b; }
                .btn.success { background: #28a745; }
                .btn.success:hover { background: #218838; }
                .btn.secondary { background: #6c757d; }
                .btn.secondary:hover { background: #5a6268; }
                .btn.danger { background: #dc3545; }
                .btn.danger:hover { background: #c82333; }
                .status { padding: 15px; margin: 15px 0; border-radius: 5px; }
                .status.success { background: #28a745; }
                .status.error { background: #dc3545; }
                .status.info { background: #17a2b8; }
                .form-group { margin: 15px 0; }
                .form-group label { display: block; margin-bottom: 5px; color: #ff6b35; font-weight: bold; }
                .form-input { padding: 10px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; width: 100%; max-width: 400px; }
                .form-input::placeholder { color: #aaa; }
                .category-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; margin-top: 20px; }
                .category-item { background: #333; padding: 15px; border-radius: 8px; }
                .category-item h4 { color: #ff6b35; margin: 0 0 10px 0; }
                .category-item p { color: #ccc; margin: 5px 0; font-size: 0.9em; }
                .category-actions { margin-top: 10px; }
                .category-actions button { padding: 6px 12px; margin: 2px; font-size: 0.8em; }
            </style>
        </head>
        <body>
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <h1>Category Management</h1>
            <p>Organize your photography portfolio into categories</p>
            
            <div class="stats">
                <div class="stat-box">
                    <h3>{{ total_categories }}</h3>
                    <p>Total Categories</p>
                </div>
                <div class="stat-box">
                    <h3>{{ active_categories }}</h3>
                    <p>Active Categories</p>
                </div>
            </div>
            
            <div class="section">
                <h3>🏷️ Create Default Categories</h3>
                <p>Create standard photography categories to organize your portfolio</p>
                <button class="btn success" onclick="createDefaultCategories()">
                    Create Default Photography Categories
                </button>
                <p style="color: #ccc; font-size: 0.9em; margin-top: 10px;">
                    Creates: Portraits, Landscapes, Events, Commercial, Street Photography, Nature
                </p>
            </div>
            
            <div class="section">
                <h3>➕ Add New Category</h3>
                <div class="form-group">
                    <label for="categoryName">Category Name:</label>
                    <input type="text" id="categoryName" class="form-input" placeholder="e.g., Wedding Photography">
                </div>
                <div class="form-group">
                    <label for="categoryDescription">Description (optional):</label>
                    <input type="text" id="categoryDescription" class="form-input" placeholder="Brief description of this category">
                </div>
                <button class="btn" onclick="createCategory()">Add Category</button>
            </div>
            
            {% if categories %}
            <div class="section">
                <h3>📂 Existing Categories</h3>
                <div class="category-grid">
                    {% for category in categories %}
                    <div class="category-item">
                        <h4>{{ category.name }}</h4>
                        <p><strong>Status:</strong> {{ 'Active' if category.is_active else 'Inactive' }}</p>
                        <p><strong>Description:</strong> {{ category.description or 'No description' }}</p>
                        <div class="category-actions">
                            {% if category.is_active %}
                            <button class="btn secondary" onclick="toggleCategory({{ category.id }}, false)">Deactivate</button>
                            {% else %}
                            <button class="btn success" onclick="toggleCategory({{ category.id }}, true)">Activate</button>
                            {% endif %}
                            <button class="btn danger" onclick="deleteCategory({{ category.id }}, '{{ category.name }}')">Delete</button>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            <div id="status"></div>
            
            <script>
            async function createDefaultCategories() {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">Creating default categories...</div>';
                
                try {
                    const response = await fetch('/api/admin/categories/create-defaults', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        statusDiv.innerHTML = `<div class="status success">
                            ✅ ${result.created_count} default categories created successfully!
                        </div>`;
                        setTimeout(() => window.location.reload(), 2000);
                    } else {
                        const error = await response.json();
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function createCategory() {
                const name = document.getElementById('categoryName').value.trim();
                const description = document.getElementById('categoryDescription').value.trim();
                
                if (!name) {
                    alert('Please enter a category name');
                    return;
                }
                
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">Creating category...</div>';
                
                try {
                    const response = await fetch('/api/admin/categories/create', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, description })
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        statusDiv.innerHTML = `<div class="status success">
                            ✅ Category "${result.name}" created successfully!
                        </div>`;
                        document.getElementById('categoryName').value = '';
                        document.getElementById('categoryDescription').value = '';
                        setTimeout(() => window.location.reload(), 2000);
                    } else {
                        const error = await response.json();
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function toggleCategory(categoryId, activate) {
                const statusDiv = document.getElementById('status');
                const action = activate ? 'Activating' : 'Deactivating';
                statusDiv.innerHTML = `<div class="status info">${action} category...</div>`;
                
                try {
                    const response = await fetch(`/api/admin/categories/${categoryId}/toggle`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ is_active: activate })
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        statusDiv.innerHTML = `<div class="status success">
                            ✅ Category "${result.name}" ${activate ? 'activated' : 'deactivated'}!
                        </div>`;
                        setTimeout(() => window.location.reload(), 1500);
                    } else {
                        const error = await response.json();
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function deleteCategory(categoryId, categoryName) {
                if (!confirm(`Are you sure you want to delete the category "${categoryName}"? This action cannot be undone.`)) {
                    return;
                }
                
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">Deleting category...</div>';
                
                try {
                    const response = await fetch(`/api/admin/categories/${categoryId}/delete`, {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        statusDiv.innerHTML = `<div class="status success">
                            ✅ Category "${result.name}" deleted successfully!
                        </div>`;
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
        """, 
        categories=categories,
        total_categories=total_categories,
        active_categories=active_categories)
        
    except Exception as e:
        return f"Error loading category management: {str(e)}"

@admin_bp.route('/api/admin/categories/create-defaults', methods=['POST'])
def create_default_categories():
    """Create default photography categories"""
    try:
        from models.database import db, Category
        
        default_categories = [
            {'name': 'Portraits', 'description': 'Portrait photography'},
            {'name': 'Landscapes', 'description': 'Landscape and nature photography'},
            {'name': 'Events', 'description': 'Event and celebration photography'},
            {'name': 'Commercial', 'description': 'Commercial and business photography'},
            {'name': 'Street Photography', 'description': 'Street and urban photography'},
            {'name': 'Nature', 'description': 'Wildlife and nature photography'}
        ]
        
        created_count = 0
        for cat_data in default_categories:
            # Check if category already exists
            existing = Category.query.filter_by(name=cat_data['name']).first()
            if not existing:
                new_category = Category(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    is_active=True
                )
                db.session.add(new_category)
                created_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'created_count': created_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/categories/create', methods=['POST'])
def create_category():
    """Create a new category"""
    try:
        from models.database import db, Category
        
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'error': 'Category name is required'}), 400
        
        # Check if category already exists
        existing = Category.query.filter_by(name=name).first()
        if existing:
            return jsonify({'error': 'Category already exists'}), 400
        
        new_category = Category(
            name=name,
            description=description if description else None,
            is_active=True
        )
        
        db.session.add(new_category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'name': new_category.name,
            'id': new_category.id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/categories/<int:category_id>/toggle', methods=['POST'])
def toggle_category(category_id):
    """Toggle category active status"""
    try:
        from models.database import db, Category
        
        data = request.get_json()
        is_active = data.get('is_active', True)
        
        category = Category.query.get_or_404(category_id)
        category.is_active = is_active
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'name': category.name,
            'is_active': category.is_active
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/categories/<int:category_id>/delete', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category"""
    try:
        from models.database import db, Category
        
        category = Category.query.get_or_404(category_id)
        name = category.name
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'name': name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
