# AI-Driven Conversational System for Mental Health Screening and Supportive Intervention

A comprehensive AI-powered chatbot system designed to provide mental health screening and supportive interventions through natural conversation.

## Features

- **AI-Powered Conversations**: Natural language processing for empathetic and supportive interactions
- **Mental Health Screening**: Structured questionnaires to assess mental health status
- **Supportive Interventions**: Personalized responses and recommendations based on screening results
- **Crisis Detection**: Automatic identification of high-risk situations with appropriate responses
- **Session Management**: Secure conversation history and user session tracking
- **Web Interface**: User-friendly chat interface for easy access

## Project Structure

```
AiCHATBOT/
├── app/
│   ├── __init__.py
│   ├── chatbot.py          # Core chatbot engine
│   ├── screening.py        # Mental health screening logic
│   ├── interventions.py    # Supportive intervention system
│   ├── safety.py          # Crisis detection and safety features
│   └── routes.py          # Web application routes
├── static/
│   ├── css/
│   │   └── style.css      # Frontend styling
│   └── js/
│       └── chat.js        # Frontend chat functionality
├── templates/
│   └── index.html         # Main chat interface
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── app.py                # Main application entry point
```

## Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy `env.example` to `.env`
   - Add your OpenAI API key (or other LLM API key) to `.env`

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the application**:
   - Open your browser and navigate to `http://localhost:5000`

## Configuration

### Environment Variables

- `AI_PROVIDER`: Choose `'ollama'` (free, local) or `'openai'` (paid)
- `AI_MODEL`: Model name (e.g., `llama3.2` for Ollama, `gpt-4o-mini` for OpenAI)
- `OPENAI_API_KEY`: Your OpenAI API key (only needed if `AI_PROVIDER=openai`)
- `FLASK_SECRET_KEY`: Secret key for Flask sessions
- `DEBUG`: Set to `True` for development mode

### AI Model Options

The system supports multiple AI providers:
- **Ollama (FREE, recommended)**: Runs Llama models locally on your computer
  - Models: `llama3.2`, `llama3.1`, `llama3`, `llama2`, `mistral`
  - Setup: See `OLLAMA_SETUP.md` for installation guide
- **OpenAI (Paid)**: Cloud-based GPT models
  - Models: `gpt-4o-mini`, `gpt-4`, `gpt-3.5-turbo`

## Usage

1. **Start a conversation**: The chatbot will greet you and offer to begin a mental health screening
2. **Complete screening**: Answer questions naturally through conversation
3. **Receive support**: Get personalized responses and recommendations
4. **Crisis support**: If high-risk indicators are detected, appropriate resources are provided

## Important Disclaimers

⚠️ **This system is not a replacement for professional mental health care.**
- For emergencies, contact your local emergency services
- For professional help, consult licensed mental health professionals
- This tool is designed for screening and supportive conversation only

## Safety Features

- Automatic crisis detection
- Immediate resource provision for high-risk situations
- Privacy-focused conversation handling
- No permanent storage of sensitive information (configurable)

## Development

### Adding New Screening Questions

Edit `app/screening.py` to add or modify screening questions and scoring logic.

### Customizing Interventions

Modify `app/interventions.py` to adjust intervention responses and recommendations.

### Extending AI Capabilities

Update `app/chatbot.py` to integrate additional AI models or enhance conversation logic.

## License

This project is for educational and research purposes. Please ensure compliance with healthcare regulations in your jurisdiction.

## Contributing

When contributing, please:
- Follow ethical guidelines for mental health applications
- Ensure user privacy and data protection
- Test thoroughly before deployment
- Document all changes

