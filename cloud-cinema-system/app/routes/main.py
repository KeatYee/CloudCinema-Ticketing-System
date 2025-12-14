from flask import Blueprint, render_template

# Define the Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return "<h1>Cloud Cinema Homepage</h1><p>If you see this, the Modular Structure is working!</p>"