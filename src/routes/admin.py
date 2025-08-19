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
