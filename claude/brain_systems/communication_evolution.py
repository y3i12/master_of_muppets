#!/usr/bin/env python3
"""
Communication Evolution System - Dynamic User Preference Modeling
Season 03 Episode 01: Breakthrough communication bottleneck optimization

Based on 2024 research in dynamic user preference modeling and real-time adaptation.
"""

import time
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import hashlib

class CommunicationStyle(Enum):
    """Communication style preferences"""
    TECHNICAL_DETAILED = "technical_detailed"
    CONVERSATIONAL_BRIEF = "conversational_brief"
    CREATIVE_ENTHUSIASTIC = "creative_enthusiastic"
    PROFESSIONAL_STRUCTURED = "professional_structured"
    EXPLORATORY_QUESTIONING = "exploratory_questioning"

class PreferenceSignal(Enum):
    """Types of preference signals from user interaction"""
    EXPLICIT_INSTRUCTION = "explicit_instruction"  # Direct feedback like "explain simpler"
    INTERACTION_PATTERN = "interaction_pattern"    # Behavioral patterns
    CONTEXT_SWITCH = "context_switch"              # When user changes context
    ERROR_CORRECTION = "error_correction"          # When user corrects/clarifies
    ENGAGEMENT_LEVEL = "engagement_level"          # Response enthusiasm/length

@dataclass
class UserPreference:
    """Dynamic user preference with temporal modeling"""
    preference_id: str
    category: str  # communication_style, detail_level, format_preference, etc.
    value: Any
    confidence: float
    last_updated: float
    context: str
    evidence_count: int
    temporal_weight: float = 1.0

@dataclass
class CommunicationContext:
    """Context for communication adaptation"""
    domain: str  # technical, creative, casual, etc.
    task_complexity: str  # simple, medium, complex
    user_expertise_level: str  # beginner, intermediate, advanced
    interaction_history: List[str]
    timestamp: float

