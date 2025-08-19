from flask import Blueprint, request, jsonify, render_template_string, send_file
from werkzeug.utils import secure_filename
import os
import json
import tarfile
import tempfile
from datetime import datetime
from models.database import db, PortfolioImage, Category

admin_bp = Blueprint('admin', __name__)

# [Keep all your existing backup code - the create_local_backup function, api_local_backup, api_download_backup]

@admin_bp.route('/admin')
def admin_dashboard():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mind's Eye Photography - Admin v2.0</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { color: #ff6b35; font-size: 2.5em; margin-bottom: 10px; }
            .admin-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .admin-card { background: #2a2a2a; padding: 30px; border-radius: 10px; text-align: center; }
            .admin-card h3 { color: #ff6b35; margin-bottom: 15px; }
            .btn { display: inline-block; padding: 12px 24px; background: #ff6b35; color: white; text-decoration: none; border-radius: 5px; }
            .status { background: #28a745; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Mind's Eye Photography</h1>
                <div class="status">✅ System restored! Ready for categories.</div>
            </div>
            <div class="admin-grid">
                <div class="admin-card">
                    <h3>🔧 Backup</h3>
                    <a href="/admin/backup" class="btn">Backup System</a>
                </div>
                <div class="admin-card">
                    <h3>📸 Portfolio</h3>
                    <a href="/admin/portfolio" class="btn">Manage Portfolio</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

# [Keep your existing backup_management and portfolio_management functions]
