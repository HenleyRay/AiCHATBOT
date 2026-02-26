"""
Flask routes for the mental health chatbot application.
"""
from flask import Blueprint, render_template, request, jsonify, session
from app.chatbot import MentalHealthChatbot
from app.interventions import InterventionSystem
import uuid

bp = Blueprint('main', __name__)

# Store chatbot instances per session (in production, use Redis or database)
chatbots = {}
intervention_system = InterventionSystem()

def get_chatbot(session_id: str) -> MentalHealthChatbot:
    """Get or create a chatbot instance for a session."""
    if session_id not in chatbots:
        chatbots[session_id] = MentalHealthChatbot()
    return chatbots[session_id]

@bp.route('/')
def index():
    """Render the main chat interface."""
    # Initialize session
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@bp.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'error': 'Message cannot be empty'
            }), 400
        
        # Get session ID
        session_id = session.get('session_id', str(uuid.uuid4()))
        if 'session_id' not in session:
            session['session_id'] = session_id
        
        # Get chatbot instance
        chatbot = get_chatbot(session_id)
        
        # Process message
        result = chatbot.process_message(user_message, session_id)
        
        # Add intervention suggestions if screening completed
        if result.get('screening_status') == 'completed':
            screening_result = result.get('screening_result', {})
            severity = screening_result.get('severity', '')
            
            interventions = intervention_system.get_interventions(severity)
            intervention_message = intervention_system.format_interventions(interventions)
            
            result['interventions'] = intervention_message
            result['intervention_data'] = interventions
        
        return jsonify({
            'success': True,
            'response': result.get('response', ''),
            'is_crisis': result.get('is_crisis', False),
            'risk_level': result.get('risk_level', 0),
            'screening_status': result.get('screening_status'),
            'suggestions': result.get('suggestions', []),
            'interventions': result.get('interventions', '')
        })
    
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500

@bp.route('/api/reset', methods=['POST'])
def reset():
    """Reset the conversation for the current session."""
    try:
        session_id = session.get('session_id')
        if session_id and session_id in chatbots:
            chatbots[session_id].reset_conversation()
        
        return jsonify({
            'success': True,
            'message': 'Conversation reset successfully'
        })
    
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500

@bp.route('/api/status', methods=['GET'])
def status():
    """Get the current status of the chatbot session."""
    try:
        session_id = session.get('session_id')
        if session_id and session_id in chatbots:
            chatbot = chatbots[session_id]
            summary = chatbot.get_conversation_summary()
            return jsonify({
                'success': True,
                'status': summary
            })
        
        return jsonify({
            'success': True,
            'status': {
                'message_count': 0,
                'screening_status': {'phase': 'not_started'},
                'has_crisis_indicators': False
            }
        })
    
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500

@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Mental Health Chatbot'
    })

