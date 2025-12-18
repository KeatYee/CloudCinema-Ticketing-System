from flask import Blueprint, render_template

# Define the Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('homepage.html')