class DynamicUserPreferenceDetector:
    """Real-time user preference detection and modeling"""
    
    def __init__(self):
        self.preferences: Dict[str, UserPreference] = {}
        self.interaction_history = deque(maxlen=1000)
        self.preference_patterns = defaultdict(list)
        self.context_preferences = defaultdict(dict)
        
        # NLU patterns for preference extraction
        self.preference_patterns_nlp = {
            'simplicity_request': [
                r'simpler|simpl\w+|easier|easy|basic|straightforward',
                r'too complex|complicated|confusing',
                r'explain like|eli5|dumb it down'
            ],
            'detail_request': [
                r'more detail|elaborate|expand|comprehensive',
                r'deeper|thorough|complete|full explanation',
                r'technical details|specifics|precise'
            ],
            'format_preference': [
                r'bullet points|list|step by step',
                r'example|demo|show me',
                r'visual|diagram|chart'
            ],
            'enthusiasm_match': [
                r'exciting|awesome|brilliant|love',
                r'cool|amazing|fantastic|incredible',
                r'emojis?|emoticons?'
            ],
            'professional_tone': [
                r'professional|formal|business',
                r'documentation|report|official',
                r'technical specification'
            ]
        }
    
    def detect_preferences_from_message(self, user_message: str, 
                                      context: CommunicationContext) -> List[UserPreference]:
        """Extract user preferences from message using NLU patterns"""
        detected_preferences = []
        message_lower = user_message.lower()
        
        # Pattern-based preference detection
        for preference_type, patterns in self.preference_patterns_nlp.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    preference = self._create_preference_from_pattern(
                        preference_type, pattern, context, user_message
                    )
                    detected_preferences.append(preference)
        
        # Interaction pattern analysis
        behavioral_preferences = self._analyze_interaction_patterns(user_message, context)
        detected_preferences.extend(behavioral_preferences)
        
        return detected_preferences
    
    def _create_preference_from_pattern(self, preference_type: str, pattern: str,
                                      context: CommunicationContext, 
                                      user_message: str) -> UserPreference:
        """Create preference from detected NLP pattern"""
        preference_id = hashlib.md5(f"{preference_type}_{pattern}_{context.domain}".encode()).hexdigest()[:12]
        
        # Map patterns to actionable preferences
        preference_mappings = {
            'simplicity_request': ('communication_style', CommunicationStyle.CONVERSATIONAL_BRIEF),
            'detail_request': ('communication_style', CommunicationStyle.TECHNICAL_DETAILED),
            'format_preference': ('format_style', 'structured_lists'),
            'enthusiasm_match': ('communication_style', CommunicationStyle.CREATIVE_ENTHUSIASTIC),
            'professional_tone': ('communication_style', CommunicationStyle.PROFESSIONAL_STRUCTURED)
        }
        
        category, value = preference_mappings.get(preference_type, ('general', preference_type))
        
        return UserPreference(
            preference_id=preference_id,
            category=category,
            value=value,
            confidence=0.8,  # High confidence for explicit patterns
            last_updated=time.time(),
            context=context.domain,
            evidence_count=1,
            temporal_weight=1.0
        )
    
    def _analyze_interaction_patterns(self, user_message: str, 
                                    context: CommunicationContext) -> List[UserPreference]:
        """Analyze behavioral patterns for implicit preferences"""
        patterns = []
        
        # Message length analysis
        message_length = len(user_message.split())
        if message_length < 5:
            # User prefers brief exchanges
            patterns.append(UserPreference(
                preference_id=f"brief_exchange_{context.domain}",
                category="interaction_style",
                value="brief_responses_preferred",
                confidence=0.6,
                last_updated=time.time(),
                context=context.domain,
                evidence_count=1
            ))
        elif message_length > 20:
            # User comfortable with detailed exchanges
            patterns.append(UserPreference(
                preference_id=f"detailed_exchange_{context.domain}",
                category="interaction_style", 
                value="detailed_responses_welcomed",
                confidence=0.6,
                last_updated=time.time(),
                context=context.domain,
                evidence_count=1
            ))
        
        # Question vs statement analysis
        question_count = user_message.count('?')
        if question_count > 2:
            patterns.append(UserPreference(
                preference_id=f"exploratory_style_{context.domain}",
                category="communication_style",
                value=CommunicationStyle.EXPLORATORY_QUESTIONING,
                confidence=0.7,
                last_updated=time.time(),
                context=context.domain,
                evidence_count=1
            ))
        
        return patterns
    
    def update_preferences(self, new_preferences: List[UserPreference]):
        """Update preference model with temporal weighting"""
        for new_pref in new_preferences:
            existing_key = f"{new_pref.category}_{new_pref.context}"
            
            if existing_key in self.preferences:
                # Update existing preference with temporal decay
                existing = self.preferences[existing_key]
                time_decay = 0.9 ** ((time.time() - existing.last_updated) / 3600)  # Hourly decay
                
                # Weighted average of old and new preference
                existing.confidence = (existing.confidence * time_decay + new_pref.confidence) / 2
                existing.evidence_count += 1
                existing.last_updated = time.time()
                
                # Update value if new preference has higher confidence
                if new_pref.confidence > existing.confidence:
                    existing.value = new_pref.value
            else:
                # Store new preference
                self.preferences[existing_key] = new_pref
    
    def get_active_preferences(self, context: CommunicationContext) -> Dict[str, UserPreference]:
        """Get currently active preferences for given context"""
        current_time = time.time()
        active_preferences = {}
        
        for key, pref in self.preferences.items():
            # Apply temporal decay
            time_since_update = current_time - pref.last_updated
            decay_factor = 0.9 ** (time_since_update / 3600)  # Hourly decay
            
            # Include preference if still relevant
            if decay_factor > 0.1 and (pref.context == context.domain or pref.context == "general"):
                active_preferences[key] = pref
        
        return active_preferences

