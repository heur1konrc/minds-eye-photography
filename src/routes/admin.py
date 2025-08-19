from flask import Blueprint, request, jsonify, render_template_string, send_file
from werkzeug.utils import secure_filename
from PIL import Image
from PIL.ExifTags import TAGS
import os
import uuid
import json
import shutil
import tarfile
import tempfile
import requests
import base64
from datetime import datetime
from models.database import db, PortfolioImage, Category, FeaturedImage, BackgroundImage, ContactSubmission

admin_bp = Blueprint('admin', __name__)

UPLOAD_FOLDER = 'src/static/assets'
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
# Portfolio Management Routes - Complete System with Batch Operations
# Add this to your src/routes/admin.py file

import os
import uuid
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from werkzeug.utils import secure_filename

# Add these routes to your admin.py file

@admin_bp.route('/admin/portfolio')
def portfolio_management():
    """Portfolio management interface with batch operations"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Portfolio Management - Mind's Eye Photography</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #ff6b35; font-size: 2em; margin-bottom: 10px; }
            .back-btn { display: inline-block; margin-bottom: 20px; padding: 8px 16px; background: #555; color: white; text-decoration: none; border-radius: 4px; }
            .back-btn:hover { background: #666; }
            
            .toolbar { background: #2a2a2a; padding: 20px; border-radius: 10px; margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
            .btn { padding: 10px 20px; background: #ff6b35; color: white; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
            .btn:hover { background: #e55a2b; }
            .btn.secondary { background: #555; }
            .btn.secondary:hover { background: #666; }
            .btn.danger { background: #dc3545; }
            .btn.danger:hover { background: #c82333; }
            .btn.success { background: #28a745; }
            .btn.success:hover { background: #218838; }
            
            .upload-area { border: 2px dashed #555; padding: 40px; text-align: center; border-radius: 10px; margin-bottom: 20px; background: #2a2a2a; }
            .upload-area.dragover { border-color: #ff6b35; background: #333; }
            .file-input { display: none; }
            
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
            .stat-card { background: #2a2a2a; padding: 15px; border-radius: 8px; text-align: center; }
            .stat-number { font-size: 2em; color: #ff6b35; font-weight: bold; }
            .stat-label { color: #ccc; margin-top: 5px; }
            
            .image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
            .image-card { background: #2a2a2a; border-radius: 10px; overflow: hidden; position: relative; }
            .image-card.selected { border: 3px solid #ff6b35; }
            .image-preview { width: 100%; height: 200px; object-fit: cover; }
            .image-info { padding: 15px; }
            .image-title { color: #ff6b35; font-weight: bold; margin-bottom: 5px; }
            .image-filename { color: #888; font-size: 0.9em; margin-bottom: 10px; }
            .image-meta { font-size: 0.8em; color: #ccc; }
            
            .checkbox { position: absolute; top: 10px; left: 10px; width: 20px; height: 20px; }
            .status { padding: 15px; margin: 15px 0; border-radius: 5px; }
            .status.success { background: #28a745; }
            .status.error { background: #dc3545; }
            .status.info { background: #17a2b8; }
            
            .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; }
            .modal-content { background: #2a2a2a; margin: 5% auto; padding: 20px; width: 90%; max-width: 600px; border-radius: 10px; }
            .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
            .modal-title { color: #ff6b35; font-size: 1.5em; }
            .close { color: #aaa; font-size: 28px; font-weight: bold; cursor: pointer; }
            .close:hover { color: #fff; }
            
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; color: #ff6b35; }
            .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 10px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; }
            .form-group textarea { height: 100px; resize: vertical; }
            
            .progress-bar { width: 100%; height: 20px; background: #333; border-radius: 10px; overflow: hidden; margin: 10px 0; }
            .progress-fill { height: 100%; background: #ff6b35; width: 0%; transition: width 0.3s; }
            
            .orphaned-files { background: #2a2a2a; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .orphaned-files h3 { color: #ffc107; margin-bottom: 15px; }
            .orphaned-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }
            .orphaned-item { background: #333; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <div class="header">
                <h1>Portfolio Management</h1>
                <p>Manage your photography portfolio with batch operations</p>
            </div>
            
            <!-- Statistics -->
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number" id="totalImages">0</div>
                    <div class="stat-label">Total Images</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="activeImages">0</div>
                    <div class="stat-label">Active Images</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="selectedImages">0</div>
                    <div class="stat-label">Selected</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="orphanedFiles">0</div>
                    <div class="stat-label">Orphaned Files</div>
                </div>
            </div>
            
            <!-- Toolbar -->
            <div class="toolbar">
                <button class="btn" onclick="refreshData()">🔄 Refresh</button>
                <button class="btn" onclick="detectOrphanedFiles()">🔍 Detect Orphaned Files</button>
                <button class="btn success" onclick="openBatchUpload()">📤 Batch Upload</button>
                <button class="btn secondary" onclick="selectAll()">☑️ Select All</button>
                <button class="btn secondary" onclick="selectNone()">☐ Select None</button>
                <button class="btn" onclick="batchEdit()">✏️ Batch Edit</button>
                <button class="btn danger" onclick="batchDelete()">🗑️ Batch Delete</button>
            </div>
            
            <!-- Upload Area -->
            <div class="upload-area" id="uploadArea">
                <h3>📤 Drag & Drop Images Here</h3>
                <p>Or click to select files</p>
                <input type="file" id="fileInput" class="file-input" multiple accept="image/*">
                <div class="progress-bar" id="uploadProgress" style="display: none;">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
            </div>
            
            <!-- Orphaned Files Section -->
            <div class="orphaned-files" id="orphanedSection" style="display: none;">
                <h3>⚠️ Orphaned Files Found</h3>
                <p>These image files exist but are not in the database:</p>
                <div class="orphaned-list" id="orphanedList"></div>
                <button class="btn success" onclick="addOrphanedToDatabase()">➕ Add All to Database</button>
            </div>
            
            <!-- Status Messages -->
            <div id="status"></div>
            
            <!-- Image Grid -->
            <div class="image-grid" id="imageGrid">
                <!-- Images will be loaded here -->
            </div>
        </div>
        
        <!-- Batch Upload Modal -->
        <div class="modal" id="batchUploadModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 class="modal-title">Batch Upload Images</h2>
                    <span class="close" onclick="closeBatchUpload()">&times;</span>
                </div>
                <div class="form-group">
                    <label>Select Images:</label>
                    <input type="file" id="batchFileInput" multiple accept="image/*">
                </div>
                <div class="form-group">
                    <label>Default Category:</label>
                    <select id="defaultCategory">
                        <option value="">Select Category</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Default Status:</label>
                    <select id="defaultStatus">
                        <option value="true">Active</option>
                        <option value="false">Inactive</option>
                    </select>
                </div>
                <button class="btn success" onclick="startBatchUpload()">Upload Images</button>
            </div>
        </div>
        
        <!-- Batch Edit Modal -->
        <div class="modal" id="batchEditModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 class="modal-title">Batch Edit Images</h2>
                    <span class="close" onclick="closeBatchEdit()">&times;</span>
                </div>
                <div class="form-group">
                    <label>Category (leave blank to keep current):</label>
                    <select id="batchCategory">
                        <option value="">Keep Current</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Status:</label>
                    <select id="batchStatus">
                        <option value="">Keep Current</option>
                        <option value="true">Active</option>
                        <option value="false">Inactive</option>
                    </select>
                </div>
                <button class="btn success" onclick="applyBatchEdit()">Apply Changes</button>
            </div>
        </div>
        
        <script>
        let images = [];
        let selectedImages = [];
        let orphanedFiles = [];
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadCategories();
            refreshData();
            setupDragDrop();
        });
        
        // Load categories for dropdowns
        async function loadCategories() {
            try {
                const response = await fetch('/api/categories');
                const categories = await response.json();
                
                const selects = ['defaultCategory', 'batchCategory'];
                selects.forEach(selectId => {
                    const select = document.getElementById(selectId);
                    select.innerHTML = '<option value="">Select Category</option>';
                    categories.forEach(cat => {
                        select.innerHTML += `<option value="${cat.id}">${cat.name}</option>`;
                    });
                });
            } catch (error) {
                console.error('Error loading categories:', error);
            }
        }
        
        // Refresh data
        async function refreshData() {
            await loadImages();
            updateStats();
        }
        
        // Load images from database
        async function loadImages() {
            try {
                const response = await fetch('/api/admin/portfolio/images');
                const data = await response.json();
                images = data.images || [];
                renderImages();
            } catch (error) {
                console.error('Error loading images:', error);
                showStatus('Error loading images', 'error');
            }
        }
        
        // Render images in grid
        function renderImages() {
            const grid = document.getElementById('imageGrid');
            grid.innerHTML = '';
            
            images.forEach(image => {
                const card = document.createElement('div');
                card.className = `image-card ${selectedImages.includes(image.id) ? 'selected' : ''}`;
                card.innerHTML = `
                    <input type="checkbox" class="checkbox" ${selectedImages.includes(image.id) ? 'checked' : ''} 
                           onchange="toggleSelection(${image.id})">
                    <img src="${image.image_url}" alt="${image.title || image.filename}" class="image-preview" 
                         onerror="this.src='/static/placeholder.jpg'">
                    <div class="image-info">
                        <div class="image-title">${image.title || 'Untitled'}</div>
                        <div class="image-filename">${image.filename}</div>
                        <div class="image-meta">
                            ${image.width}x${image.height} • ${(image.file_size/1024/1024).toFixed(1)}MB<br>
                            ${image.categories.map(cat => cat.name).join(', ') || 'No category'}
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });
        }
        
        // Toggle image selection
        function toggleSelection(imageId) {
            const index = selectedImages.indexOf(imageId);
            if (index > -1) {
                selectedImages.splice(index, 1);
            } else {
                selectedImages.push(imageId);
            }
            renderImages();
            updateStats();
        }
        
        // Select all images
        function selectAll() {
            selectedImages = images.map(img => img.id);
            renderImages();
            updateStats();
        }
        
        // Select no images
        function selectNone() {
            selectedImages = [];
            renderImages();
            updateStats();
        }
        
        // Update statistics
        function updateStats() {
            document.getElementById('totalImages').textContent = images.length;
            document.getElementById('activeImages').textContent = images.filter(img => img.is_active).length;
            document.getElementById('selectedImages').textContent = selectedImages.length;
            document.getElementById('orphanedFiles').textContent = orphanedFiles.length;
        }
        
        // Detect orphaned files
        async function detectOrphanedFiles() {
            try {
                const response = await fetch('/api/admin/portfolio/orphaned');
                const data = await response.json();
                orphanedFiles = data.orphaned_files || [];
                
                if (orphanedFiles.length > 0) {
                    const section = document.getElementById('orphanedSection');
                    const list = document.getElementById('orphanedList');
                    
                    list.innerHTML = '';
                    orphanedFiles.forEach(file => {
                        const item = document.createElement('div');
                        item.className = 'orphaned-item';
                        item.innerHTML = `
                            <span>${file}</span>
                            <button class="btn" onclick="addSingleOrphan('${file}')">Add</button>
                        `;
                        list.appendChild(item);
                    });
                    
                    section.style.display = 'block';
                } else {
                    document.getElementById('orphanedSection').style.display = 'none';
                    showStatus('No orphaned files found', 'success');
                }
                
                updateStats();
            } catch (error) {
                console.error('Error detecting orphaned files:', error);
                showStatus('Error detecting orphaned files', 'error');
            }
        }
        
        // Add orphaned files to database
        async function addOrphanedToDatabase() {
            try {
                const response = await fetch('/api/admin/portfolio/add-orphaned', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ files: orphanedFiles })
                });
                
                const result = await response.json();
                if (response.ok) {
                    showStatus(`Added ${result.added_count} images to database`, 'success');
                    document.getElementById('orphanedSection').style.display = 'none';
                    orphanedFiles = [];
                    refreshData();
                } else {
                    showStatus(result.error, 'error');
                }
            } catch (error) {
                console.error('Error adding orphaned files:', error);
                showStatus('Error adding orphaned files', 'error');
            }
        }
        
        // Batch delete
        async function batchDelete() {
            if (selectedImages.length === 0) {
                showStatus('No images selected', 'error');
                return;
            }
            
            if (!confirm(`Delete ${selectedImages.length} selected images?`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/admin/portfolio/batch-delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image_ids: selectedImages })
                });
                
                const result = await response.json();
                if (response.ok) {
                    showStatus(`Deleted ${result.deleted_count} images`, 'success');
                    selectedImages = [];
                    refreshData();
                } else {
                    showStatus(result.error, 'error');
                }
            } catch (error) {
                console.error('Error deleting images:', error);
                showStatus('Error deleting images', 'error');
            }
        }
        
        // Show status message
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.innerHTML = `<div class="status ${type}">${message}</div>`;
            setTimeout(() => status.innerHTML = '', 5000);
        }
        
        // Setup drag and drop
        function setupDragDrop() {
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            
            uploadArea.addEventListener('click', () => fileInput.click());
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
                handleFiles(e.dataTransfer.files);
            });
            
            fileInput.addEventListener('change', (e) => {
                handleFiles(e.target.files);
            });
        }
        
        // Handle file upload
        function handleFiles(files) {
            if (files.length > 0) {
                uploadFiles(files);
            }
        }
        
        // Upload files
        async function uploadFiles(files) {
            const formData = new FormData();
            for (let file of files) {
                formData.append('files', file);
            }
            
            const progressBar = document.getElementById('uploadProgress');
            const progressFill = document.getElementById('progressFill');
            progressBar.style.display = 'block';
            
            try {
                const response = await fetch('/api/admin/portfolio/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                if (response.ok) {
                    showStatus(`Uploaded ${result.uploaded_count} images`, 'success');
                    refreshData();
                } else {
                    showStatus(result.error, 'error');
                }
            } catch (error) {
                console.error('Error uploading files:', error);
                showStatus('Error uploading files', 'error');
            } finally {
                progressBar.style.display = 'none';
                progressFill.style.width = '0%';
            }
        }
        
        // Modal functions
        function openBatchUpload() {
            document.getElementById('batchUploadModal').style.display = 'block';
        }
        
        function closeBatchUpload() {
            document.getElementById('batchUploadModal').style.display = 'none';
        }
        
        function batchEdit() {
            if (selectedImages.length === 0) {
                showStatus('No images selected', 'error');
                return;
            }
            document.getElementById('batchEditModal').style.display = 'block';
        }
        
        function closeBatchEdit() {
            document.getElementById('batchEditModal').style.display = 'none';
        }
        
        // Apply batch edit
        async function applyBatchEdit() {
            const category = document.getElementById('batchCategory').value;
            const status = document.getElementById('batchStatus').value;
            
            try {
                const response = await fetch('/api/admin/portfolio/batch-edit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image_ids: selectedImages,
                        category_id: category || null,
                        is_active: status ? status === 'true' : null
                    })
                });
                
                const result = await response.json();
                if (response.ok) {
                    showStatus(`Updated ${result.updated_count} images`, 'success');
                    closeBatchEdit();
                    refreshData();
                } else {
                    showStatus(result.error, 'error');
                }
            } catch (error) {
                console.error('Error updating images:', error);
                showStatus('Error updating images', 'error');
            }
        }
        </script>
    </body>
    </html>
    ''')

# API Routes for Portfolio Management

@admin_bp.route('/api/admin/portfolio/images')
def api_get_portfolio_images():
    """Get all portfolio images with metadata"""
    try:
        images = PortfolioImage.query.order_by(PortfolioImage.sort_order, PortfolioImage.created_at.desc()).all()
        return jsonify({
            'images': [image.to_dict() for image in images]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/portfolio/orphaned')
def api_get_orphaned_files():
    """Find image files that exist but are not in database"""
    try:
        # Get all files in assets directory
        assets_path = 'src/static/assets'
        if not os.path.exists(assets_path):
            return jsonify({'orphaned_files': []})
        
        filesystem_files = set()
        for file in os.listdir(assets_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                filesystem_files.add(file)
        
        # Get all filenames in database
        db_files = set()
        images = PortfolioImage.query.all()
        for image in images:
            db_files.add(image.filename)
        
        # Find orphaned files
        orphaned_files = list(filesystem_files - db_files)
        
        return jsonify({
            'orphaned_files': orphaned_files,
            'total_files': len(filesystem_files),
            'db_files': len(db_files)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/portfolio/add-orphaned', methods=['POST'])
def api_add_orphaned_files():
    """Add orphaned files to database"""
    try:
        data = request.get_json()
        files = data.get('files', [])
        
        added_count = 0
        assets_path = 'src/static/assets'
        
        for filename in files:
            file_path = os.path.join(assets_path, filename)
            if os.path.exists(file_path):
                # Extract image metadata
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                        file_size = os.path.getsize(file_path)
                        
                        # Extract EXIF data
                        exif_data = {}
                        if hasattr(img, '_getexif') and img._getexif():
                            exif = img._getexif()
                            for tag_id, value in exif.items():
                                tag = TAGS.get(tag_id, tag_id)
                                exif_data[tag] = value
                        
                        # Create database record
                        portfolio_image = PortfolioImage(
                            filename=filename,
                            original_filename=filename,
                            title=filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title(),
                            width=width,
                            height=height,
                            file_size=file_size,
                            camera_make=exif_data.get('Make'),
                            camera_model=exif_data.get('Model'),
                            lens=exif_data.get('LensModel'),
                            aperture=str(exif_data.get('FNumber', '')),
                            shutter_speed=str(exif_data.get('ExposureTime', '')),
                            iso=str(exif_data.get('ISOSpeedRatings', '')),
                            focal_length=str(exif_data.get('FocalLength', '')),
                            is_active=True,
                            sort_order=0
                        )
                        
                        db.session.add(portfolio_image)
                        added_count += 1
                        
                except Exception as img_error:
                    print(f"Error processing {filename}: {img_error}")
                    continue
        
        db.session.commit()
        
        return jsonify({
            'added_count': added_count,
            'message': f'Successfully added {added_count} images to database'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/portfolio/batch-delete', methods=['POST'])
def api_batch_delete():
    """Delete multiple images"""
    try:
        data = request.get_json()
        image_ids = data.get('image_ids', [])
        
        if not image_ids:
            return jsonify({'error': 'No images selected'}), 400
        
        # Get images to delete
        images = PortfolioImage.query.filter(PortfolioImage.id.in_(image_ids)).all()
        deleted_count = 0
        
        for image in images:
            # Delete file from filesystem
            file_path = os.path.join('src/static/assets', image.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete from database
            db.session.delete(image)
            deleted_count += 1
        
        db.session.commit()
        
        return jsonify({
            'deleted_count': deleted_count,
            'message': f'Successfully deleted {deleted_count} images'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/portfolio/batch-edit', methods=['POST'])
def api_batch_edit():
    """Edit multiple images"""
    try:
        data = request.get_json()
        image_ids = data.get('image_ids', [])
        category_id = data.get('category_id')
        is_active = data.get('is_active')
        
        if not image_ids:
            return jsonify({'error': 'No images selected'}), 400
        
        images = PortfolioImage.query.filter(PortfolioImage.id.in_(image_ids)).all()
        updated_count = 0
        
        for image in images:
            if category_id:
                # Clear existing categories and add new one
                image.categories.clear()
                category = Category.query.get(category_id)
                if category:
                    image.categories.append(category)
            
            if is_active is not None:
                image.is_active = is_active
            
            image.updated_at = datetime.utcnow()
            updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'updated_count': updated_count,
            'message': f'Successfully updated {updated_count} images'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/portfolio/upload', methods=['POST'])
def api_upload_images():
    """Upload multiple images"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        uploaded_count = 0
        errors = []
        
        assets_path = 'src/static/assets'
        os.makedirs(assets_path, exist_ok=True)
        
        for file in files:
            if file and allowed_file(file.filename):
                try:
                    # Generate unique filename
                    original_filename = secure_filename(file.filename)
                    file_extension = original_filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{uuid.uuid4()}.{file_extension}"
                    
                    # Save file
                    file_path = os.path.join(assets_path, unique_filename)
                    file.save(file_path)
                    
                    # Extract metadata
                    with Image.open(file_path) as img:
                        width, height = img.size
                        file_size = os.path.getsize(file_path)
                        
                        # Extract EXIF data
                        exif_data = {}
                        if hasattr(img, '_getexif') and img._getexif():
                            exif = img._getexif()
                            for tag_id, value in exif.items():
                                tag = TAGS.get(tag_id, tag_id)
                                exif_data[tag] = value
                    
                    # Create database record
                    portfolio_image = PortfolioImage(
                        filename=unique_filename,
                        original_filename=original_filename,
                        title=original_filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title(),
                        width=width,
                        height=height,
                        file_size=file_size,
                        camera_make=exif_data.get('Make'),
                        camera_model=exif_data.get('Model'),
                        lens=exif_data.get('LensModel'),
                        aperture=str(exif_data.get('FNumber', '')),
                        shutter_speed=str(exif_data.get('ExposureTime', '')),
                        iso=str(exif_data.get('ISOSpeedRatings', '')),
                        focal_length=str(exif_data.get('FocalLength', '')),
                        is_active=True,
                        sort_order=0
                    )
                    
                    db.session.add(portfolio_image)
                    uploaded_count += 1
                    
                except Exception as e:
                    errors.append(f"Error uploading {file.filename}: {str(e)}")
        
        db.session.commit()
        
        result = {
            'uploaded_count': uploaded_count,
            'message': f'Successfully uploaded {uploaded_count} images'
        }
        
        if errors:
            result['errors'] = errors
        
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
        
        # Create backup in a temporary directory
        temp_dir = tempfile.mkdtemp()
        backup_path = os.path.join(temp_dir, backup_filename)
        
        # Create tar.gz file
        with tarfile.open(backup_path, 'w:gz') as tar:
            # Add database
            db_path = 'database/app.db'
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

