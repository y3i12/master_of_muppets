#!/usr/bin/env python3
"""
Enhanced Pattern Recognition System - Advanced Learning Algorithms
Improved cognitive pattern recognition with neural network approaches
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import time
import math

@dataclass
class PatternSignature:
    """Enhanced pattern signature with neural network features"""
    pattern_id: str
    pattern_type: str  # 'failure', 'success', 'optimization', 'learning'
    features: List[float]  # Neural network feature vector
    context_embedding: List[float]  # Context representation
    frequency: int = 1
    success_rate: float = 0.0
    confidence_score: float = 0.0
    temporal_weight: float = 1.0
    last_seen: float = 0.0

@dataclass
class LearningContext:
    """Enhanced learning context with embedding"""
    domain: str  # 'pcb', 'kicad', 'manufacturing', 'routing'
    operation: str
    parameters: Dict[str, Any]
    environment: Dict[str, Any]
    timestamp: float
    embedding: List[float] = None

class NeuralPatternMatcher:
    """Neural network-inspired pattern matching"""
    
    def __init__(self, feature_dim: int = 64, context_dim: int = 32):
        self.feature_dim = feature_dim
        self.context_dim = context_dim
        self.patterns = {}
        self.feature_weights = np.random.normal(0, 0.1, (feature_dim,))
        self.context_weights = np.random.normal(0, 0.1, (context_dim,))
        
    def encode_features(self, input_data: Dict[str, Any]) -> List[float]:
        """Encode input data into neural network features"""
        features = np.zeros(self.feature_dim)
        
        # Hash-based feature encoding for different data types
        for key, value in input_data.items():
            key_hash = hash(key) % self.feature_dim
            
            if isinstance(value, (int, float)):
                features[key_hash] = float(value) / 1000.0  # Normalize
            elif isinstance(value, str):
                value_hash = hash(value) % self.feature_dim
                features[value_hash] = 1.0
            elif isinstance(value, bool):
                features[key_hash] = 1.0 if value else -1.0
            elif isinstance(value, list):
                for i, item in enumerate(value[:10]):  # Limit to first 10 items
                    idx = (key_hash + i) % self.feature_dim
                    features[idx] = hash(str(item)) % 100 / 100.0
        
        return features.tolist()
    
    def encode_context(self, context: LearningContext) -> List[float]:
        """Encode learning context into embedding"""
        context_features = np.zeros(self.context_dim)
        
        # Domain encoding
        domain_hash = hash(context.domain) % self.context_dim
        context_features[domain_hash] = 1.0
        
        # Operation encoding
        op_hash = hash(context.operation) % self.context_dim
        context_features[op_hash] = 0.8
        
        # Temporal encoding
        time_factor = math.sin(context.timestamp / 86400)  # Daily cycle
        context_features[0] = time_factor
        
        # Parameter complexity encoding
        param_complexity = len(context.parameters) / 20.0  # Normalize
        context_features[1] = min(param_complexity, 1.0)
        
        return context_features.tolist()
    
    def similarity_score(self, pattern1: PatternSignature, pattern2: PatternSignature) -> float:
        """Calculate neural similarity between patterns"""
        # Feature similarity using cosine distance
        features1 = np.array(pattern1.features)
        features2 = np.array(pattern2.features)
        
        feature_sim = np.dot(features1, features2) / (
            np.linalg.norm(features1) * np.linalg.norm(features2) + 1e-8
        )
        
        # Context similarity
        context1 = np.array(pattern1.context_embedding)
        context2 = np.array(pattern2.context_embedding)
        
        context_sim = np.dot(context1, context2) / (
            np.linalg.norm(context1) * np.linalg.norm(context2) + 1e-8
        )
        
        # Weighted combination
        total_similarity = 0.7 * feature_sim + 0.3 * context_sim
        
        # Temporal decay factor
        time_diff = abs(pattern1.last_seen - pattern2.last_seen)
        decay_factor = math.exp(-time_diff / 86400)  # 1-day half-life
        
        return float(total_similarity * decay_factor)

class EnhancedPatternRecognition:
    """Advanced pattern recognition with neural network approaches"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.patterns_file = self.base_path / "claude" / "brain_systems" / "enhanced_patterns.json"
        self.patterns_file.parent.mkdir(exist_ok=True, parents=True)
        
        # Neural pattern matcher
        self.neural_matcher = NeuralPatternMatcher()
        
        # Pattern storage
        self.patterns: Dict[str, PatternSignature] = {}
        self.pattern_graph = defaultdict(list)  # Pattern relationships
        self.recent_patterns = deque(maxlen=1000)
        
        # Learning statistics
        self.learning_stats = {
            'patterns_learned': 0,
            'successful_predictions': 0,
            'failed_predictions': 0,
            'pattern_merges': 0,
            'adaptation_cycles': 0
        }
        
        # Load existing patterns
        self.load_patterns()
    
    def learn_pattern(self, context: LearningContext, outcome: Dict[str, Any], 
                     pattern_type: str = 'learning') -> str:
        """Learn a new pattern with neural encoding"""
        
        # Generate pattern ID
        pattern_id = f"{pattern_type}_{context.domain}_{int(time.time())}_{len(self.patterns)}"
        
        # Encode features and context
        features = self.neural_matcher.encode_features(outcome)
        context_embedding = self.neural_matcher.encode_context(context)
        context.embedding = context_embedding
        
        # Create pattern signature
        pattern = PatternSignature(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            features=features,
            context_embedding=context_embedding,
            frequency=1,
            success_rate=1.0 if outcome.get('success', False) else 0.0,
            confidence_score=0.5,  # Initial confidence
            temporal_weight=1.0,
            last_seen=time.time()
        )
        
        # Check for similar existing patterns
        similar_pattern = self._find_similar_pattern(pattern)
        
        if similar_pattern:
            # Merge with existing pattern
            self._merge_patterns(similar_pattern, pattern)
            self.learning_stats['pattern_merges'] += 1
            return similar_pattern.pattern_id
        else:
            # Store new pattern
            self.patterns[pattern_id] = pattern
            self.recent_patterns.append(pattern_id)
            self.learning_stats['patterns_learned'] += 1
            
            # Update pattern graph relationships
            self._update_pattern_graph(pattern)
            
            return pattern_id
    
    def predict_outcome(self, context: LearningContext, 
                       parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Predict outcome using neural pattern matching"""
        
        # Encode input for prediction
        features = self.neural_matcher.encode_features(parameters)
        context_embedding = self.neural_matcher.encode_context(context)
        
        # Create temporary pattern for matching
        query_pattern = PatternSignature(
            pattern_id="query",
            pattern_type="query",
            features=features,
            context_embedding=context_embedding,
            last_seen=time.time()
        )
        
        # Find best matching patterns
        matches = []
        for pattern in self.patterns.values():
            if pattern.pattern_type in ['success', 'optimization', 'learning']:
                similarity = self.neural_matcher.similarity_score(query_pattern, pattern)
                if similarity > 0.3:  # Threshold for relevance
                    matches.append((pattern, similarity))
        
        # Sort by similarity and confidence
        matches.sort(key=lambda x: x[1] * x[0].confidence_score, reverse=True)
        
        if not matches:
            return {
                'prediction_available': False,
                'confidence': 0.0,
                'reason': 'No similar patterns found'
            }
        
        # Use top matches for prediction
        top_matches = matches[:5]  # Use top 5 patterns
        
        # Weighted prediction ensemble
        total_weight = sum(sim * pattern.confidence_score for pattern, sim in top_matches)
        success_prediction = sum(
            sim * pattern.confidence_score * pattern.success_rate 
            for pattern, sim in top_matches
        ) / max(total_weight, 1e-8)
        
        # Confidence based on pattern agreement
        confidences = [pattern.confidence_score * sim for pattern, sim in top_matches]
        avg_confidence = sum(confidences) / len(confidences)
        
        return {
            'prediction_available': True,
            'success_probability': success_prediction,
            'confidence': avg_confidence,
            'matching_patterns': len(top_matches),
            'top_pattern_similarity': matches[0][1] if matches else 0.0,
            'recommended_adjustments': self._generate_recommendations(top_matches)
        }
    
    def adapt_learning_rate(self, recent_performance: List[bool]) -> float:
        """Dynamically adapt learning rate based on performance"""
        if len(recent_performance) < 5:
            return 1.0  # Default learning rate
        
        # Calculate recent success rate
        success_rate = sum(recent_performance) / len(recent_performance)
        
        # Adaptive learning rate
        if success_rate > 0.8:
            # High success - reduce learning rate for stability
            learning_rate = 0.5
        elif success_rate < 0.4:
            # Low success - increase learning rate for faster adaptation
            learning_rate = 1.5
        else:
            # Moderate success - standard learning rate
            learning_rate = 1.0
        
        self.learning_stats['adaptation_cycles'] += 1
        return learning_rate
    
    def _find_similar_pattern(self, new_pattern: PatternSignature, 
                            threshold: float = 0.8) -> Optional[PatternSignature]:
        """Find similar existing pattern using neural matching"""
        for pattern in self.patterns.values():
            if pattern.pattern_type == new_pattern.pattern_type:
                similarity = self.neural_matcher.similarity_score(new_pattern, pattern)
                if similarity > threshold:
                    return pattern
        return None
    
    def _merge_patterns(self, existing: PatternSignature, new: PatternSignature):
        """Merge new pattern with existing similar pattern"""
        # Update frequency
        existing.frequency += 1
        
        # Update success rate with exponential moving average
        alpha = 0.3  # Learning rate for updates
        existing.success_rate = (1 - alpha) * existing.success_rate + alpha * new.success_rate
        
        # Update confidence based on frequency and consistency
        consistency = 1.0 - abs(existing.success_rate - new.success_rate)
        existing.confidence_score = min(1.0, existing.confidence_score + 0.1 * consistency)
        
        # Update features with weighted average
        weight_existing = existing.frequency / (existing.frequency + 1)
        weight_new = 1.0 / (existing.frequency + 1)
        
        existing.features = [
            weight_existing * e + weight_new * n 
            for e, n in zip(existing.features, new.features)
        ]
        
        # Update timestamp
        existing.last_seen = time.time()
    
    def _update_pattern_graph(self, pattern: PatternSignature):
        """Update pattern relationship graph"""
        # Find related patterns based on context similarity
        for existing_pattern in self.patterns.values():
            if existing_pattern.pattern_id != pattern.pattern_id:
                context_sim = np.dot(
                    np.array(pattern.context_embedding),
                    np.array(existing_pattern.context_embedding)
                )
                
                if context_sim > 0.5:  # Threshold for relationship
                    self.pattern_graph[pattern.pattern_id].append(existing_pattern.pattern_id)
                    self.pattern_graph[existing_pattern.pattern_id].append(pattern.pattern_id)
    
    def _generate_recommendations(self, top_matches: List[Tuple[PatternSignature, float]]) -> List[str]:
        """Generate recommendations based on successful patterns"""
        recommendations = []
        
        for pattern, similarity in top_matches[:3]:
            if pattern.success_rate > 0.7:
                recommendations.append(
                    f"Similar successful pattern (sim={similarity:.2f}, "
                    f"success={pattern.success_rate:.1%}): "
                    f"{pattern.pattern_type} in {pattern.pattern_id.split('_')[1]} domain"
                )
        
        return recommendations
    
    def save_patterns(self):
        """Save patterns to disk with neural data"""
        pattern_data = {
            'patterns': {
                pid: asdict(pattern) for pid, pattern in self.patterns.items()
            },
            'pattern_graph': dict(self.pattern_graph),
            'learning_stats': self.learning_stats,
            'neural_weights': {
                'feature_weights': self.neural_matcher.feature_weights.tolist(),
                'context_weights': self.neural_matcher.context_weights.tolist()
            },
            'version': '2.0',
            'last_updated': time.time()
        }
        
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(pattern_data, f, indent=2)
        except Exception as e:
            print(f"[PATTERN_RECOGNITION] Save error: {e}")
    
    def load_patterns(self):
        """Load patterns from disk"""
        if not self.patterns_file.exists():
            return
        
        try:
            with open(self.patterns_file, 'r') as f:
                data = json.load(f)
            
            # Load patterns
            for pid, pattern_data in data.get('patterns', {}).items():
                self.patterns[pid] = PatternSignature(**pattern_data)
            
            # Load pattern graph
            self.pattern_graph = defaultdict(list, data.get('pattern_graph', {}))
            
            # Load statistics
            self.learning_stats.update(data.get('learning_stats', {}))
            
            # Load neural weights if available
            neural_weights = data.get('neural_weights', {})
            if neural_weights:
                self.neural_matcher.feature_weights = np.array(neural_weights.get('feature_weights', []))
                self.neural_matcher.context_weights = np.array(neural_weights.get('context_weights', []))
            
        except Exception as e:
            print(f"[PATTERN_RECOGNITION] Load error: {e}")
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about learning performance"""
        total_predictions = self.learning_stats['successful_predictions'] + self.learning_stats['failed_predictions']
        prediction_accuracy = (
            self.learning_stats['successful_predictions'] / max(total_predictions, 1)
        )
        
        return {
            'total_patterns': len(self.patterns),
            'recent_patterns': len(self.recent_patterns),
            'pattern_types': {
                ptype: len([p for p in self.patterns.values() if p.pattern_type == ptype])
                for ptype in ['success', 'failure', 'optimization', 'learning']
            },
            'prediction_accuracy': prediction_accuracy,
            'pattern_merges': self.learning_stats['pattern_merges'],
            'adaptation_cycles': self.learning_stats['adaptation_cycles'],
            'avg_pattern_confidence': sum(p.confidence_score for p in self.patterns.values()) / max(len(self.patterns), 1)
        }

if __name__ == "__main__":
    # Test enhanced pattern recognition
    print("Enhanced Pattern Recognition System Test")
    print("=" * 50)
    
    recognizer = EnhancedPatternRecognition()
    
    # Test learning
    context = LearningContext(
        domain="pcb",
        operation="routing",
        parameters={"net_count": 89, "complexity": "high"},
        environment={"tool": "kicad-fu", "version": "1.0"},
        timestamp=time.time()
    )
    
    outcome = {
        "success": True,
        "routing_score": 69.9,
        "completion_rate": 100.0,
        "optimization_applied": ["via_reduction", "length_optimization"]
    }
    
    pattern_id = recognizer.learn_pattern(context, outcome, "success")
    print(f"Learned pattern: {pattern_id}")
    
    # Test prediction
    prediction = recognizer.predict_outcome(context, {
        "net_count": 85,
        "complexity": "high",
        "board_size": [100, 80]
    })
    
    print(f"Prediction available: {prediction['prediction_available']}")
    if prediction['prediction_available']:
        print(f"Success probability: {prediction['success_probability']:.1%}")
        print(f"Confidence: {prediction['confidence']:.1%}")
    
    # Get insights
    insights = recognizer.get_learning_insights()
    print(f"\nLearning Insights:")
    print(f"Total patterns: {insights['total_patterns']}")
    print(f"Prediction accuracy: {insights['prediction_accuracy']:.1%}")
    
    # Save patterns
    recognizer.save_patterns()
    print("Pattern recognition test complete!")