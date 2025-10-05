"""
Main routes for the note-sharing platform
Provides basic frontend pages for users
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import requests

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def index():
    """Home page - redirect to login or dashboard based on auth status"""
    return render_template('index.html')

@main_routes.route('/login')
def login_page():
    """Login page for regular users"""
    return render_template('login.html')

@main_routes.route('/register')
def register_page():
    """Registration page for new users"""
    return render_template('register.html')

@main_routes.route('/dashboard')
def dashboard():
    """Main user dashboard"""
    return render_template('dashboard.html')

@main_routes.route('/notes')
def notes():
    """Notes listing page"""
    return render_template('notes.html')
