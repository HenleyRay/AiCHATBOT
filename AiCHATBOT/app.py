"""
Main application entry point for the Mental Health Chatbot.
"""
from app import create_app
from config import Config

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("Mental Health Chatbot Application")
    print("=" * 60)
    print(f"Starting server on http://{Config.HOST}:{Config.PORT}")
    print(f"Debug mode: {Config.DEBUG}")
    print("=" * 60)
    
    if not Config.OPENAI_API_KEY:
        print("\n⚠️  WARNING: OpenAI API key not configured!")
        print("   The chatbot will work with limited functionality.")
        print("   Please set OPENAI_API_KEY in your .env file for full AI capabilities.\n")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )

