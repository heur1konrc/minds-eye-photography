from flask import Blueprint, render_template, request, jsonify, send_file, current_app, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
import tarfile
import tempfile
from datetime import datetime
import uuid
from models.database import db, PortfolioImage, Category

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

def get_base_template():
    """Simple base template without complex Jinja2 variables"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mind's Eye Photography Admin</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                background: #1a1a1a; 
                color: white; 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                line-height: 1.6; 
            }
            
            /* Top Navigation Bar */
            .admin-nav {
                background: #2a2a2a;
                border-bottom: 3px solid #ff6b35;
                padding: 0;
                position: sticky;
                top: 0;
                z-index: 1000;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }
            .nav-container {
                max-width: 1400px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 20px;
            }
            .nav-brand {
                color: #ff6b35;
                font-size: 1.4em;
                font-weight: bold;
                text-decoration: none;
                padding: 15px 0;
            }
            .nav-brand:hover { color: #e55a2b; }
            
            .nav-links {
                display: flex;
                list-style: none;
                margin: 0;
                padding: 0;
            }
            .nav-links li {
                margin: 0;
            }
            .nav-links a {
                display: block;
                padding: 18px 20px;
                color: #ccc;
                text-decoration: none;
                transition: all 0.3s;
                border-bottom: 3px solid transparent;
                font-weight: 500;
            }
            .nav-links a:hover {
                color: white;
                background: rgba(255, 107, 53, 0.1);
                border-bottom-color: #ff6b35;
            }
            .nav-links a.active {
                color: #ff6b35;
                background: rgba(255, 107, 53, 0.1);
                border-bottom-color: #ff6b35;
            }
            
            /* Main Content Area */
            .admin-content {
                max-width: 1400px;
                margin: 0 auto;
                padding: 30px 20px;
                min-height: calc(100vh - 80px);
            }
            
            /* Page Header */
            .page-header {
                margin-bottom: 30px;
                border-bottom: 1px solid #333;
                padding-bottom: 20px;
            }
            .page-header h1 {
                color: #ff6b35;
                font-size: 2.2em;
                margin-bottom: 8px;
            }
            .page-header p {
                color: #ccc;
                font-size: 1.1em;
            }
            
            /* Common Styles */
            .section {
                background: #2a2a2a;
                padding: 25px;
                border-radius: 12px;
                margin: 25px 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .section h3 {
                color: #ff6b35;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            .section p {
                color: #ccc;
                margin-bottom: 15px;
            }
            
            .btn {
                padding: 12px 24px;
                margin: 5px;
                background: #ff6b35;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                font-weight: 500;
                transition: all 0.3s;
                font-size: 0.95em;
            }
            .btn:hover {
                background: #e55a2b;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
            }
            .btn:disabled {
                background: #666;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            .btn.success { background: #28a745; }
            .btn.success:hover { background: #218838; }
            .btn.secondary { background: #6c757d; }
            .btn.secondary:hover { background: #5a6268; }
            .btn.danger { background: #dc3545; }
            .btn.danger:hover { background: #c82333; }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }
            .stat-box {
                background: #2a2a2a;
                padding: 25px;
                border-radius: 12px;
                text-align: center;
                border-left: 5px solid #ff6b35;
                transition: transform 0.3s;
            }
            .stat-box:hover { transform: translateY(-3px); }
            .stat-box h3 {
                color: #ff6b35;
                font-size: 2.5em;
                margin: 0 0 8px 0;
                font-weight: 700;
            }
            .stat-box p {
                color: #ccc;
                margin: 0;
                font-size: 1em;
                font-weight: 500;
            }
            
            .status {
                padding: 15px 20px;
                margin: 20px 0;
                border-radius: 8px;
                border-left: 5px solid;
                font-weight: 500;
            }
            .status.success {
                background: rgba(40, 167, 69, 0.1);
                border-color: #28a745;
                color: #28a745;
            }
            .status.error {
                background: rgba(220, 53, 69, 0.1);
                border-color: #dc3545;
                color: #dc3545;
            }
            .status.info {
                background: rgba(23, 162, 184, 0.1);
                border-color: #17a2b8;
                color: #17a2b8;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #ccc;
            }
            
            /* Portfolio specific styles */
            .portfolio-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .image-card {
                background: #333;
                border-radius: 12px;
                overflow: hidden;
                transition: all 0.3s;
                position: relative;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .image-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            }
            .image-card.selected {
                border: 3px solid #ff6b35;
                box-shadow: 0 8px 25px rgba(255, 107, 53, 0.3);
            }
            
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
                top: 12px;
                left: 12px;
                width: 20px;
                height: 20px;
                cursor: pointer;
            }
            .image-id {
                position: absolute;
                top: 12px;
                right: 12px;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 0.8em;
                font-weight: 500;
            }
            
            .image-content { padding: 20px; }
            .image-title {
                font-size: 1.2em;
                font-weight: 600;
                color: #ff6b35;
                margin-bottom: 8px;
            }
            .image-description {
                color: #ccc;
                margin-bottom: 15px;
                font-size: 0.95em;
            }
            
            .current-categories h5 {
                color: #ff6b35;
                margin: 12px 0 8px 0;
                font-size: 0.9em;
                font-weight: 600;
            }
            .category-badges { margin-bottom: 15px; }
            .category-badge {
                background: #ff6b35;
                color: white;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 0.8em;
                margin: 3px;
                display: inline-block;
                cursor: pointer;
                transition: all 0.3s;
                font-weight: 500;
            }
            .category-badge:hover {
                background: #e55a2b;
                transform: translateY(-1px);
            }
            .no-categories {
                color: #888;
                font-style: italic;
                font-size: 0.85em;
            }
            
            .update-categories h5 {
                color: #ff6b35;
                margin: 12px 0 8px 0;
                font-size: 0.9em;
                font-weight: 600;
            }
            .category-checkboxes { margin-bottom: 15px; }
            .category-checkbox {
                display: block;
                margin: 6px 0;
                color: #ccc;
                font-size: 0.9em;
                cursor: pointer;
            }
            .category-checkbox input {
                margin-right: 10px;
                cursor: pointer;
            }
            
            .image-actions {
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }
            .image-actions .btn {
                padding: 8px 14px;
                font-size: 0.85em;
            }
            
            /* Form styles */
            .form-group {
                margin: 20px 0;
            }
            .form-group label {
                display: block;
                color: #ff6b35;
                margin-bottom: 8px;
                font-weight: 600;
            }
            .form-input, .form-select {
                padding: 12px;
                background: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 6px;
                width: 100%;
                max-width: 400px;
                font-size: 0.95em;
            }
            .form-input:focus, .form-select:focus {
                outline: none;
                border-color: #ff6b35;
                box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.2);
            }
            
            /* Upload styles */
            .drop-zone {
                border: 3px dashed #555;
                border-radius: 12px;
                padding: 50px;
                text-align: center;
                margin: 20px 0;
                transition: all 0.3s;
                cursor: pointer;
                background: rgba(255, 107, 53, 0.05);
            }
            .drop-zone:hover, .drop-zone.dragover {
                border-color: #ff6b35;
                background: rgba(255, 107, 53, 0.1);
                transform: translateY(-2px);
            }
            .drop-zone p {
                color: #ccc;
                margin: 12px 0;
            }
            .drop-zone .main-text {
                font-size: 1.3em;
                color: #ff6b35;
                font-weight: 600;
            }
            .file-input { display: none; }
            
            /* Responsive Design */
            @media (max-width: 768px) {
                .nav-container {
                    flex-direction: column;
                    padding: 10px 20px;
                }
                .nav-brand {
                    padding: 10px 0;
                }
                .nav-links {
                    width: 100%;
                    justify-content: center;
                }
                .nav-links a {
                    padding: 12px 15px;
                    font-size: 0.9em;
                }
                .admin-content {
                    padding: 20px 15px;
                }
                .page-header h1 {
                    font-size: 1.8em;
                }
                .stats {
                    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                    gap: 15px;
                }
            }
        </style>
    </head>
    <body>
        <!-- Persistent Top Navigation -->
        <nav class="admin-nav">
            <div class="nav-container">
                <a href="/admin" class="nav-brand">Mind's Eye Admin</a>
                <ul class="nav-links">
                    <li><a href="/admin" id="nav-portfolio">📸 Portfolio</a></li>
                    <li><a href="/admin/upload" id="nav-upload">📁 Upload</a></li>
                    <li><a href="/admin/categories" id="nav-categories">🏷️ Categories</a></li>
                    <li><a href="/admin/backup" id="nav-backup">💾 Backup</a></li>
                    <li><a href="/api/portfolio" target="_blank">🔗 API</a></li>
                </ul>
            </div>
        </nav>
        
        <!-- Main Content Area -->
        <div class="admin-content">
            <div class="page-header">
                <h1 id="page-title">Loading...</h1>
                <p id="page-description">Please wait...</p>
            </div>
            
            <div id="main-content">
                <div class="loading">
                    <h3>Loading admin interface...</h3>
                    <p>Please wait while we load your data.</p>
                </div>
            </div>
        </div>
        
        <script>
        // Global variables
        let currentPage = 'portfolio';
        let allImages = [];
        let allCategories = [];
        
        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            // Determine current page from URL
            const path = window.location.pathname;
            if (path.includes('/upload')) {
                currentPage = 'upload';
            } else if (path.includes('/categories')) {
                currentPage = 'categories';
            } else if (path.includes('/backup')) {
                currentPage = 'backup';
            } else {
                currentPage = 'portfolio';
            }
            
            // Update navigation
            updateNavigation();
            
            // Load appropriate page
            loadPage();
        });
        
        function updateNavigation() {
            // Remove all active classes
            document.querySelectorAll('.nav-links a').forEach(link => {
                link.classList.remove('active');
            });
            
            // Add active class to current page
            const activeLink = document.getElementById('nav-' + currentPage);
            if (activeLink) {
                activeLink.classList.add('active');
            }
        }
        
        async function loadPage() {
            try {
                switch(currentPage) {
                    case 'portfolio':
                        await loadPortfolioPage();
                        break;
                    case 'upload':
                        await loadUploadPage();
                        break;
                    case 'categories':
                        await loadCategoriesPage();
                        break;
                    case 'backup':
                        await loadBackupPage();
                        break;
                }
            } catch (error) {
                console.error('Error loading page:', error);
                showError('Failed to load page: ' + error.message);
            }
        }
        
        async function loadPortfolioPage() {
            document.getElementById('page-title').textContent = 'Portfolio Management';
            document.getElementById('page-description').textContent = 'Professional portfolio management with category assignment and bulk operations';
            
            // Load data
            await Promise.all([loadImages(), loadCategories()]);
            
            // Render portfolio interface
            renderPortfolioInterface();
        }
        
        async function loadUploadPage() {
            document.getElementById('page-title').textContent = 'Upload Images';
            document.getElementById('page-description').textContent = 'Upload multiple images to your portfolio with drag & drop or file selection';
            
            // Load categories for dropdown
            await loadCategories();
            
            // Render upload interface
            renderUploadInterface();
        }
        
        async function loadCategoriesPage() {
            document.getElementById('page-title').textContent = 'Category Management';
            document.getElementById('page-description').textContent = 'Organize your photography portfolio into categories';
            
            // Load categories
            await loadCategories();
            
            // Render categories interface
            renderCategoriesInterface();
        }
        
        async function loadBackupPage() {
            document.getElementById('page-title').textContent = 'Backup Management';
            document.getElementById('page-description').textContent = 'Create comprehensive backups of your portfolio system';
            
            // Render backup interface
            renderBackupInterface();
        }
        
        async function loadImages() {
            try {
                const response = await fetch('/api/portfolio');
                if (!response.ok) throw new Error('Failed to load images');
                const data = await response.json();
                allImages = data.images || [];
            } catch (error) {
                console.error('Error loading images:', error);
                allImages = [];
            }
        }
        
        async function loadCategories() {
            try {
                const response = await fetch('/api/admin/categories');
                if (!response.ok) throw new Error('Failed to load categories');
                const data = await response.json();
                allCategories = data.categories || [];
            } catch (error) {
                console.error('Error loading categories:', error);
                allCategories = [];
            }
        }
        
        function renderPortfolioInterface() {
            const activeImages = allImages.filter(img => img.is_active);
            const orphanedCount = 0; // We'll calculate this if needed
            
            const html = `
                <div class="stats">
                    <div class="stat-box">
                        <h3>${allImages.length}</h3>
                        <p>Images in Database</p>
                    </div>
                    <div class="stat-box">
                        <h3>${activeImages.length}</h3>
                        <p>Active Images</p>
                    </div>
                    <div class="stat-box">
                        <h3>${orphanedCount}</h3>
                        <p>Orphaned Files</p>
                    </div>
                    <div class="stat-box">
                        <h3>${allImages.length}</h3>
                        <p>Displayed Images</p>
                    </div>
                </div>
                
                <div class="section">
                    <h3>📸 Current Portfolio (${allImages.length} images)</h3>
                    <div class="portfolio-grid" id="portfolio-grid">
                        ${allImages.map(image => renderImageCard(image)).join('')}
                    </div>
                </div>
                
                <div id="status"></div>
            `;
            
            document.getElementById('main-content').innerHTML = html;
        }
        
        function renderImageCard(image) {
            const categoryBadges = image.categories.map(cat => 
                `<span class="category-badge">${cat.name}</span>`
            ).join('');
            
            const categoryCheckboxes = allCategories.map(cat => {
                const checked = image.categories.some(imgCat => imgCat.id === cat.id) ? 'checked' : '';
                return `
                    <label class="category-checkbox">
                        <input type="checkbox" name="category_${image.id}" value="${cat.id}" ${checked}>
                        ${cat.name}
                    </label>
                `;
            }).join('');
            
            return `
                <div class="image-card" data-image-id="${image.id}">
                    <div class="image-header">
                        <img src="${image.image_url}" alt="${image.title || 'Untitled'}" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <div style="display:none; padding: 20px; text-align: center; color: #ff6b35;">
                            📷 Image: ${image.filename}
                        </div>
                        <input type="checkbox" class="image-select" onchange="updateSelectedCount()">
                        <div class="image-id">#${image.id}</div>
                    </div>
                    <div class="image-content">
                        <div class="image-title">${image.title || 'Untitled'}</div>
                        <div class="image-description">${image.description || 'No description'}</div>
                        
                        <div class="current-categories">
                            <h5>Current Categories:</h5>
                            <div class="category-badges">
                                ${categoryBadges || '<span class="no-categories">No categories assigned</span>'}
                            </div>
                        </div>
                        
                        <div class="update-categories">
                            <h5>Update Categories:</h5>
                            <div class="category-checkboxes">
                                ${categoryCheckboxes}
                            </div>
                        </div>
                        
                        <div class="image-actions">
                            <button class="btn" onclick="updateImageCategories(${image.id})">Update Categories</button>
                            <button class="btn secondary" onclick="editImage(${image.id}, '${(image.title || '').replace(/'/g, "\\'")}', '${(image.description || '').replace(/'/g, "\\'")}')">Edit Title/Description</button>
                            <button class="btn danger" onclick="deleteImage(${image.id}, '${(image.title || 'Untitled').replace(/'/g, "\\'")}')">Delete</button>
                        </div>
                    </div>
                </div>
            `;
        }
        
        function renderUploadInterface() {
            const categoryOptions = allCategories.map(cat => 
                `<option value="${cat.id}">${cat.name}</option>`
            ).join('');
            
            const html = `
                <div class="section">
                    <h3>📁 Upload Settings</h3>
                    <div class="form-group">
                        <label for="defaultTitle">Title Prefix (optional):</label>
                        <input type="text" id="defaultTitle" class="form-input" placeholder="e.g., Wedding 2025, Nature Collection">
                        <small style="color: #aaa; display: block; margin-top: 8px;">Will be added to the beginning of each image title</small>
                    </div>
                    <div class="form-group">
                        <label for="defaultCategory">Default Category (optional):</label>
                        <select id="defaultCategory" class="form-select">
                            <option value="">No default category</option>
                            ${categoryOptions}
                        </select>
                        <small style="color: #aaa; display: block; margin-top: 8px;">All uploaded images will be assigned to this category</small>
                    </div>
                </div>
                
                <div class="section">
                    <h3>📸 Select Images</h3>
                    <div class="drop-zone" id="dropZone">
                        <p class="main-text">📁 Drag & Drop Images Here</p>
                        <p>or</p>
                        <button class="btn" onclick="document.getElementById('fileInput').click()">Choose Files</button>
                        <p style="font-size: 0.9em; margin-top: 20px; color: #999;">Supported formats: JPG, PNG, GIF, WebP</p>
                    </div>
                    <input type="file" id="fileInput" class="file-input" multiple accept="image/*">
                    
                    <div id="fileList" class="file-list"></div>
                    
                    <button id="uploadButton" class="btn" onclick="uploadFiles()" style="display: none;">
                        Upload Selected Images
                    </button>
                </div>
                
                <div id="status"></div>
            `;
            
            document.getElementById('main-content').innerHTML = html;
            
            // Initialize upload functionality
            initializeUpload();
        }
        
        function renderCategoriesInterface() {
            const html = `
                <div class="stats">
                    <div class="stat-box">
                        <h3>${allCategories.length}</h3>
                        <p>Total Categories</p>
                    </div>
                    <div class="stat-box">
                        <h3>${allCategories.filter(c => c.is_active).length}</h3>
                        <p>Active Categories</p>
                    </div>
                </div>
                
                <div class="section">
                    <h3>🏷️ Create Default Categories</h3>
                    <p>Create standard photography categories to organize your portfolio</p>
                    <button class="btn success" onclick="createDefaultCategories()">
                        Create Default Photography Categories
                    </button>
                    <p style="color: #ccc; font-size: 0.9em; margin-top: 12px;">
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
                
                ${allCategories.length > 0 ? `
                <div class="section">
                    <h3>📂 Existing Categories</h3>
                    <div class="category-grid">
                        ${allCategories.map(cat => `
                            <div class="category-item">
                                <h4>${cat.name}</h4>
                                <p><strong>Status:</strong> ${cat.is_active ? 'Active' : 'Inactive'}</p>
                                <p><strong>Description:</strong> ${cat.description || 'No description'}</p>
                                <div class="category-actions">
                                    ${cat.is_active ? 
                                        `<button class="btn secondary" onclick="toggleCategory(${cat.id}, false)">Deactivate</button>` :
                                        `<button class="btn success" onclick="toggleCategory(${cat.id}, true)">Activate</button>`
                                    }
                                    <button class="btn danger" onclick="deleteCategory(${cat.id}, '${cat.name}')">Delete</button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                <div id="status"></div>
            `;
            
            document.getElementById('main-content').innerHTML = html;
        }
        
        function renderBackupInterface() {
            const html = `
                <div class="section">
                    <h3>🔧 Create Local Backup</h3>
                    <p>Create a comprehensive backup including database and all portfolio images</p>
                    
                    <div class="form-group">
                        <label for="backupFilename">Custom Backup Filename (optional):</label>
                        <input type="text" id="backupFilename" class="form-input" placeholder="e.g., portfolio_backup_2025">
                        <small style="color: #aaa; display: block; margin-top: 8px;">Leave empty for automatic timestamp filename</small>
                    </div>
                    
                    <button class="btn" onclick="createLocalBackup()">Create & Download Backup</button>
                </div>
                
                <div id="status"></div>
            `;
            
            document.getElementById('main-content').innerHTML = html;
        }
        
        function showError(message) {
            document.getElementById('main-content').innerHTML = `
                <div class="section">
                    <h3>❌ Error</h3>
                    <div class="status error">
                        ${message}
                    </div>
                </div>
            `;
        }
        
        function showStatus(message, type = 'info') {
            const statusDiv = document.getElementById('status');
            if (statusDiv) {
                statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
            }
        }
        
        // Portfolio functions
        function updateSelectedCount() {
            // Implementation for selected count
        }
        
        async function updateImageCategories(imageId) {
            const imageCard = document.querySelector(`[data-image-id="${imageId}"]`);
            const checkboxes = imageCard.querySelectorAll('input[name^="category_"]');
            
            const selectedCategories = Array.from(checkboxes)
                .filter(cb => cb.checked)
                .map(cb => parseInt(cb.value));
            
            showStatus('Updating categories...', 'info');
            
            try {
                const response = await fetch(`/api/admin/portfolio/images/${imageId}/categories`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category_ids: selectedCategories })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showStatus(`✅ Categories updated for "${result.title}"! Refreshing page...`, 'success');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    const error = await response.json();
                    showStatus(`❌ Error: ${error.message || error.error}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Error: ${error.message}`, 'error');
            }
        }
        
        function editImage(imageId, title, description) {
            const newTitle = prompt('Enter new title:', title);
            if (newTitle === null) return;
            
            const newDescription = prompt('Enter new description:', description);
            if (newDescription === null) return;
            
            showStatus('Saving changes...', 'info');
            
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
                    showStatus('✅ Image details updated! Refreshing page...', 'success');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    showStatus(`❌ Error: ${result.error}`, 'error');
                }
            })
            .catch(error => {
                showStatus(`❌ Error: ${error.message}`, 'error');
            });
        }
        
        async function deleteImage(imageId, title) {
            if (!confirm(`Are you sure you want to delete "${title}"? This action cannot be undone.`)) {
                return;
            }
            
            showStatus('Deleting image...', 'info');
            
            try {
                const response = await fetch(`/api/admin/portfolio/images/${imageId}/delete`, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showStatus(`✅ Image "${result.title}" deleted successfully! Refreshing page...`, 'success');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    const error = await response.json();
                    showStatus(`❌ Error: ${error.message || error.error}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Error: ${error.message}`, 'error');
            }
        }
        
        // Upload functions
        function initializeUpload() {
            let selectedFiles = [];
            
            const dropZone = document.getElementById('dropZone');
            const fileInput = document.getElementById('fileInput');
            
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
                    showStatus('Some files were skipped. Only image files are allowed.', 'error');
                }
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
            
            window.removeFile = function(index) {
                selectedFiles.splice(index, 1);
                updateFileList();
            };
            
            window.uploadFiles = async function() {
                if (selectedFiles.length === 0) return;
                
                const uploadButton = document.getElementById('uploadButton');
                uploadButton.disabled = true;
                
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
                        showStatus(`Uploading ${file.name} (${i + 1}/${selectedFiles.length})...`, 'info');
                        
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
                
                showStatus(`✅ Upload complete! Uploaded: ${uploadedCount} images${failedCount > 0 ? `, Failed: ${failedCount} images` : ''}`, 'success');
                
                // Reset form
                selectedFiles = [];
                updateFileList();
                document.getElementById('defaultTitle').value = '';
                document.getElementById('defaultCategory').value = '';
                uploadButton.disabled = false;
            };
        }
        
        // Category functions
        async function createDefaultCategories() {
            showStatus('Creating default categories...', 'info');
            
            try {
                const response = await fetch('/api/admin/categories/create-defaults', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showStatus(`✅ ${result.created_count} default categories created successfully!`, 'success');
                    setTimeout(() => window.location.reload(), 2000);
                } else {
                    const error = await response.json();
                    showStatus(`❌ Error: ${error.message}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Error: ${error.message}`, 'error');
            }
        }
        
        async function createCategory() {
            const name = document.getElementById('categoryName').value.trim();
            const description = document.getElementById('categoryDescription').value.trim();
            
            if (!name) {
                alert('Please enter a category name');
                return;
            }
            
            showStatus('Creating category...', 'info');
            
            try {
                const response = await fetch('/api/admin/categories/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, description })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showStatus(`✅ Category "${result.name}" created successfully!`, 'success');
                    document.getElementById('categoryName').value = '';
                    document.getElementById('categoryDescription').value = '';
                    setTimeout(() => window.location.reload(), 2000);
                } else {
                    const error = await response.json();
                    showStatus(`❌ Error: ${error.message}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Error: ${error.message}`, 'error');
            }
        }
        
        async function toggleCategory(categoryId, activate) {
            const action = activate ? 'Activating' : 'Deactivating';
            showStatus(`${action} category...`, 'info');
            
            try {
                const response = await fetch(`/api/admin/categories/${categoryId}/toggle`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ is_active: activate })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showStatus(`✅ Category "${result.name}" ${activate ? 'activated' : 'deactivated'}!`, 'success');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    const error = await response.json();
                    showStatus(`❌ Error: ${error.message}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Error: ${error.message}`, 'error');
            }
        }
        
        async function deleteCategory(categoryId, categoryName) {
            if (!confirm(`Are you sure you want to delete the category "${categoryName}"? This action cannot be undone.`)) {
                return;
            }
            
            showStatus('Deleting category...', 'info');
            
            try {
                const response = await fetch(`/api/admin/categories/${categoryId}/delete`, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showStatus(`✅ Category "${result.name}" deleted successfully!`, 'success');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    const error = await response.json();
                    showStatus(`❌ Error: ${error.message}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Error: ${error.message}`, 'error');
            }
        }
        
        // Backup functions
        async function createLocalBackup() {
            const filenameInput = document.getElementById('backupFilename');
            const customFilename = filenameInput.value.trim();
            
            showStatus('Creating backup... This may take a moment.', 'info');
            
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
                    showStatus(`✅ Backup created successfully!<br><strong>File:</strong> ${result.filename}<br><strong>Size:</strong> ${result.size}<br><strong>Created:</strong> ${result.timestamp}<br><a href="${result.download_url}" class="btn" style="margin-top: 15px; text-decoration: none;">Download Backup Now</a>`, 'success');
                    
                    // Automatically start download
                    window.location.href = result.download_url;
                } else {
                    const error = await response.json();
                    showStatus(`❌ Backup failed: ${error.message}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Backup failed: ${error.message}`, 'error');
            }
        }
        </script>
    </body>
    </html>
    """

# ===== MAIN ROUTES =====

@admin_bp.route('/')
def admin_dashboard():
    """Main admin dashboard - Portfolio Management"""
    return render_template('admin/admin.html')

@admin_bp.route('/portfolio')
def admin_portfolio():
    """Portfolio Management"""
    return render_template('admin/admin.html')

@admin_bp.route('/upload')
def admin_upload():
    """Upload Management"""
    return render_template('admin/admin.html')

@admin_bp.route('/categories')
def admin_categories():
    """Category Management"""
    return render_template('admin/admin.html')

@admin_bp.route('/backup')
def admin_backup():
    """Backup Management"""
    return render_template('admin/admin.html')'/api/admin/categories')
def get_categories():
    """Get all categories for admin interface"""
    try:
        from models.database import Category
        categories = Category.query.order_by(Category.name).all()
        
        return jsonify({
            'success': True,
            'categories': [{
                'id': cat.id,
                'name': cat.name,
                'description': cat.description,
                'is_active': cat.is_active
            } for cat in categories]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
