from flask import Blueprint
from .controller import admin_ns

admin_bp = Blueprint('admin', __name__)

# The namespace will be registered with the main API in the app/__init__.py
