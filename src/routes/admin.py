from flask import Blueprint, render_template_string, jsonify, request, current_app, send_file
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
        <p class="subtitle">Complete admin system with file upload and persistent storage</p>
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

@admin_bp.route('/admin/upload')
def upload_interface():
    try:
        from models.database import db, Category
        
        # Get all active categories for selection
        categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
        
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload Images</title>
            <style>
                body { background: #1a1a1a; color: white; font-family: Arial; padding: 20px; }
                h1 { color: #ff6b35; }
                .back-btn { background: #555; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; margin-bottom: 20px; display: inline-block; }
                .back-btn:hover { background: #666; }
                .upload-section { background: #2a2a2a; padding: 20px; border-radius: 10px; margin: 20px 0; }
                .upload-section h3 { color: #ff6b35; margin-bottom: 15px; }
                .upload-area { border: 2px dashed #555; padding: 40px; text-align: center; border-radius: 10px; margin: 20px 0; transition: border-color 0.3s; }
                .upload-area.dragover { border-color: #ff6b35; background: rgba(255, 107, 53, 0.1); }
                .upload-area input[type="file"] { display: none; }
                .upload-btn { background: #ff6b35; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin: 10px; }
                .upload-btn:hover { background: #e55a2b; }
                .form-group { margin: 15px 0; }
                .form-group label { display: block; margin-bottom: 5px; color: #ff6b35; font-weight: bold; }
                .form-input { padding: 10px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; width: 100%; max-width: 400px; }
                .form-select { padding: 10px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; width: 100%; max-width: 400px; }
                .status { padding: 15px; margin: 15px 0; border-radius: 5px; }
                .status.success { background: #28a745; }
                .status.error { background: #dc3545; }
                .status.info { background: #17a2b8; }
                .file-list { margin: 20px 0; }
                .file-item { background: #333; padding: 10px; margin: 5px 0; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
                .file-info { flex-grow: 1; }
                .file-actions { margin-left: 10px; }
                .remove-btn { background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; }
                .remove-btn:hover { background: #c82333; }
                .progress-bar { width: 100%; height: 20px; background: #333; border-radius: 10px; margin: 10px 0; overflow: hidden; }
                .progress-fill { height: 100%; background: #28a745; width: 0%; transition: width 0.3s; }
                .upload-options { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <h1>Upload Images</h1>
            <p>Upload multiple images to your portfolio with automatic database integration</p>
            
            <div class="upload-section">
                <h3>📁 Select Images to Upload</h3>
                <div class="upload-area" id="uploadArea">
                    <p>Drag & drop images here or click to select files</p>
                    <input type="file" id="fileInput" multiple accept="image/*">
                    <button class="upload-btn" onclick="document.getElementById('fileInput').click()">
                        Choose Files
                    </button>
                </div>
                
                <div class="upload-options">
                    <div class="form-group">
                        <label for="defaultTitle">Default Title Prefix (optional):</label>
                        <input type="text" id="defaultTitle" class="form-input" placeholder="e.g., 'Portfolio 2025'">
                        <small style="color: #aaa;">Will be combined with filename</small>
                    </div>
                    <div class="form-group">
                        <label for="defaultCategory">Default Category (optional):</label>
                        <select id="defaultCategory" class="form-select">
                            <option value="">No default category</option>
                            {% for category in categories %}
                            <option value="{{ category.id }}">{{ category.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
                
                <div id="fileList" class="file-list"></div>
                
                <div id="uploadProgress" style="display: none;">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <p id="progressText">Uploading...</p>
                </div>
                
                <button class="upload-btn" id="uploadButton" onclick="uploadFiles()" style="display: none;">
                    Upload Selected Images
                </button>
            </div>
            
            <div id="status"></div>
            
            <script>
            let selectedFiles = [];
            
            // Drag and drop functionality
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
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
                        <p><strong>Description:</strong> {{ category.description or 'No description' }}</p>
                        <p><strong>Status:</strong> 
                            <span style="color: {{ '#28a745' if category.is_active else '#dc3545' }};">
                                {{ 'Active' if category.is_active else 'Inactive' }}
                            </span>
                        </p>
                        <p><strong>Created:</strong> {{ category.created_at.strftime('%Y-%m-%d') if category.created_at else 'Unknown' }}</p>
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
                            ✅ Success! Created ${result.created_count} default categories.
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
                const statusDiv = document.getElementById('status');
                const name = document.getElementById('categoryName').value.trim();
                const description = document.getElementById('categoryDescription').value.trim();
                
                if (!name) {
                    statusDiv.innerHTML = '<div class="status error">❌ Category name is required</div>';
                    return;
                }
                
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
                            ✅ Category "${result.name}" ${activate ? 'activated' : 'deactivated'} successfully!
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
                            ✅ Category "${categoryName}" deleted successfully!
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
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Category Management</title>
            <style>
                body { background: #1a1a1a; color: white; font-family: Arial; padding: 20px; }
                h1 { color: #ff6b35; }
                .back-btn { background: #555; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; margin-bottom: 20px; display: inline-block; }
                .error { background: #dc3545; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <h1>Category Management</h1>
            <div class="error">
                <strong>Error loading categories:</strong> {{ error }}
            </div>
        </body>
        </html>
        """, error=str(e))

@admin_bp.route('/admin/portfolio')
def portfolio_management():
    try:
        from models.database import db, PortfolioImage
        
        # Get statistics
        total_images_db = PortfolioImage.query.count()
        active_images_db = PortfolioImage.query.filter_by(is_active=True).count()
        
        # Find orphaned files (images on disk but not in database)
        assets_path = os.path.join(current_app.root_path, 'static', 'assets')
        
        # Get all image files from disk
        orphaned_files = []
        if os.path.exists(assets_path):
            # Get all files in assets folder
            disk_files = [f for f in os.listdir(assets_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
            
            # Get filenames already in database
            db_filenames = {img.filename for img in PortfolioImage.query.all()}
            
            # Find orphaned files
            orphaned_files = [f for f in disk_files if f not in db_filenames]
        
        # Get all images from database for display
        portfolio_images = PortfolioImage.query.order_by(PortfolioImage.id.desc()).all()
        
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Portfolio Management</title>
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
                .status { padding: 15px; margin: 15px 0; border-radius: 5px; }
                .status.success { background: #28a745; }
                .status.error { background: #dc3545; }
                .status.info { background: #17a2b8; }
                .image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
                .image-item { background: #333; padding: 10px; border-radius: 8px; text-align: center; }
                .image-item img { max-width: 100%; height: 150px; object-fit: cover; border-radius: 4px; margin-bottom: 10px; }
                .image-item p { font-size: 0.9em; color: #ccc; margin: 5px 0; }
                .orphaned-list { background: #333; padding: 15px; border-radius: 8px; margin: 15px 0; }
                .orphaned-list ul { list-style: none; margin: 0; padding: 0; }
                .orphaned-list li { padding: 5px 0; color: #ccc; font-family: monospace; }
            </style>
        </head>
        <body>
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <h1>Portfolio Management</h1>
            <p>Manage your photography portfolio images</p>
            
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
            
            {% if portfolio_images %}
            <div class="section">
                <h3>📸 Portfolio Images in Database</h3>
                <div class="image-grid">
                    {% for image in portfolio_images %}
                    <div class="image-item">
                        <img src="/static/assets/{{ image.filename }}" alt="{{ image.title or image.filename }}">
                        <p><strong>{{ image.title or 'Untitled' }}</strong></p>
                        <p>{{ image.filename }}</p>
                        <p style="color: {{ '#28a745' if image.is_active else '#dc3545' }};">
                            {{ 'Active' if image.is_active else 'Inactive' }}
                        </p>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            <div id="status"></div>
            
            <script>
            async function addOrphanedImages() {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">Adding orphaned images to database...</div>';
                
                try {
                    const response = await fetch('/api/admin/portfolio/add-orphaned', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        statusDiv.innerHTML = `<div class="status success">
                            ✅ Success! Added ${result.added_count} images to database.<br>
                            <strong>Images are now available in your portfolio API!</strong>
                        </div>`;
                        
                        setTimeout(() => {
                            window.location.reload();
                        }, 2000);
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
        total_images_db=total_images_db,
        active_images_db=active_images_db,
        orphaned_files=orphaned_files,
        portfolio_images=portfolio_images)
        
    except Exception as e:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Portfolio Management</title>
            <style>
                body { background: #1a1a1a; color: white; font-family: Arial; padding: 20px; }
                h1 { color: #ff6b35; }
                .back-btn { background: #555; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; margin-bottom: 20px; display: inline-block; }
                .error { background: #dc3545; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <h1>Portfolio Management</h1>
            <div class="error">
                <strong>Error loading portfolio:</strong> {{ error }}
            </div>
        </body>
        </html>
        """, error=str(e))

# API Routes for file upload functionality
@admin_bp.route('/api/admin/upload', methods=['POST'])
def api_upload_file():
    """API endpoint to handle file uploads"""
    try:
        from models.database import db, PortfolioImage, Category
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Get form data
        title_prefix = request.form.get('title_prefix', '').strip()
        category_id = request.form.get('category_id', '').strip()
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        name, ext = os.path.splitext(original_filename)
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # Ensure assets directory exists
        assets_path = os.path.join(current_app.root_path, 'static', 'assets')
        os.makedirs(assets_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(assets_path, unique_filename)
        file.save(file_path)
        
        # Create title
        if title_prefix:
            title = f"{title_prefix} - {name}"
        else:
            title = name.replace('_', ' ').replace('-', ' ').title()
        
        # Create database record
        new_image = PortfolioImage(
            filename=unique_filename,
            title=title,
            description=f"Uploaded: {original_filename}",
            is_active=True
        )
        
        db.session.add(new_image)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': unique_filename,
            'title': title,
            'original_filename': original_filename
        })
        
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API Routes for backup functionality
@admin_bp.route('/api/admin/backup/local', methods=['POST'])
def api_local_backup():
    """API endpoint to create local backup with custom filename"""
    try:
        # Get custom filename from request
        data = request.get_json() or {}
        custom_filename = data.get('filename', '').strip()
        
        success, result = create_local_backup(custom_filename)
        
        if success:
            # Store the backup file path for download
            backup_files[result['filename']] = result['path']
            
            return jsonify({
                'filename': result['filename'],
                'size': result['size'],
                'timestamp': result['timestamp'],
                'download_url': f"/api/admin/backup/download/{result['filename']}"
            })
        else:
            return jsonify({
                'error': True,
                'message': result
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': True,
            'message': f"Local backup failed: {str(e)}"
        }), 500

@admin_bp.route('/api/admin/backup/download/<filename>')
def api_download_backup(filename):
    """API endpoint to download backup file"""
    try:
        if filename not in backup_files:
            return jsonify({'error': 'Backup file not found'}), 404
        
        file_path = backup_files[filename]
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Backup file no longer exists'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/gzip'
        )
        
    except Exception as e:
        return jsonify({
            'error': True,
            'message': f"Download failed: {str(e)}"
        }), 500

# API Routes for category management
@admin_bp.route('/api/admin/categories/create-defaults', methods=['POST'])
def api_create_default_categories():
    """Create default photography categories"""
    try:
        from models.database import db, Category
        
        default_categories = [
            {'name': 'Portraits', 'description': 'Portrait photography including headshots and people'},
            {'name': 'Landscapes', 'description': 'Natural landscapes and scenic photography'},
            {'name': 'Events', 'description': 'Event photography including weddings and parties'},
            {'name': 'Commercial', 'description': 'Commercial and business photography'},
            {'name': 'Street Photography', 'description': 'Candid street photography and urban scenes'},
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
            'message': f'Successfully created {created_count} default categories',
            'created_count': created_count
        })
        
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/categories/create', methods=['POST'])
def api_create_category():
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
            return jsonify({'error': f'Category "{name}" already exists'}), 400
        
        new_category = Category(
            name=name,
            description=description if description else None,
            is_active=True
        )
        
        db.session.add(new_category)
        db.session.commit()
        
        return jsonify({
            'id': new_category.id,
            'name': new_category.name,
            'description': new_category.description,
            'is_active': new_category.is_active
        })
        
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/categories/<int:category_id>/toggle', methods=['POST'])
def api_toggle_category(category_id):
    """Toggle category active status"""
    try:
        from models.database import db, Category
        
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        is_active = data.get('is_active', True)
        
        category.is_active = is_active
        db.session.commit()
        
        return jsonify({
            'id': category.id,
            'name': category.name,
            'is_active': category.is_active
        })
        
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/categories/<int:category_id>/delete', methods=['DELETE'])
def api_delete_category(category_id):
    """Delete a category"""
    try:
        from models.database import db, Category
        
        category = Category.query.get_or_404(category_id)
        category_name = category.name
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'message': f'Category "{category_name}" deleted successfully'
        })
        
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API endpoint to handle adding orphaned images
@admin_bp.route('/api/admin/portfolio/add-orphaned', methods=['POST'])
def add_orphaned_images():
    """API endpoint to add orphaned images to database"""
    try:
        from models.database import db, PortfolioImage
        
        assets_path = os.path.join(current_app.root_path, 'static', 'assets')
        
        if not os.path.exists(assets_path):
            return jsonify({'error': 'Assets folder not found'}), 404
        
        # Get all image files from disk
        disk_files = [f for f in os.listdir(assets_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
        
        # Get filenames already in database
        db_filenames = {img.filename for img in PortfolioImage.query.all()}
        
        # Find orphaned files
        orphaned_files = [f for f in disk_files if f not in db_filenames]
        
        if not orphaned_files:
            return jsonify({'message': 'No orphaned images found', 'added_count': 0})
        
        # Add orphaned images to database
        added_count = 0
        for filename in orphaned_files:
            # Create a basic title from filename
            title = filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()
            
            new_image = PortfolioImage(
                filename=filename,
                title=title,
                description=f"Imported from {filename}",
                is_active=True
            )
            
            db.session.add(new_image)
            added_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully added {added_count} images to database',
            'added_count': added_count,
            'filenames': orphaned_files
        })
        
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        return jsonify({'error': str(e)}), 500
