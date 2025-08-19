from flask import Blueprint, render_template_string, jsonify, request, current_app, send_file
from werkzeug.utils import secure_filename
import os
import json
import tarfile
import tempfile
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

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
            db_path = 'app.db'
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
            .nav-links { margin: 20px 0; }
            .nav-links a { display: inline-block; margin: 10px; padding: 10px 20px; background: #ff6b35; color: white; text-decoration: none; border-radius: 5px; }
            .nav-links a:hover { background: #e55a2b; }
        </style>
    </head>
    <body>
        <h1>Mind's Eye Photography - Admin</h1>
        <p>Complete working admin system</p>
        <div class="nav-links">
            <a href="/admin/backup">Backup System</a>
            <a href="/admin/portfolio">Portfolio Management</a>
            <a href="/api/portfolio">View API</a>
        </div>
    </body>
    </html>
    """)

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
