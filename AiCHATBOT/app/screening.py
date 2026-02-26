"""
Mental health screening questionnaire system.
"""
from typing import Dict
from enum import Enum

class ScreeningPhase(Enum):
    """Phases of the screening process."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class MentalHealthScreening:
    """Manages mental health screening questionnaires."""
    
    # PHQ-9 (Patient Health Questionnaire) - Depression screening
    PHQ9_QUESTIONS = [
        "Over the last 2 weeks, how often have you been bothered by little interest or pleasure in doing things?",
        "Over the last 2 weeks, how often have you been bothered by feeling down, depressed, or hopeless?",
        "Over the last 2 weeks, how often have you had trouble falling or staying asleep, or sleeping too much?",
        "Over the last 2 weeks, how often have you been bothered by feeling tired or having little energy?",
        "Over the last 2 weeks, how often have you been bothered by poor appetite or overeating?",
        "Over the last 2 weeks, how often have you been bothered by feeling bad about yourself or that you are a failure?",
        "Over the last 2 weeks, how often have you been bothered by trouble concentrating on things?",
        "Over the last 2 weeks, how often have you been bothered by moving or speaking so slowly that other people could have noticed, or being so fidgety or restless that you have been moving around a lot more than usual?",
        "Over the last 2 weeks, how often have you been bothered by thoughts that you would be better off dead or of hurting yourself?"
    ]
    
    # GAD-7 (Generalized Anxiety Disorder) - Anxiety screening
    GAD7_QUESTIONS = [
        "Over the last 2 weeks, how often have you been bothered by feeling nervous, anxious, or on edge?",
        "Over the last 2 weeks, how often have you been bothered by not being able to stop or control worrying?",
        "Over the last 2 weeks, how often have you been bothered by worrying too much about different things?",
        "Over the last 2 weeks, how often have you been bothered by trouble relaxing?",
        "Over the last 2 weeks, how often have you been bothered by being so restless that it is hard to sit still?",
        "Over the last 2 weeks, how often have you been bothered by becoming easily annoyed or irritable?",
        "Over the last 2 weeks, how often have you been bothered by feeling afraid, as if something awful might happen?"
    ]
    
    # Response options (0-3 scale)
    RESPONSE_OPTIONS = [
        "Not at all (0)",
        "Several days (1)",
        "More than half the days (2)",
        "Nearly every day (3)"
    ]
    
    def __init__(self):
        """Initialize the screening system."""
        self.current_phase = ScreeningPhase.NOT_STARTED
        self.current_questionnaire = None
        self.current_question_index = 0
        self.responses = {}
        self.scores = {}
    
    def start_screening(self, questionnaire_type: str = 'phq9') -> Dict:
        """
        Start a new screening questionnaire.
        
        Args:
            questionnaire_type: Type of questionnaire ('phq9' or 'gad7')
            
        Returns:
            Dictionary with first question and instructions
        """
        self.current_phase = ScreeningPhase.IN_PROGRESS
        self.current_questionnaire = questionnaire_type
        self.current_question_index = 0
        self.responses = {}
        
        if questionnaire_type == 'phq9':
            questions = self.PHQ9_QUESTIONS
            title = "Depression Screening (PHQ-9)"
        elif questionnaire_type == 'gad7':
            questions = self.GAD7_QUESTIONS
            title = "Anxiety Screening (GAD-7)"
        else:
            questions = self.PHQ9_QUESTIONS
            title = "Mental Health Screening"
        
        return {
            'questionnaire': questionnaire_type,
            'title': title,
            'question': questions[0],
            'question_number': 1,
            'total_questions': len(questions),
            'response_options': self.RESPONSE_OPTIONS,
            'instructions': (
                "I'll ask you a series of questions. For each one, please let me know how often "
                "you've experienced this over the last 2 weeks. You can answer with:\n"
                "- 'Not at all' or '0'\n"
                "- 'Several days' or '1'\n"
                "- 'More than half the days' or '2'\n"
                "- 'Nearly every day' or '3'\n\n"
                "You can also describe your experience in your own words, and I'll understand."
            )
        }
    
    def process_response(self, user_response: str) -> Dict:
        """
        Process a user's response to a screening question.
        
        Args:
            user_response: User's answer to the current question
            
        Returns:
            Dictionary with next question or completion status
        """
        if self.current_phase != ScreeningPhase.IN_PROGRESS:
            return {'error': 'No screening in progress'}
        
        # Extract score from response
        score = self._extract_score(user_response)
        
        # Store response
        question_key = f"{self.current_questionnaire}_q{self.current_question_index}"
        self.responses[question_key] = {
            'score': score,
            'raw_response': user_response
        }
        
        # Get questions for current questionnaire
        if self.current_questionnaire == 'phq9':
            questions = self.PHQ9_QUESTIONS
        elif self.current_questionnaire == 'gad7':
            questions = self.GAD7_QUESTIONS
        else:
            questions = self.PHQ9_QUESTIONS
        
        # Move to next question
        self.current_question_index += 1
        
        # Check if screening is complete
        if self.current_question_index >= len(questions):
            return self._complete_screening()
        
        # Return next question
        return {
            'question': questions[self.current_question_index],
            'question_number': self.current_question_index + 1,
            'total_questions': len(questions),
            'response_options': self.RESPONSE_OPTIONS,
            'progress': f"{self.current_question_index + 1}/{len(questions)}"
        }
    
    def _extract_score(self, response: str) -> int:
        """
        Extract numerical score from user's text response.
        
        Args:
            response: User's text response
            
        Returns:
            Score from 0-3
        """
        response_lower = response.lower()
        
        # Check for explicit numbers
        if '0' in response or 'not at all' in response_lower or 'never' in response_lower:
            return 0
        elif '1' in response or 'several days' in response_lower or 'sometimes' in response_lower:
            return 1
        elif '2' in response or 'more than half' in response_lower or 'often' in response_lower:
            return 2
        elif '3' in response or 'nearly every day' in response_lower or 'always' in response_lower or 'every day' in response_lower:
            return 3
        
        # Default to middle score if unclear
        return 1
    
    def _complete_screening(self) -> Dict:
        """Complete the screening and calculate scores."""
        self.current_phase = ScreeningPhase.COMPLETED
        
        # Calculate total score
        total_score = sum(
            resp['score'] for resp in self.responses.values()
            if resp['score'] is not None
        )
        
        # Store score
        self.scores[self.current_questionnaire] = total_score
        
        # Determine severity
        severity = self._determine_severity(total_score, self.current_questionnaire)
        
        return {
            'status': 'completed',
            'questionnaire': self.current_questionnaire,
            'total_score': total_score,
            'severity': severity,
            'interpretation': self._get_interpretation(total_score, self.current_questionnaire)
        }
    
    def _determine_severity(self, score: int, questionnaire: str) -> str:
        """Determine severity level based on score."""
        if questionnaire == 'phq9':
            if score <= 4:
                return 'minimal'
            elif score <= 9:
                return 'mild'
            elif score <= 14:
                return 'moderate'
            elif score <= 19:
                return 'moderately_severe'
            else:
                return 'severe'
        elif questionnaire == 'gad7':
            if score <= 4:
                return 'minimal'
            elif score <= 9:
                return 'mild'
            elif score <= 14:
                return 'moderate'
            else:
                return 'severe'
        return 'unknown'
    
    def _get_interpretation(self, score: int, questionnaire: str) -> str:
        """Get interpretation text for the score."""
        severity = self._determine_severity(score, questionnaire)
        
        interpretations = {
            'phq9': {
                'minimal': 'Your responses suggest minimal or no depression symptoms.',
                'mild': 'Your responses suggest mild depression symptoms. Consider self-care strategies and monitoring.',
                'moderate': 'Your responses suggest moderate depression symptoms. Professional support may be beneficial.',
                'moderately_severe': 'Your responses suggest moderately severe depression symptoms. Professional support is recommended.',
                'severe': 'Your responses suggest severe depression symptoms. Professional support is strongly recommended.'
            },
            'gad7': {
                'minimal': 'Your responses suggest minimal or no anxiety symptoms.',
                'mild': 'Your responses suggest mild anxiety symptoms. Consider stress management techniques.',
                'moderate': 'Your responses suggest moderate anxiety symptoms. Professional support may be beneficial.',
                'severe': 'Your responses suggest severe anxiety symptoms. Professional support is recommended.'
            }
        }
        
        return interpretations.get(questionnaire, {}).get(severity, 'Please consult with a healthcare professional.')
    
    def get_current_status(self) -> Dict:
        """Get current screening status."""
        return {
            'phase': self.current_phase.value,
            'questionnaire': self.current_questionnaire,
            'current_question': self.current_question_index,
            'scores': self.scores
        }
    
    def reset(self):
        """Reset the screening system."""
        self.current_phase = ScreeningPhase.NOT_STARTED
        self.current_questionnaire = None
        self.current_question_index = 0
        self.responses = {}
        self.scores = {}

