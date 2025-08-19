from flask import Blueprint, request, jsonify, render_template_string, send_file
from werkzeug.utils import secure_filename
import os
import json
import tarfile
import tempfile
from datetime import datetime
from models.database import db, PortfolioImage, Category

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
                <div class="version">v2.0 - Working Backup System</div>
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
                <p>Test the backup system - v2.0 Working Version</p>
                <div class="version">This is the WORKING backup system!</div>
            </div>
            
            <div class="backup-section">
                <h3>🔧 Create Local Backup</h3>
                <p>Create a comprehensive backup with custom filename that downloads directly to your computer</p>
                
                <div class="input-group">
                    <label for="backupFilename">Backup Filename (optional):</label>
                    <input type="text" id="backupFilename" class="filename-input" placeholder="e.g., working_v2_backup or leave blank for auto-generated">
                    <small style="color: #aaa; display: block; margin-top: 5px;">Leave blank for timestamp-based filename. .tar.gz will be added automatically.</small>
                </div>
                
                <button class="btn" onclick="createLocalBackup()">Create & Download Backup</button>
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

