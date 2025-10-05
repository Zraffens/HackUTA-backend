from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User


def admin_required(f):
    """
    Decorator to ensure the current user is an admin.
    Should be used after @jwt_required() decorator.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        if not current_user_id:
            return jsonify({'message': 'Authentication required'}), 401
        
        user = User.query.filter_by(public_id=current_user_id).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if not user.is_admin:
            return jsonify({'message': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_admin():
    """
    Get the current admin user object.
    Should be called within an admin_required decorated function.
    """
    current_user_id = get_jwt_identity()
    return User.query.filter_by(public_id=current_user_id).first()
