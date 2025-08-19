from flask import Blueprint, render_template_string

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
        </style>
    </head>
    <body>
        <a href="/admin" class="back-btn">← Back to Admin</a>
        <h1>Portfolio Management</h1>
        <p>Your 8 images will be accessible here - will add full functionality next</p>
    </body>
    </html>
    """)
