# Initialize your dashboard module
from flask import Blueprint

# Define a blueprint for the dashboard
dashboard_bp = Blueprint('dashboard', __name__)

# Import routes to bind them to the dashboard blueprint
from . import routes
