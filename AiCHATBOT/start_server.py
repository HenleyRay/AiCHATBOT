"""Start the server with proper error handling."""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from config import Config
    
    app = create_app()
    
    print("=" * 60)
    print("Mental Health Chatbot Application")
    print("=" * 60)
    print(f"Starting server on http://127.0.0.1:{Config.PORT}")
    print(f"Debug mode: {Config.DEBUG}")
    print("=" * 60)
    print("\n✓ Server is starting...")
    print(f"✓ Open your browser: http://127.0.0.1:{Config.PORT}")
    print("✓ Press Ctrl+C to stop the server\n")
    print("=" * 60)
    
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == 'your_openai_api_key_here':
        print("\n⚠️  WARNING: OpenAI API key not configured!")
        print("   The chatbot will work with limited functionality.")
        print("   Please set OPENAI_API_KEY in your .env file for full AI capabilities.\n")
    
    app.run(
        host='127.0.0.1',
        port=Config.PORT,
        debug=Config.DEBUG,
        use_reloader=False
    )
except Exception as e:
    print("\n✗ ERROR: Failed to start server")
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")
    sys.exit(1)

