from flask import Blueprint, render_template, redirect, url_for, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

admin_routes = Blueprint('admin_routes', __name__, url_prefix='/admin')

@admin_routes.route('/')
def admin_dashboard():
    """Serve the enhanced admin dashboard"""
    return render_template('admin/enhanced_dashboard.html')

@admin_routes.route('/login')
def admin_login():
    """Redirect to admin dashboard (login is handled by the frontend)"""
    return redirect(url_for('admin_routes.admin_dashboard'))

@admin_routes.route('/basic')
def admin_dashboard_basic():
    """Serve the basic admin dashboard"""
    return render_template('admin/dashboard.html')
