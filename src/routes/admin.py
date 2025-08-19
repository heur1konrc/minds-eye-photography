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
    @admin_bp.route('/admin/backup')
def backup_management():
    """Backup management interface"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Backup Management</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .back-btn { display: inline-block; margin-bottom: 20px; padding: 8px 16px; background: #555; color: white; text-decoration: none; border-radius: 4px; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #ff6b35; }
            .btn { padding: 12px 24px; background: #ff6b35; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .status { padding: 15px; margin: 15px 0; border-radius: 5px; }
            .status.success { background: #28a745; }
            .status.error { background: #dc3545; }
            .status.info { background: #17a2b8; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <div class="header">
                <h1>Backup Management</h1>
            </div>
            <button class="btn" onclick="createBackup()">Create Backup</button>
            <div id="status"></div>
        </div>
        <script>
        async function createBackup() {
            document.getElementById('status').innerHTML = '<div class="status info">Creating backup...</div>';
            try {
                const response = await fetch('/api/admin/backup/local', { method: 'POST' });
                if (response.ok) {
                    const result = await response.json();
                    document.getElementById('status').innerHTML = `<div class="status success">✅ Backup created! <a href="${result.download_url}" style="color: white;">Download</a></div>`;
                    window.location.href = result.download_url;
                } else {
                    document.getElementById('status').innerHTML = '<div class="status error">❌ Backup failed</div>';
                }
            } catch (error) {
                document.getElementById('status').innerHTML = '<div class="status error">❌ Error: ' + error.message + '</div>';
            }
        }
        </script>
    </body>
    </html>
    ''')

@admin_bp.route('/admin/portfolio')
def portfolio_management():
    """Portfolio management interface"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Portfolio Management</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .back-btn { display: inline-block; margin-bottom: 20px; padding: 8px 16px; background: #555; color: white; text-decoration: none; border-radius: 4px; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #ff6b35; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/admin" class="back-btn">← Back to Admin</a>
            <div class="header">
                <h1>Portfolio Management</h1>
                <p>Portfolio management will be restored next!</p>
            </div>
        </div>
    </body>
    </html>
    ''')

    ''')

# [Keep your existing backup_management and portfolio_management functions]
