"""
Safety and crisis detection module for mental health chatbot.
"""
from typing import Dict, Tuple

class SafetyDetector:
    """Detects crisis situations and high-risk indicators in conversations."""
    
    # High-risk keywords and phrases
    CRISIS_KEYWORDS = [
        'suicide', 'kill myself', 'end my life', 'want to die', 'not worth living',
        'self harm', 'hurt myself', 'cutting', 'overdose', 'jump off',
        'no reason to live', 'better off dead', 'suicidal', 'ending it'
    ]
    
    # Moderate-risk indicators
    MODERATE_RISK_KEYWORDS = [
        'hopeless', 'helpless', 'worthless', 'no future', 'can\'t go on',
        'give up', 'desperate', 'overwhelmed', 'can\'t cope', 'breaking down'
    ]
    
    # Emergency resources
    EMERGENCY_RESOURCES = {
        'US': {
            'crisis_line': '988 Suicide & Crisis Lifeline',
            'phone': '988',
            'text': 'Text HOME to 741741',
            'website': 'https://988lifeline.org'
        },
        'UK': {
            'crisis_line': 'Samaritans',
            'phone': '116 123',
            'website': 'https://www.samaritans.org'
        },
        'general': {
            'crisis_line': 'International Crisis Support',
            'phone': 'Your local emergency services',
            'text': 'Text your local crisis line',
            'website': 'https://www.iasp.info/resources/Crisis_Centres/'
        }
    }
    
    def detect_crisis(self, message: str) -> Tuple[bool, int, str]:
        """
        Detect if a message contains crisis indicators.
        
        Args:
            message: User's message text
            
        Returns:
            Tuple of (is_crisis, risk_level, detected_keywords)
            - is_crisis: Boolean indicating if crisis detected
            - risk_level: 0 (low), 1 (moderate), 2 (high/crisis)
            - detected_keywords: String of detected keywords
        """
        message_lower = message.lower()
        detected_high = []
        detected_moderate = []
        
        # Check for high-risk keywords
        for keyword in self.CRISIS_KEYWORDS:
            if keyword in message_lower:
                detected_high.append(keyword)
        
        # Check for moderate-risk keywords
        for keyword in self.MODERATE_RISK_KEYWORDS:
            if keyword in message_lower:
                detected_moderate.append(keyword)
        
        # Determine risk level
        if detected_high:
            return True, 2, ', '.join(detected_high)
        elif detected_moderate:
            return True, 1, ', '.join(detected_moderate)
        else:
            return False, 0, ''
    
    def get_crisis_response(self, risk_level: int, country: str = 'general') -> Dict:
        """
        Get appropriate crisis response based on risk level.
        
        Args:
            risk_level: Risk level (0, 1, or 2)
            country: Country code for localized resources
            
        Returns:
            Dictionary with response message and resources
        """
        resources = self.EMERGENCY_RESOURCES.get(country, self.EMERGENCY_RESOURCES['general'])
        
        if risk_level == 2:  # High risk
            return {
                'is_crisis': True,
                'message': (
                    "I'm very concerned about what you've shared. Your safety is the most important thing right now. "
                    "Please reach out for immediate help:\n\n"
                    f"🌐 {resources['crisis_line']}: {resources['phone']}\n"
                    f"💬 {resources.get('text', 'Text your local crisis line')}\n"
                    f"🌍 {resources['website']}\n\n"
                    "If you're in immediate danger, please call your local emergency services right away. "
                    "You don't have to go through this alone - there are people who want to help you."
                ),
                'resources': resources,
                'priority': 'high'
            }
        elif risk_level == 1:  # Moderate risk
            return {
                'is_crisis': False,
                'message': (
                    "I can sense you're going through a really difficult time. It's important to know that "
                    "you don't have to face this alone. Consider reaching out to:\n\n"
                    f"📞 {resources['crisis_line']}: {resources['phone']}\n"
                    f"💬 {resources.get('text', 'Text your local crisis line')}\n\n"
                    "Talking to a professional can make a real difference. Would you like to continue our conversation, "
                    "or would you prefer information about finding professional support?"
                ),
                'resources': resources,
                'priority': 'moderate'
            }
        else:
            return {
                'is_crisis': False,
                'message': '',
                'resources': None,
                'priority': 'low'
            }
    
    def should_escalate(self, risk_level: int) -> bool:
        """Determine if the situation requires immediate escalation."""
        return risk_level >= 2

