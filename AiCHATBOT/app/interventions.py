"""
Supportive intervention system for mental health chatbot.
"""
from typing import Dict, List

class InterventionSystem:
    """Provides supportive interventions and resources based on screening results."""
    
    # Self-care resources
    SELF_CARE_RESOURCES = {
        'mindfulness': {
            'title': 'Mindfulness and Meditation',
            'description': 'Practices to help you stay present and reduce stress',
            'resources': [
                'Headspace app',
                'Calm app',
                'Insight Timer app',
                'Mindful.org website'
            ]
        },
        'exercise': {
            'title': 'Physical Activity',
            'description': 'Regular exercise can improve mood and reduce anxiety',
            'resources': [
                'Start with 10-15 minutes of daily walking',
                'Yoga or stretching exercises',
                'Find an activity you enjoy'
            ]
        },
        'sleep': {
            'title': 'Sleep Hygiene',
            'description': 'Good sleep is essential for mental health',
            'resources': [
                'Maintain a regular sleep schedule',
                'Create a relaxing bedtime routine',
                'Limit screen time before bed',
                'Keep your bedroom cool and dark'
            ]
        },
        'social': {
            'title': 'Social Connection',
            'description': 'Staying connected with others is important',
            'resources': [
                'Reach out to friends or family',
                'Join support groups',
                'Consider community activities',
                'Volunteer opportunities'
            ]
        }
    }
    
    # Professional resources
    PROFESSIONAL_RESOURCES = {
        'therapy': {
            'title': 'Therapy and Counseling',
            'description': 'Professional mental health support',
            'resources': [
                'Psychology Today therapist directory',
                'BetterHelp online therapy',
                'Talkspace online therapy',
                'Your insurance provider\'s network',
                'Local community mental health centers'
            ]
        },
        'crisis': {
            'title': 'Crisis Support',
            'description': 'Immediate support when you need it',
            'resources': [
                '988 Suicide & Crisis Lifeline (US)',
                'Crisis Text Line: Text HOME to 741741',
                'Your local emergency services',
                'National Suicide Prevention Lifeline'
            ]
        },
        'support_groups': {
            'title': 'Support Groups',
            'description': 'Connect with others who understand',
            'resources': [
                'NAMI (National Alliance on Mental Illness)',
                'Depression and Bipolar Support Alliance',
                'Anxiety and Depression Association of America',
                'Local support group directories'
            ]
        }
    }
    
    # Coping strategies
    COPING_STRATEGIES = {
        'anxiety': [
            'Deep breathing exercises (4-7-8 technique)',
            'Progressive muscle relaxation',
            'Grounding techniques (5-4-3-2-1 method)',
            'Challenge negative thoughts',
            'Limit caffeine and alcohol'
        ],
        'depression': [
            'Set small, achievable daily goals',
            'Maintain a routine',
            'Stay connected with others',
            'Engage in activities you used to enjoy',
            'Practice self-compassion'
        ],
        'stress': [
            'Time management techniques',
            'Learn to say no when needed',
            'Take regular breaks',
            'Practice relaxation techniques',
            'Prioritize self-care'
        ]
    }
    
    def get_interventions(self, severity: str, symptoms: List[str] = None) -> Dict:
        """
        Get personalized interventions based on severity and symptoms.
        
        Args:
            severity: Severity level from screening
            symptoms: List of reported symptoms
            
        Returns:
            Dictionary with intervention recommendations
        """
        interventions = {
            'severity': severity,
            'self_care': [],
            'professional': [],
            'coping_strategies': [],
            'resources': []
        }
        
        # Determine self-care recommendations
        if severity in ['minimal', 'mild']:
            interventions['self_care'] = [
                self.SELF_CARE_RESOURCES['mindfulness'],
                self.SELF_CARE_RESOURCES['exercise'],
                self.SELF_CARE_RESOURCES['sleep']
            ]
        elif severity in ['moderate']:
            interventions['self_care'] = [
                self.SELF_CARE_RESOURCES['mindfulness'],
                self.SELF_CARE_RESOURCES['social']
            ]
            interventions['professional'] = [
                self.PROFESSIONAL_RESOURCES['therapy']
            ]
        else:  # moderately_severe or severe
            interventions['professional'] = [
                self.PROFESSIONAL_RESOURCES['therapy'],
                self.PROFESSIONAL_RESOURCES['support_groups']
            ]
            interventions['self_care'] = [
                self.SELF_CARE_RESOURCES['sleep'],
                self.SELF_CARE_RESOURCES['social']
            ]
        
        # Add coping strategies based on symptoms
        if symptoms:
            if any('anxious' in s.lower() or 'worry' in s.lower() for s in symptoms):
                interventions['coping_strategies'].extend(self.COPING_STRATEGIES['anxiety'])
            if any('sad' in s.lower() or 'depressed' in s.lower() or 'down' in s.lower() for s in symptoms):
                interventions['coping_strategies'].extend(self.COPING_STRATEGIES['depression'])
            if any('stress' in s.lower() or 'overwhelmed' in s.lower() for s in symptoms):
                interventions['coping_strategies'].extend(self.COPING_STRATEGIES['stress'])
        
        # Add general resources
        interventions['resources'] = [
            'National Institute of Mental Health (NIMH)',
            'Mental Health America',
            'Your local community mental health center'
        ]
        
        return interventions
    
    def format_interventions(self, interventions: Dict) -> str:
        """
        Format interventions as a readable message.
        
        Args:
            interventions: Interventions dictionary
            
        Returns:
            Formatted string message
        """
        message = "Here are some supportive resources and suggestions:\n\n"
        
        if interventions.get('self_care'):
            message += "🌱 **Self-Care Strategies:**\n"
            for item in interventions['self_care']:
                message += f"- {item['title']}: {item['description']}\n"
                for resource in item['resources'][:2]:  # Limit to 2 resources
                    message += f"  • {resource}\n"
            message += "\n"
        
        if interventions.get('coping_strategies'):
            message += "💪 **Coping Strategies:**\n"
            for strategy in interventions['coping_strategies'][:5]:  # Limit to 5
                message += f"- {strategy}\n"
            message += "\n"
        
        if interventions.get('professional'):
            message += "👩‍⚕️ **Professional Support:**\n"
            for item in interventions['professional']:
                message += f"- {item['title']}: {item['description']}\n"
                for resource in item['resources'][:3]:  # Limit to 3
                    message += f"  • {resource}\n"
            message += "\n"
        
        message += (
            "Remember: These are suggestions, and what works best varies from person to person. "
            "If you're experiencing significant distress, please consider speaking with a "
            "mental health professional who can provide personalized support."
        )
        
        return message

