"""
Configuration settings for the Mental Health Chatbot application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class."""
    
    # OpenAI API Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Application Settings
    PORT = int(os.getenv('APP_PORT', 5000))
    HOST = os.getenv('APP_HOST', '127.0.0.1')  # Use 127.0.0.1 for local access
    
    # AI Provider Configuration
    # Options: 'openai' (paid) or 'ollama' (free, runs locally)
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'ollama')
    
    # AI Model Configuration
    # For OpenAI: 'gpt-4o-mini', 'gpt-4', 'gpt-3.5-turbo', etc.
    # For Ollama: 'llama3.2', 'llama3.1', 'llama3', 'llama2', 'mistral', etc.
    AI_MODEL = os.getenv('AI_MODEL', 'llama3.2')
    # Lower temperature for more consistent, focused responses
    AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', '0.3'))
    # Reasonable length for supportive but not overwhelming replies
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '350'))
    
    # Safety Configuration
    ENABLE_CRISIS_DETECTION = os.getenv('ENABLE_CRISIS_DETECTION', 'True').lower() == 'true'
    
    # Session Configuration
    SESSION_LIFETIME_HOURS = int(os.getenv('SESSION_LIFETIME_HOURS', '24'))