@admin_bp.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mind's Eye Photography - Admin v2.0</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { color: #ff6b35; font-size: 2.5em; margin-bottom: 10px; }
            .version { color: #888; font-size: 0.9em; }
            .admin-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .admin-card { background: #2a2a2a; padding: 30px; border-radius: 10px; text-align: center; }
            .admin-card h3 { color: #ff6b35; margin-bottom: 15px; }
            .admin-card p { margin-bottom: 20px; color: #ccc; }
            .btn { display: inline-block; padding: 12px 24px; background: #ff6b35; color: white; text-decoration: none; border-radius: 5px; transition: background 0.3s; }
            .btn:hover { background: #e55a2b; }
            .status { background: #28a745; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Mind's Eye Photography</h1>
                <p>Admin Dashboard</p>
                <div class="version">v2.0 - Fresh Start with Working Backup System</div>
            </div>
            <div class="status">
                ✅ Clean deployment successful! Backup system ready for testing.
            </div>
            <div class="admin-grid">
                <div class="admin-card">
                    <h3>🔧 Backup Management</h3>
                    <p>Test the backup system FIRST before adding data</p>
                    <a href="/admin/backup" class="btn">Test Backup System</a>
                </div>
                <div class="admin-card">
                    <h3>📸 Portfolio Management</h3>
                    <p>Upload and manage your photography portfolio</p>
                    <a href="/admin/portfolio" class="btn">Manage Portfolio</a>
                </div>
                <div class="admin-card">
                    <h3>🏷️ Categories</h3>
                    <p>Create and organize image categories</p>
                    <a href="/admin/categories" class="btn">Manage Categories</a>
                </div>
                <div class="admin-card">
                    <h3>⭐ Featured Image</h3>
                    <p>Set and manage the featured image on your homepage</p>
                    <a href="/admin/featured" class="btn">Manage Featured</a>
                </div>
                <div class="admin-card">
                    <h3>🌅 Background Images</h3>
                    <p>Manage website background images</p>
                    <a href="/admin/backgrounds" class="btn">Manage Backgrounds</a>
                </div>
                <div class="admin-card">
                    <h3>📧 Contact Messages</h3>
                    <p>View and manage contact form submissions</p>
                    <a href="/admin/contacts" class="btn">View Messages</a>
                </div>
                <div class="admin-card">
                    <h3>🌐 Back to Site</h3>
                    <p>Return to the main website</p>
                    <a href="/" class="btn">View Site</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

@admin_bp.route('/admin/backup')
def backup_management():
    """Backup management interface with custom filename input"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Backup Management - Mind's Eye Photography v2.0</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; }
            .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #ff6b35; font-size: 2em; margin-bottom: 10px; }
            .backup-section { background: #2a2a2a; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .backup-section h3 { color: #ff6b35; margin-bottom: 15px; }
            .backup-section p { color: #ccc; margin-bottom: 15px; }
            .btn { padding: 12px 24px; margin: 5px; background: #ff6b35; color: white; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
            .btn:hover { background: #e55a2b; }
            .btn.secondary { background: #555; }
            .btn.secondary:hover { background: #666; }
            .status { padding: 15px; margin: 15px 0; border-radius: 5px; }
            .status.success { background: #28a745; }
            .status.error { background: #dc3545; }
            .status.info { background: #17a2b8; }
            .back-btn { display: inline-block; margin-bottom: 20px; padding: 8px 16px; background: #555; color: white; text-decoration: none; border-radius: 4px; }
            .back-btn:hover { background: #666; }
            .filename-input { padding: 10px; margin: 10px 5px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; width: 300px; }
            .filename-input::placeholder { color: #aaa; }
            .input-group { margin: 15px 0; }
            .input-group label { display: block; margin-bottom: 5px; color: #ff6b35; font-weight: bold; }
            .version { color: #888; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <div class="header">
                <h1>Backup Management</h1>
                <p>Test the backup system - v2.0 Fresh Start</p>
                <div class="version">This is the NEW backup system with working downloads!</div>
            </div>
            
            <div class="backup-section">
                <h3>🔧 Create Local Backup</h3>
                <p>Create a comprehensive backup with custom filename that downloads directly to your computer</p>
                
                <div class="input-group">
                    <label for="backupFilename">Backup Filename (optional):</label>
                    <input type="text" id="backupFilename" class="filename-input" placeholder="e.g., test_backup_v2 or leave blank for auto-generated">
                    <small style="color: #aaa; display: block; margin-top: 5px;">Leave blank for timestamp-based filename. .tar.gz will be added automatically.</small>
                </div>
                
                <button class="btn" onclick="createLocalBackup()">Create & Download Backup</button>
                
                <h4 style="color: #ff6b35; margin-top: 20px;">Backup includes:</h4>
                <ul style="margin-left: 20px; color: #ccc;">
                    <li>Database (SQLite file)</li>
                    <li>All uploaded images</li>
                    <li>Configuration and settings</li>
                    <li>Portfolio metadata</li>
                </ul>
            </div>
            
            <div id="status"></div>
        </div>
        
        <script>
        async function createLocalBackup() {
            const statusDiv = document.getElementById('status');
            const filenameInput = document.getElementById('backupFilename');
            const customFilename = filenameInput.value.trim();
            
            statusDiv.innerHTML = '<div class="status info">Creating backup...</div>';
            
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
                        <a href="${result.download_url}" class="btn" style="margin-top: 10px;">Download Backup Now</a>
                    </div>`;
                    
                    // Auto-download the backup
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
    ''')

# Placeholder routes for other admin functions
@admin_bp.route('/admin/portfolio')
def portfolio_management():
    return render_template_string('<h1>Portfolio Management</h1><p>Coming soon after backup system is tested!</p><a href="/admin">← Back to Admin</a>')

@admin_bp.route('/admin/categories')
def category_management():
    return render_template_string('<h1>Category Management</h1><p>Coming soon after backup system is tested!</p><a href="/admin">← Back to Admin</a>')

@admin_bp.route('/admin/featured')
def featured_management():
    return render_template_string('<h1>Featured Image Management</h1><p>Coming soon after backup system is tested!</p><a href="/admin">← Back to Admin</a>')

@admin_bp.route('/admin/backgrounds')
def background_management():
    return render_template_string('<h1>Background Management</h1><p>Coming soon after backup system is tested!</p><a href="/admin">← Back to Admin</a>')

@admin_bp.route('/admin/contacts')
def contact_management():
    return render_template_string('<h1>Contact Management</h1><p>Coming soon after backup system is tested!</p><a href="/admin">← Back to Admin</a>')

