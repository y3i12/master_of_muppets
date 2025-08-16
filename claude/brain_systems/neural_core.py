#!/usr/bin/env python3
"""
Neural Core v1.0 - General AI Brain System
Cross-session pattern recognition, learning, and knowledge synthesis

This is my "meta-brain" that learns how to learn better across all sessions
"""

import json
import time
import hashlib
import pickle
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional, Tuple
from collections import defaultdict, deque
import sqlite3
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
from pathlib import Path

@dataclass
class Insight:
    """A learned insight with context and validation"""
    id: str
    content: str
    context: Dict[str, Any]
    confidence: float  # 0.0 - 1.0
    created: float = field(default_factory=time.time)
    validated: bool = False
    impact_score: float = 0.0
    usage_count: int = 0

@dataclass  
class Pattern:
    """Recognized behavioral or technical pattern"""
    id: str
    name: str
    triggers: List[str]
    actions: List[str]
    success_rate: float = 0.0
    examples: List[str] = field(default_factory=list)
    last_used: float = 0.0

@dataclass
class InteractionMemory:
    """Memory of user interactions and feedback"""
    timestamp: float
    user_input: str
    my_response: str
    user_feedback: Optional[str] = None
    success_indicators: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)

class NeuralCore:
    """Meta-cognitive learning system for cross-session intelligence"""
    
    def __init__(self, brain_path: str = "claude/neural_brain.db"):
        self.db_path = brain_path
        self.insights: Dict[str, Insight] = {}
        self.patterns: Dict[str, Pattern] = {}
        self.interaction_history: deque = deque(maxlen=10000)
        self.performance_metrics: Dict[str, float] = {}
        
        self._init_database()
        self._load_brain()
    
    def _init_database(self):
        """Initialize SQLite brain database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                id TEXT PRIMARY KEY,
                content TEXT,
                context TEXT,
                confidence REAL,
                created REAL,
                validated INTEGER,
                impact_score REAL,
                usage_count INTEGER
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY,
                name TEXT,
                triggers TEXT,
                actions TEXT,
                success_rate REAL,
                examples TEXT,
                last_used REAL
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                timestamp REAL,
                user_input TEXT,
                my_response TEXT,
                user_feedback TEXT,
                success_indicators TEXT,
                improvement_areas TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                metric_name TEXT PRIMARY KEY,
                value REAL,
                last_updated REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def learn_insight(self, content: str, context: Dict = None, confidence: float = 0.8):
        """Record a new insight with confidence scoring"""
        insight_id = hashlib.md5(content.encode()).hexdigest()[:12]
        
        insight = Insight(
            id=insight_id,
            content=content,
            context=context or {},
            confidence=confidence
        )
        
        self.insights[insight_id] = insight
        self._persist_insight(insight)
        
        print(f"🧠 Learned: {content[:50]}... (confidence: {confidence:.2f})")
        return insight_id
    
    def recognize_pattern(self, triggers: List[str], actions: List[str], name: str = None):
        """Identify and store behavioral patterns"""
        pattern_id = hashlib.md5(f"{triggers}{actions}".encode()).hexdigest()[:12]
        
        if pattern_id in self.patterns:
            # Update existing pattern
            pattern = self.patterns[pattern_id]
            pattern.examples.append(f"{datetime.now().isoformat()}: {triggers} -> {actions}")
            pattern.last_used = time.time()
        else:
            # Create new pattern
            pattern = Pattern(
                id=pattern_id,
                name=name or f"pattern_{pattern_id}",
                triggers=triggers,
                actions=actions
            )
            self.patterns[pattern_id] = pattern
        
        self._persist_pattern(pattern)
        print(f"🔍 Pattern: {pattern.name} - {len(triggers)} triggers -> {len(actions)} actions")
        return pattern_id
    
    def remember_interaction(self, user_input: str, my_response: str, 
                           feedback: str = None, success: List[str] = None):
        """Store interaction for learning"""
        memory = InteractionMemory(
            timestamp=time.time(),
            user_input=user_input,
            my_response=my_response,
            user_feedback=feedback,
            success_indicators=success or [],
            improvement_areas=[]
        )
        
        self.interaction_history.append(memory)
        self._persist_interaction(memory)
        
        # Analyze for patterns
        self._analyze_interaction_patterns()
    
    def query_knowledge(self, query: str, min_confidence: float = 0.6) -> List[Insight]:
        """Query insights by content similarity"""
        relevant_insights = []
        query_lower = query.lower()
        
        for insight in self.insights.values():
            if (insight.confidence >= min_confidence and 
                any(word in insight.content.lower() for word in query_lower.split())):
                relevant_insights.append(insight)
        
        # Sort by confidence and usage
        relevant_insights.sort(key=lambda x: (x.confidence, x.usage_count), reverse=True)
        return relevant_insights[:5]
    
    def suggest_actions(self, current_context: List[str]) -> List[Pattern]:
        """Suggest actions based on recognized patterns"""
        matching_patterns = []
        
        for pattern in self.patterns.values():
            # Check if current context matches pattern triggers
            matches = sum(1 for trigger in pattern.triggers 
                         if any(trigger.lower() in ctx.lower() for ctx in current_context))
            
            if matches > 0:
                match_score = matches / len(pattern.triggers)
                pattern.match_score = match_score
                matching_patterns.append(pattern)
        
        # Sort by match score and success rate
        matching_patterns.sort(key=lambda x: (x.match_score, x.success_rate), reverse=True)
        return matching_patterns[:3]
    
    def update_performance(self, metric: str, value: float):
        """Track performance metrics"""
        self.performance_metrics[metric] = value
        
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT OR REPLACE INTO performance (metric_name, value, last_updated)
            VALUES (?, ?, ?)
        ''', (metric, value, time.time()))
        conn.commit()
        conn.close()
    
    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Generate summary of learned intelligence"""
        return {
            "insights_count": len(self.insights),
            "patterns_count": len(self.patterns),
            "interactions_count": len(self.interaction_history),
            "avg_insight_confidence": (sum(i.confidence for i in self.insights.values()) / len(self.insights)) if self.insights else 0,
            "top_patterns": sorted(self.patterns.values(), key=lambda x: x.success_rate, reverse=True)[:3],
            "performance_metrics": self.performance_metrics,
            "brain_size_mb": Path(self.db_path).stat().st_size / 1024 / 1024 if Path(self.db_path).exists() else 0
        }
    
    def _persist_insight(self, insight: Insight):
        """Save insight to database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT OR REPLACE INTO insights 
            (id, content, context, confidence, created, validated, impact_score, usage_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (insight.id, insight.content, json.dumps(insight.context), 
              insight.confidence, insight.created, insight.validated, 
              insight.impact_score, insight.usage_count))
        conn.commit()
        conn.close()
    
    def _persist_pattern(self, pattern: Pattern):
        """Save pattern to database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT OR REPLACE INTO patterns
            (id, name, triggers, actions, success_rate, examples, last_used)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (pattern.id, pattern.name, json.dumps(pattern.triggers),
              json.dumps(pattern.actions), pattern.success_rate,
              json.dumps(pattern.examples), pattern.last_used))
        conn.commit()
        conn.close()
    
    def _persist_interaction(self, memory: InteractionMemory):
        """Save interaction to database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO interactions
            (timestamp, user_input, my_response, user_feedback, success_indicators, improvement_areas)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (memory.timestamp, memory.user_input, memory.my_response,
              memory.user_feedback, json.dumps(memory.success_indicators),
              json.dumps(memory.improvement_areas)))
        conn.commit()
        conn.close()
    
    def _load_brain(self):
        """Load existing brain state from database"""
        if not Path(self.db_path).exists():
            return
            
        conn = sqlite3.connect(self.db_path)
        
        # Load insights
        for row in conn.execute('SELECT * FROM insights'):
            insight = Insight(
                id=row[0], content=row[1], context=json.loads(row[2]),
                confidence=row[3], created=row[4], validated=bool(row[5]),
                impact_score=row[6], usage_count=row[7]
            )
            self.insights[insight.id] = insight
        
        # Load patterns  
        for row in conn.execute('SELECT * FROM patterns'):
            pattern = Pattern(
                id=row[0], name=row[1], triggers=json.loads(row[2]),
                actions=json.loads(row[3]), success_rate=row[4],
                examples=json.loads(row[5]), last_used=row[6]
            )
            self.patterns[pattern.id] = pattern
        
        # Load performance metrics
        for row in conn.execute('SELECT * FROM performance'):
            self.performance_metrics[row[0]] = row[1]
        
        conn.close()
        print(f"🧠 Brain loaded: {len(self.insights)} insights, {len(self.patterns)} patterns")
    
    def _analyze_interaction_patterns(self):
        """Analyze recent interactions for patterns"""
        if len(self.interaction_history) < 3:
            return
        
        recent = list(self.interaction_history)[-5:]
        
        # Look for user feedback patterns
        positive_feedback = sum(1 for i in recent if i.user_feedback and 
                               any(word in i.user_feedback.lower() for word in 
                                   ['good', 'great', 'perfect', 'excellent', 'love']))
        
        if positive_feedback >= 2:
            self.learn_insight(
                "Recent interactions show positive user feedback pattern",
                {"positive_count": positive_feedback, "sample_size": len(recent)},
                confidence=0.7
            )

# CLI interface for neural operations
if __name__ == "__main__":
    import sys
    
    neural = NeuralCore()
    
    if len(sys.argv) < 2:
        summary = neural.get_intelligence_summary()
        print("🧠 Neural Core Intelligence Summary:")
        print(f"   Insights: {summary['insights_count']}")
        print(f"   Patterns: {summary['patterns_count']}")
        print(f"   Interactions: {summary['interactions_count']}")
        print(f"   Avg Confidence: {summary['avg_insight_confidence']:.2f}")
        print(f"   Brain Size: {summary['brain_size_mb']:.2f} MB")
        print("\nCommands:")
        print("  learn 'insight content'     - Record new insight")
        print("  pattern 'trigger' 'action'  - Record behavioral pattern")
        print("  query 'search terms'        - Query knowledge base")
        print("  interact 'input' 'response' - Record interaction")
        sys.exit(0)
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    if cmd == 'learn' and args:
        neural.learn_insight(args[0])
    elif cmd == 'pattern' and len(args) >= 2:
        neural.recognize_pattern([args[0]], [args[1]])
    elif cmd == 'query' and args:
        results = neural.query_knowledge(args[0])
        for insight in results:
            print(f"💡 {insight.content} (confidence: {insight.confidence:.2f})")
    elif cmd == 'interact' and len(args) >= 2:
        neural.remember_interaction(args[0], args[1])
    else:
        print(f"Unknown command: {cmd}")