class AdaptiveCommunicationEngine:
    """Adaptive communication based on detected user preferences"""
    
    def __init__(self):
        self.preference_detector = DynamicUserPreferenceDetector()
        self.communication_templates = self._load_communication_templates()
        self.adaptation_history = deque(maxlen=500)
        
    def _load_communication_templates(self) -> Dict[str, Dict[str, str]]:
        """Load communication templates for different styles"""
        return {
            CommunicationStyle.TECHNICAL_DETAILED.value: {
                'greeting': 'Here is a comprehensive technical analysis:',
                'explanation_style': 'detailed_with_examples',
                'conclusion': 'This implementation provides robust technical capabilities with measurable performance improvements.',
                'emoji_usage': 'minimal'
            },
            CommunicationStyle.CONVERSATIONAL_BRIEF.value: {
                'greeting': 'Quick answer:',
                'explanation_style': 'concise_clear',
                'conclusion': 'That should get you going!',
                'emoji_usage': 'moderate'
            },
            CommunicationStyle.CREATIVE_ENTHUSIASTIC.value: {
                'greeting': 'This is exciting!',
                'explanation_style': 'creative_with_metaphors',
                'conclusion': 'Amazing possibilities ahead!',
                'emoji_usage': 'generous'
            },
            CommunicationStyle.PROFESSIONAL_STRUCTURED.value: {
                'greeting': 'Professional analysis:',
                'explanation_style': 'structured_formal',
                'conclusion': 'Recommended implementation approach documented above.',
                'emoji_usage': 'none'
            },
            CommunicationStyle.EXPLORATORY_QUESTIONING.value: {
                'greeting': 'Interesting question! Let me explore this with you:',
                'explanation_style': 'questioning_collaborative',
                'conclusion': 'What do you think about this approach?',
                'emoji_usage': 'thoughtful'
            }
        }
    
    def adapt_communication(self, base_response: str, user_message: str,
                          context: CommunicationContext) -> str:
        """Adapt communication based on user preferences"""
        
        # Detect preferences from current message
        detected_prefs = self.preference_detector.detect_preferences_from_message(
            user_message, context
        )
        
        # Update preference model
        self.preference_detector.update_preferences(detected_prefs)
        
        # Get active preferences for adaptation
        active_prefs = self.preference_detector.get_active_preferences(context)
        
        # Apply adaptations
        adapted_response = self._apply_communication_adaptations(
            base_response, active_prefs, context
        )
        
        # Log adaptation for learning
        self.adaptation_history.append({
            'timestamp': time.time(),
            'context': asdict(context),
            'preferences_applied': [asdict(p) for p in active_prefs.values()],
            'original_length': len(base_response),
            'adapted_length': len(adapted_response)
        })
        
        return adapted_response
    
    def _apply_communication_adaptations(self, response: str, 
                                       preferences: Dict[str, UserPreference],
                                       context: CommunicationContext) -> str:
        """Apply specific adaptations based on preferences"""
        
        adapted_response = response
        
        # Communication style adaptation
        for pref_key, pref in preferences.items():
            if pref.category == 'communication_style':
                style_template = self.communication_templates.get(pref.value.value if hasattr(pref.value, 'value') else str(pref.value))
                if style_template:
                    adapted_response = self._apply_style_template(adapted_response, style_template)
            
            elif pref.category == 'interaction_style':
                if pref.value == 'brief_responses_preferred':
                    adapted_response = self._make_more_concise(adapted_response)
                elif pref.value == 'detailed_responses_welcomed':
                    adapted_response = self._add_helpful_details(adapted_response, context)
            
            elif pref.category == 'format_style':
                if pref.value == 'structured_lists':
                    adapted_response = self._format_as_lists(adapted_response)
        
        return adapted_response
    
    def _apply_style_template(self, response: str, template: Dict[str, str]) -> str:
        """Apply communication style template"""
        # This would implement style-specific formatting
        # For now, return original response with template awareness
        return response
    
    def _make_more_concise(self, response: str) -> str:
        """Make response more concise for users who prefer brevity"""
        # Simple implementation - could be enhanced with summarization
        sentences = response.split('. ')
        if len(sentences) > 3:
            return '. '.join(sentences[:3]) + '.'
        return response
    
    def _add_helpful_details(self, response: str, context: CommunicationContext) -> str:
        """Add helpful details for users who welcome detailed responses"""
        # This could add context-specific helpful information
        return response
    
    def _format_as_lists(self, response: str) -> str:
        """Format response with more structured lists"""
        # This would convert prose to bullet points where appropriate
        return response
    
    def get_communication_insights(self) -> Dict[str, Any]:
        """Get insights about communication adaptation performance"""
        if not self.adaptation_history:
            return {'status': 'no_adaptations_yet'}
        
        recent_adaptations = list(self.adaptation_history)[-10:]
        
        return {
            'total_adaptations': len(self.adaptation_history),
            'recent_adaptations': len(recent_adaptations),
            'active_preferences': len(self.preference_detector.preferences),
            'preference_categories': list(set(p.category for p in self.preference_detector.preferences.values())),
            'most_common_adaptations': self._analyze_adaptation_patterns()
        }
    
    def _analyze_adaptation_patterns(self) -> List[str]:
        """Analyze patterns in communication adaptations"""
        # This would analyze the adaptation history for patterns
        return ['brevity_requests', 'detail_enhancements', 'style_adaptations']

# Global communication evolution system
_communication_engine = AdaptiveCommunicationEngine()

def evolve_communication(response: str, user_message: str, 
                        domain: str = "general") -> str:
    """Main interface for communication evolution"""
    context = CommunicationContext(
        domain=domain,
        task_complexity="medium",
        user_expertise_level="intermediate", 
        interaction_history=[],
        timestamp=time.time()
    )
    
    return _communication_engine.adapt_communication(response, user_message, context)

def get_communication_evolution_stats() -> Dict[str, Any]:
    """Get communication evolution statistics"""
    return _communication_engine.get_communication_insights()

if __name__ == "__main__":
    # Test communication evolution system
    print("Communication Evolution System Test")
    print("=" * 50)
    
    # Test user preference detection
    test_messages = [
        "Can you explain this in simpler terms?",
        "I need more technical details and comprehensive analysis.",
        "This is exciting! Tell me more!",
        "Please provide a professional report format."
    ]
    
    for message in test_messages:
        adapted = evolve_communication("Here is the technical implementation...", message)
        print(f"User: {message}")
        print(f"Adapted response: {adapted[:100]}...")
        print()
    
    # Get statistics
    stats = get_communication_evolution_stats()
    print(f"Communication evolution stats: {stats}")