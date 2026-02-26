"""
Mental Health Chatbot Application Package
"""
import os
from flask import Flask
from config import Config

def create_app():
    """Create and configure the Flask application."""
    # Get the base directory (parent of 'app' folder)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(Config)
    
    # Register blueprints
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app

