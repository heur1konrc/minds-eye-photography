from flask import Blueprint, render_template_string

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin_dashboard():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin</title>
        <style>
            body { background: #1a1a1a; color: white; font-family: Arial; padding: 20px; }
            h1 { color: #ff6b35; }
        </style>
    </head>
    <body>
        <h1>Admin Dashboard</h1>
        <p>Minimal working version - we'll build from here!</p>
    </body>
    </html>
    """)
@admin_bp.route('/admin/backup')
def backup_management():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Backup</title>
        <style>
            body { background: #1a1a1a; color: white; font-family: Arial; padding: 20px; }
            h1 { color: #ff6b35; }
            .back-btn { background: #555; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; }
        </style>
    </head>
    <body>
        <a href="/admin" class="back-btn">← Back to Admin</a>
        <h1>Backup Management</h1>
        <p>Backup system will be restored here!</p>
    </body>
    </html>
    """)
    @admin_bp.route('/admin/portfolio')
def portfolio_management():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Portfolio</title>
        <style>
            body { background: #1a1a1a; color: white; font-family: Arial; padding: 20px; }
            h1 { color: #ff6b35; }
            .back-btn { background: #555; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; }
        </style>
    </head>
    <body>
        <a href="/admin" class="back-btn">← Back to Admin</a>
        <h1>Portfolio Management</h1>
        <p>Your 8 images will be restored here next!</p>
    </body>
    </html>
    """)

