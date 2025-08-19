from flask import Blueprint, render_template_string, jsonify, request, current_app
import os

admin_bp = Blueprint('admin', __name__)

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
        </style>
    </head>
    <body>
        <a href="/admin" class="back-btn">← Back to Admin</a>
        <h1>Backup Management</h1>
        <p>Backup system placeholder - will add full functionality next</p>
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
