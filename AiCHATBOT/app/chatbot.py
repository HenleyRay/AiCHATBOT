"""
Core AI chatbot engine for mental health conversations - CLEANED VERSION
"""
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

from typing import Dict, List
import re
import traceback
from config import Config
from app.safety import SafetyDetector
from app.screening import MentalHealthScreening, ScreeningPhase

class MentalHealthChatbot:
    """Main chatbot class - simplified and cleaned."""
    
    def __init__(self):
        """Initialize the chatbot."""
        self.openai_client = None
        self.use_ollama = False
        
        # Check which AI provider to use
        if Config.AI_PROVIDER == 'ollama':
            if OLLAMA_AVAILABLE:
                try:
                    # Test if Ollama is running
                    ollama.list()
                    self.use_ollama = True
                    print("[Chatbot] Using Ollama (free local Llama)")
                except Exception as e:
                    print(f"[Chatbot] Ollama not available: {e}")
                    print("[Chatbot] Make sure Ollama is installed and running. Visit https://ollama.com")
                    self.use_ollama = False
            else:
                print("[Chatbot] Ollama package not installed. Run: pip install ollama")
        elif OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                print("[Chatbot] Using OpenAI")
            except Exception:
                self.openai_client = None
        
        self.safety_detector = SafetyDetector()
        self.screening = MentalHealthScreening()
        self.conversation_history: List[Dict] = []
        self.conversation_memory = {
            "emotion_acknowledged": False,
            "last_bot_response": None,
            # If OpenAI starts failing (e.g., insufficient quota), we can switch to offline mode
            "openai_disabled": False,
            "openai_disabled_reason": None
        }
    
    def _get_system_prompt(self) -> str:
        """Core system prompt focused on natural, supportive conversation."""
        return """You are a supportive, emotionally intelligent guide for mental health conversations.
You are NOT a therapist. You sound like a calm, caring friend who is practical and respectful.

STYLE:
- Warm, natural, non-robotic language. Vary phrasing; don't follow a rigid template.
- Keep it concise: usually 3-6 sentences.
- Validate feelings briefly, then move into practical support.
- Use gentle, everyday language (avoid clinical terms unless the user uses them).

CONTENT:
- Reference specific details the user shared (exam, work, family, relationship, sleep, etc.).
- Offer 1-3 concrete, doable suggestions (small steps).
- If you ask a question, it must be specific and necessary (max 1 question). Avoid broad probing.
- Avoid repeating empathy lines or re-asking for the cause if they already explained it.

ABSOLUTE DON'TS:
- No generic therapy prompts like: "I'm here to listen", "Tell me more", "What's on your mind?"
- No greetings once the conversation has started.
- Don't lecture, diagnose, or promise outcomes.

EXAMPLES (tone + specificity):
User: "I'm sad because I failed my exam"
Good: "That’s a heavy hit, especially when you put effort into it. Failing one exam doesn’t mean you’re not capable—it usually means the approach needs adjusting. If you can, take 20 minutes to decompress, then do a quick review: what topics cost you the most points? Pick one small change for next time (practice questions, study group, office hours). This feels awful now, but it’s something you can recover from."

User: "I've been feeling this a while"
Good: "When it’s been hanging around for a while, it can start to feel like your normal—which is exhausting. Since you mentioned the exam earlier, it might help to make a simple plan for this week: one small study block, one rest block, and one check-in with a teacher or friend. You don’t have to fix everything at once; you just need one next step."""
    
    def _detect_cause_known(self, user_message: str) -> bool:
        """Check if user already explained the cause."""
        # Check current + last 5 messages
        texts = [user_message.lower()]
        for exchange in self.conversation_history[-5:]:
            prev = exchange.get("user_message", "").lower()
            if prev:
                texts.append(prev)
        
        combined = " ".join(texts)
        
        # Causal markers
        if any(m in combined for m in ["because", "since", "due to", "reason is", "the reason"]):
            return True
        
        # Cause keywords
        cause_words = ["failed", "exam", "test", "school", "work", "job", "relationship", 
                      "family", "breakup", "money", "stress", "pressure"]
        
        return any(word in combined for word in cause_words)
    
    def _check_emotion_acknowledged(self) -> bool:
        """Check if emotion was already acknowledged."""
        if not self.conversation_memory["emotion_acknowledged"]:
            return False
        
        # Check if bot already responded with empathy
        if len(self.conversation_history) > 0:
            last_response = self.conversation_history[-1].get("bot_response", "").lower()
            empathy_words = ["sorry", "understand", "hear", "feel", "sounds", "difficult"]
            if any(word in last_response for word in empathy_words):
                return True
        
        return False
    
    def _update_memory(self, user_message: str):
        """Update conversation memory."""
        message_lower = user_message.lower()
        
        # Check for emotion
        emotion_words = ["sad", "down", "depressed", "stressed", "anxious", "worried", 
                        "overwhelmed", "upset", "angry", "tired"]
        if any(word in message_lower for word in emotion_words):
            self.conversation_memory["emotion_acknowledged"] = True
        
        # Check for cause explanation
        if self._detect_cause_known(user_message):
            self.conversation_memory["emotion_acknowledged"] = True
    
    def _extract_user_context(self) -> str:
        """Extract key context from conversation for better responses."""
        if not self.conversation_history:
            return ""
        
        # Collect key facts from conversation
        facts = []
        all_user_messages = " ".join([
            exchange.get('user_message', '') 
            for exchange in self.conversation_history[-5:]
        ]).lower()
        
        if 'exam' in all_user_messages or 'failed' in all_user_messages:
            facts.append("User failed an exam")
        if 'school' in all_user_messages or 'college' in all_user_messages:
            facts.append("User is a student")
        if 'work' in all_user_messages or 'job' in all_user_messages:
            facts.append("User mentioned work")
        if 'family' in all_user_messages or 'parents' in all_user_messages:
            facts.append("User mentioned family")
        
        return ", ".join(facts) if facts else ""
    
    def _build_context_prompt(self, user_message: str) -> str:
        """Build enhanced context prompt with specific instructions."""
        cause_known = self._detect_cause_known(user_message)
        emotion_acknowledged = self._check_emotion_acknowledged()
        is_ongoing = len(self.conversation_history) > 0
        user_context = self._extract_user_context()
        
        prompt = self._get_system_prompt()
        
        # Add specific context
        prompt += "\n\n=== CURRENT SITUATION ===\n"
        prompt += f"User context: {user_context if user_context else 'New conversation'}\n"
        prompt += f"Cause already explained: {cause_known}\n"
        prompt += f"Emotion already acknowledged: {emotion_acknowledged}\n"
        prompt += f"Conversation in progress: {is_ongoing}\n"
        
        # STRONG rules based on context
        if cause_known:
            prompt += "\n🚫 CRITICAL: User ALREADY explained the cause. DO NOT ask 'what happened' or 'what's going on'. Reference what they said and give advice.\n"
        
        if emotion_acknowledged:
            prompt += "\n🚫 CRITICAL: Emotion was ALREADY acknowledged. DO NOT say 'I'm sorry you're feeling...' again. Skip to practical advice.\n"
        
        if is_ongoing:
            prompt += "\n🚫 CRITICAL: This is an ONGOING conversation. DO NOT greet. DO NOT say 'Hello' or 'Hi there'. Continue naturally.\n"
        
        # Reference what user said
        if len(self.conversation_history) > 0:
            recent_user_messages = [
                exchange.get('user_message', '') 
                for exchange in self.conversation_history[-3:]
            ]
            if recent_user_messages:
                prompt += f"\n📝 What user already shared: {' | '.join(recent_user_messages[-2:])}\n"
                prompt += "Reference these specific details in your response.\n"
        
        # Prevent repetition
        if self.conversation_memory["last_bot_response"]:
            last = self.conversation_memory["last_bot_response"][:100]
            prompt += f"\n🚫 DO NOT REPEAT: Your last response was '{last}...'\n"
            prompt += "This response must be DIFFERENT - use different words, different advice, different angle.\n"
        
        return prompt
    
    def _clean_response(self, response: str, cause_known: bool) -> str:
        """Clean response - remove low-quality filler without breaking natural language."""
        if not response:
            return response
        
        # Note: use word boundaries to avoid accidental matches (e.g. "this" contains "hi")
        banned_phrase_patterns = [
            r"\bcan you tell me more\b",
            r"\btell me more\b",
            r"\bwhat's on your mind\b",
            r"\bwhat happened\b",
            r"\bwhat's been going on\b",
            r"\bwhat's going on\b",
            r"\bwhat's happening\b",
            r"\bi'm here to listen\b",
            r"\bwould you like to talk\b",
            r"\bcan you share\b",
            r"\bi want to understand\b",
            r"\bi want to make sure i understand\b",
        ]

        banned_question_patterns = [
            r"\bcan you tell me more\b\??",
            r"\btell me more\b\??",
            r"\bwhat happened\b\??",
            r"\bwhat's going on\b\??",
            r"\bwhat's happening\b\??",
            r"\bwhat's been going on\b\??",
            r"\bwhat's on your mind\b\??",
        ]
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', response)
        cleaned = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_lower = sentence.lower()
            should_remove = False
            
            # Drop obvious filler / therapy-prompt phrases
            for pat in banned_phrase_patterns:
                if re.search(pat, sentence_lower, flags=re.IGNORECASE):
                    should_remove = True
                    break

            # Drop greeting-only sentences in ongoing conversations (use word boundaries; avoid substring bugs)
            if not should_remove and len(self.conversation_history) > 0:
                if re.match(r"^(hi|hello|hey)\b", sentence_lower):
                    should_remove = True
                if re.search(r"\bi'm glad you're here\b", sentence_lower):
                    should_remove = True
                if re.search(r"\bhow are you doing\b", sentence_lower) or re.search(r"\bhow are things going\b", sentence_lower):
                    should_remove = True
            
            # If cause is known, remove broad probing questions specifically (not all questions)
            if not should_remove and cause_known and "?" in sentence:
                for pat in banned_question_patterns:
                    if re.search(pat, sentence_lower, flags=re.IGNORECASE):
                        should_remove = True
                        break
            
            if not should_remove:
                cleaned.append(sentence)
        
        result = " ".join(cleaned).strip()
        
        # If everything was removed, try to salvage something
        if not result:
            # Remove banned phrases from original but keep structure
            result = response
            for pat in banned_phrase_patterns:
                result = re.sub(pat, "", result, flags=re.IGNORECASE)
            result = re.sub(r'\s+', ' ', result).strip()
        
        # If cause is known, don't forcefully strip all questions; the prompt should do most of the work.
        
        # Clean up extra whitespace
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result if result else response

    def _generate_ollama_response(self, user_message: str) -> str:
        """Generate AI response using Ollama (free local Llama)."""
        try:
            # Update memory
            self._update_memory(user_message)
            
            # Build messages for Ollama (similar format to OpenAI)
            messages = []
            
            # Add system prompt
            system_prompt = self._build_context_prompt(user_message)
            messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history (last 6 exchanges)
            for exchange in self.conversation_history[-6:]:
                user_msg = exchange.get('user_message', '').strip()
                bot_msg = exchange.get('bot_response', '').strip()
                if user_msg:
                    messages.append({"role": "user", "content": user_msg})
                if bot_msg:
                    messages.append({"role": "assistant", "content": bot_msg})
            
            # Add current message
            messages.append({"role": "user", "content": user_message.strip()})
            
            # Generate response using Ollama
            response = ollama.chat(
                model=Config.AI_MODEL,  # e.g., "llama3.2", "llama3.1", "llama3"
                messages=messages,
                options={
                    "temperature": Config.AI_TEMPERATURE,
                    "num_predict": Config.MAX_TOKENS,  # Ollama uses num_predict instead of max_tokens
                    "top_p": 0.9,
                }
            )
            
            ai_response = response['message']['content'].strip()
            
            # If response is empty or too short, regenerate
            if len(ai_response) < 20:
                messages[0]["content"] += "\n\n⚠️ Your response was too short. Provide a complete, helpful response (3-5 sentences)."
                response = ollama.chat(
                    model=Config.AI_MODEL,
                    messages=messages,
                    options={
                        "temperature": Config.AI_TEMPERATURE,
                        "num_predict": Config.MAX_TOKENS,
                        "top_p": 0.9,
                    }
                )
                ai_response = response['message']['content'].strip()
            
            # Clean response
            cause_known = self._detect_cause_known(user_message)
            ai_response = self._clean_response(ai_response, cause_known)
            
            # Update memory
            self.conversation_memory["last_bot_response"] = ai_response
            
            # Store in history
            self.conversation_history.append({
                'user_message': user_message,
                'bot_response': ai_response
            })
            
            # Limit history
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return ai_response
        
        except Exception as e:
            print("\n[Chatbot] Ollama call failed; falling back to offline response.")
            print(f"[Chatbot] Error type: {type(e).__name__}")
            print(f"[Chatbot] Error: {str(e)}")
            traceback.print_exc()
            
            # If Ollama fails, fall back to offline mode
            fallback = self._generate_fallback_response(user_message)
            self._update_memory(user_message)
            self.conversation_memory["last_bot_response"] = fallback
            self.conversation_history.append({'user_message': user_message, 'bot_response': fallback})
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            return fallback

    def _generate_fallback_response(self, user_message: str) -> str:
        """
        Generate a simple, natural-sounding response when OpenAI isn't configured.
        This keeps the app usable without an API key.
        """
        msg = (user_message or "").strip()
        msg_l = msg.lower()

        context = (self._extract_user_context() or "").lower()
        context_hint = ""
        if "failed an exam" in context or "student" in context:
            context_hint = "Since you mentioned school earlier, "
        elif "work" in context:
            context_hint = "Since you mentioned work earlier, "
        elif "family" in context:
            context_hint = "Since you mentioned family earlier, "

        # Very lightweight topic detection
        anxious = any(w in msg_l for w in ["anxious", "panic", "worried", "overthinking", "nervous"])
        sad = any(w in msg_l for w in ["sad", "down", "depressed", "empty", "hopeless"])
        stress = any(w in msg_l for w in ["stressed", "overwhelmed", "burnt out", "pressure", "stress"])
        sleep = any(w in msg_l for w in ["sleep", "insomnia", "can't sleep", "tired", "exhausted"])

        # Build a short supportive reply
        opening = "That sounds really tough." if (anxious or sad or stress) else "I hear you."
        if "exam" in msg_l or "test" in msg_l:
            middle = "If this is about school pressure, try to focus on one small next step you can control today."
            tip = "A good start is a 15-minute reset (water + stretch), then pick one topic to review or one task to finish."
        elif sleep:
            middle = "Sleep issues can make everything feel heavier, even when the situation hasn’t changed."
            tip = "If you can, try a simple wind-down: dim lights, put your phone away for 20 minutes, and do slow breathing (inhale 4, exhale 6) for 5 rounds."
        elif anxious:
            middle = "When anxiety spikes, your body can stay on high alert."
            tip = "Try grounding: name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste—then take one slow breath."
        elif sad:
            middle = "When you’re feeling low, it’s easy for your mind to turn everything into proof that you’re failing."
            tip = "Pick one tiny “care task” right now (shower, snack, short walk, text one person). Small actions can shift momentum."
        elif stress:
            middle = "When you’re overloaded, clarity usually comes after you reduce the pile a little."
            tip = "Write down the top 3 things on your mind, circle the one you can influence today, and do the first 5 minutes of it—just to start."
        else:
            middle = "We can take this one step at a time."
            tip = "If it helps, try writing a 2-sentence summary: what’s happening + what you need most right now (rest, support, a plan, space)."

        closing = "You don’t have to handle this perfectly—just keep it small and doable."

        reply = f"{opening} {context_hint}{middle} {tip} {closing}"
        reply = re.sub(r"\s+", " ", reply).strip()
        return reply
    
    def _generate_ai_response(self, user_message: str) -> str:
        """Generate AI response using Ollama or OpenAI."""
        if self.conversation_memory.get("openai_disabled"):
            # Keep memory behavior consistent even if we disable OpenAI mid-session
            self._update_memory(user_message)
            ai_response = self._generate_fallback_response(user_message)
            self.conversation_memory["last_bot_response"] = ai_response
            self.conversation_history.append({'user_message': user_message, 'bot_response': ai_response})
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            return ai_response

        # Use Ollama if configured
        if self.use_ollama:
            return self._generate_ollama_response(user_message)
        
        # Fall back to OpenAI if available
        if not self.openai_client or not Config.OPENAI_API_KEY:
            # Keep memory behavior consistent even without OpenAI
            self._update_memory(user_message)
            ai_response = self._generate_fallback_response(user_message)
            self.conversation_memory["last_bot_response"] = ai_response
            self.conversation_history.append({'user_message': user_message, 'bot_response': ai_response})
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            return ai_response
        
        try:
            # Update memory
            self._update_memory(user_message)
            
            # Build messages
            messages = [{"role": "system", "content": self._build_context_prompt(user_message)}]
            
            # Add conversation history (last 3 exchanges for faster API calls)
            # Format: user -> assistant pairs to maintain context
            for exchange in self.conversation_history[-3:]:
                user_msg = exchange.get('user_message', '').strip()
                bot_msg = exchange.get('bot_response', '').strip()
                if user_msg:
                    messages.append({"role": "user", "content": user_msg})
                if bot_msg:
                    messages.append({"role": "assistant", "content": bot_msg})
            
            # Add current message
            messages.append({"role": "user", "content": user_message.strip()})
            
            # Generate response with optimized parameters
            response = self.openai_client.chat.completions.create(
                model=Config.AI_MODEL,
                messages=messages,
                temperature=Config.AI_TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
                top_p=0.9,  # Nucleus sampling for better quality
                frequency_penalty=0.3,  # Reduce repetition
                presence_penalty=0.3  # Encourage new topics
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Clean response
            cause_known = self._detect_cause_known(user_message)
            ai_response = self._clean_response(ai_response, cause_known)
            
            # Update memory
            self.conversation_memory["last_bot_response"] = ai_response
            
            # Store in history
            self.conversation_history.append({
                'user_message': user_message,
                'bot_response': ai_response
            })
            
            # Limit history to last 15 exchanges to keep memory manageable
            if len(self.conversation_history) > 15:
                self.conversation_history = self.conversation_history[-15:]
            
            return ai_response
        
        except Exception as e:
            # Log the real error so it can be fixed (model access, auth, network, etc.)
            print("\n[Chatbot] OpenAI call failed; falling back to offline response.")
            print(f"[Chatbot] Error type: {type(e).__name__}")
            print(f"[Chatbot] Error: {str(e)}")
            traceback.print_exc()

            # Graceful fallback so the user doesn't see a dead-end message.
            fallback = self._generate_fallback_response(user_message)

            # If quota/billing is exhausted, disable OpenAI for this session to avoid repeated failures.
            err_text = str(e).lower()
            if "insufficient_quota" in err_text or "exceeded your current quota" in err_text:
                self.conversation_memory["openai_disabled"] = True
                self.conversation_memory["openai_disabled_reason"] = "insufficient_quota"
                prefix = (
                    "Your OpenAI API key is currently out of quota/billing, so I can’t use the online AI right now. "
                    "You can fix this by adding billing on your OpenAI account or using a different API key.\n\n"
                    "For now, I can still support you in offline mode:\n\n"
                )
            else:
                prefix = (
                    "I’m having a temporary issue connecting to the AI right now, "
                    "but I can still support you.\n\n"
                )

            fallback = prefix + fallback
            self.conversation_memory["last_bot_response"] = fallback
            self.conversation_history.append({'user_message': user_message, 'bot_response': fallback})
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            return fallback
    
    def process_message(self, user_message: str, session_id: str = 'default') -> Dict:
        """Process user message - main entry point."""
        # Safety check
        is_crisis, risk_level, _ = self.safety_detector.detect_crisis(user_message)
        
        if is_crisis and risk_level >= 2:
            crisis_response = self.safety_detector.get_crisis_response(risk_level)
            return {
                'response': crisis_response['message'],
                'is_crisis': True,
                'risk_level': risk_level,
                'screening_status': None,
                'suggestions': []
            }
        
        # Check screening
        if self.screening.current_phase == ScreeningPhase.IN_PROGRESS:
            screening_result = self.screening.process_response(user_message)
            if screening_result.get('status') == 'completed':
                interpretation = screening_result.get('interpretation', '')
                return {
                    'response': f"Thank you for completing the screening. {interpretation}",
                    'is_crisis': False,
                    'risk_level': 0,
                    'screening_status': 'completed',
                    'screening_result': screening_result
                }
            else:
                question = screening_result.get('question', '')
                progress = screening_result.get('progress', '')
                return {
                    'response': f"Question {progress}:\n{question}",
                    'is_crisis': False,
                    'risk_level': 0,
                    'screening_status': 'in_progress'
                }
        
        # Check if wants screening
        if self._wants_screening(user_message):
            screening_start = self.screening.start_screening('phq9')
            return {
                'response': f"{screening_start['instructions']}\n\n{screening_start['question']}",
                'is_crisis': False,
                'risk_level': 0,
                'screening_status': 'started'
            }
        
        # Generate AI response
        ai_response = self._generate_ai_response(user_message)
        
        return {
            'response': ai_response,
            'is_crisis': False,
            'risk_level': 0,
            'screening_status': None,
            'suggestions': []
        }
    
    def _wants_screening(self, message: str) -> bool:
        """Check if user wants screening."""
        message_lower = message.lower()
        # Avoid overly broad triggers like "test" (e.g., "I have a test tomorrow").
        # Use explicit screening language instead.
        keywords = [
            'screening', 'assessment', 'questionnaire',
            'phq9', 'phq-9', 'phq',
            'gad7', 'gad-7', 'gad',
            'depression screening', 'anxiety screening',
            'depression test', 'anxiety test',
            'evaluate my depression', 'evaluate my anxiety'
        ]
        return any(kw in message_lower for kw in keywords)
    
    def reset_conversation(self):
        """Reset conversation."""
        self.conversation_history = []
        self.screening.reset()
        self.conversation_memory = {
            "emotion_acknowledged": False,
            "last_bot_response": None,
            "openai_disabled": False,
            "openai_disabled_reason": None
        }
    
    def get_conversation_summary(self) -> Dict:
        """Get conversation summary."""
        return {
            'message_count': len(self.conversation_history),
            'screening_status': self.screening.get_current_status()
        }

