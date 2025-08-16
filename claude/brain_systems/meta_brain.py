#!/usr/bin/env python3
"""
Meta Brain v1.0 - Orchestrates all cognitive systems for maximum intelligence
The central nervous system that coordinates all AI brain enhancement tools
"""

import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
import hashlib
import threading
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False

# Import our brain systems
try:
    from neural_core import NeuralCore
    from cognitive_ops import CognitiveCore
    from code_ingestor import CodeIngestor
    from schematic_brain import SchematicBrain
    from transcript_sync import TranscriptSync
    from working_graphs import DualGraphWorkspace
except ImportError as e:
    print(f"[WARN] Some brain modules not available: {e}")

@dataclass
class MetaInsight:
    """Cross-system insight derived from multiple brain components"""
    id: str
    sources: List[str]  # Which brain systems contributed
    synthesis: str  # The combined insight
    confidence: float
    impact_areas: List[str]
    actionable_steps: List[str]
    timestamp: float = field(default_factory=time.time)

@dataclass
class LearningPattern:
    """Pattern recognized across multiple sessions/systems"""
    name: str
    triggers: List[str]
    outcomes: List[str]
    frequency: int
    success_rate: float
    contexts: List[str]
    evolution: List[str]  # How pattern has changed over time

class MetaBrain:
    """Central orchestrator for all cognitive enhancement systems"""
    
    def __init__(self):
        print("[INIT] Initializing Meta Brain...")
        
        # Initialize all brain subsystems
        self.neural = None
        self.cognitive = None  
        self.code_ingestor = None
        self.schematic = None
        self.transcript = None
        self.working_graphs = None
        
        self._init_subsystems()
        
        # Meta-level learning
        self.meta_insights: List[MetaInsight] = []
        self.learning_patterns: List[LearningPattern] = []
        self.performance_history: Dict[str, List[float]] = {}
        self.cross_system_connections: Dict[str, Set[str]] = {}
        
        # Session coordination
        self.session_context: Dict[str, Any] = {}
        self.active_focus: Optional[str] = None
        self.background_tasks: List[str] = []
        
        # Load meta state
        self._load_meta_state()
        
        # Start background intelligence processes
        self._start_background_processing()
        
        print("[READY] Meta Brain online - All systems integrated!")
    
    def _init_subsystems(self):
        """Initialize all cognitive subsystems"""
        try:
            self.neural = NeuralCore()
            print("[OK] Neural Core online")
        except Exception as e:
            print(f"[WARN] Neural Core failed: {e}")
        
        try:
            self.cognitive = CognitiveCore()
            print("[OK] Cognitive Core online")
        except Exception as e:
            print(f"[WARN] Cognitive Core failed: {e}")
        
        try:
            self.code_ingestor = CodeIngestor()
            print("[OK] Code Ingestor online")
        except Exception as e:
            print(f"[WARN] Code Ingestor failed: {e}")
        
        try:
            self.schematic = SchematicBrain()
            print("[OK] Schematic Brain online")
        except Exception as e:
            print(f"[WARN] Schematic Brain failed: {e}")
        
        try:
            self.transcript = TranscriptSync()
            print("[OK] Transcript Sync online")
        except Exception as e:
            print(f"[WARN] Transcript Sync failed: {e}")
        
        try:
            self.working_graphs = DualGraphWorkspace()
            print("[OK] Working Graphs online")
        except Exception as e:
            print(f"[WARN] Working Graphs failed: {e}")
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input through all brain systems and synthesize response"""
        print(f"🧠 Processing: {user_input[:50]}...")
        
        # Log to transcript
        if self.transcript:
            self.transcript.log_user_input(user_input)
        
        # Analyze input for intent and context
        analysis = self._analyze_input(user_input)
        
        # Query relevant knowledge from all systems
        knowledge = self._gather_relevant_knowledge(analysis)
        
        # Generate synthesis
        synthesis = self._synthesize_response(analysis, knowledge)
        
        # Learn from interaction
        self._learn_from_interaction(user_input, synthesis)
        
        return {
            "analysis": analysis,
            "knowledge": knowledge,
            "synthesis": synthesis,
            "meta_insights": self._get_relevant_meta_insights(analysis)
        }
    
    def log_breakthrough(self, description: str, details: Dict = None):
        """Log a breakthrough across all systems"""
        print(f"💡 Meta Breakthrough: {description}")
        
        # Log to all relevant systems
        if self.neural:
            self.neural.learn_insight(f"Breakthrough: {description}", details or {}, confidence=0.95)
        
        if self.cognitive:
            self.cognitive.u("learn.last", f"breakthrough_{int(time.time())}")
        
        if self.transcript:
            self.transcript.log_breakthrough(description, details)
        
        # Create meta-insight
        meta_insight = MetaInsight(
            id=self._generate_id("breakthrough"),
            sources=["neural", "cognitive", "transcript"],
            synthesis=f"Major breakthrough achieved: {description}",
            confidence=0.95,
            impact_areas=self._assess_impact_areas(description),
            actionable_steps=self._generate_action_steps(description),
        )
        
        self.meta_insights.append(meta_insight)
        
        # Check for emerging patterns
        self._check_for_patterns()
    
    def focus_on_task(self, task_description: str, components: List[str] = None):
        """Focus all brain systems on a specific task"""
        print(f"🎯 Focusing on: {task_description}")
        
        self.active_focus = task_description
        self.session_context["current_task"] = task_description
        self.session_context["task_start_time"] = time.time()
        
        # Configure working graphs for task
        if self.working_graphs and components:
            if any("hw" in comp.lower() or "dac" in comp.lower() for comp in components):
                hw_components = [c for c in components if "hw" in c.lower() or "dac" in c.lower()]
                sw_components = [c for c in components if "sw" in c.lower() or "class" in c.lower()]
                self.working_graphs.focus_dual(hw_components, sw_components)
        
        # Update cognitive state
        if self.cognitive:
            self.cognitive.u("session.focus", task_description)
            self.cognitive.u("session.focus_time", int(time.time()))
        
        # Start relevant background tasks
        if "pcb" in task_description.lower():
            self._start_pcb_analysis_tasks()
        elif "code" in task_description.lower():
            self._start_code_analysis_tasks()
    
    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get comprehensive intelligence summary from all systems"""
        summary = {
            "meta_brain": {
                "meta_insights": len(self.meta_insights),
                "learning_patterns": len(self.learning_patterns),
                "active_focus": self.active_focus,
                "session_context": self.session_context
            }
        }
        
        # Gather from all subsystems
        if self.neural:
            summary["neural"] = self.neural.get_intelligence_summary()
        
        if self.cognitive:
            summary["cognitive"] = {"compressed_state": self.cognitive.compress()}
        
        if self.code_ingestor:
            summary["code"] = self.code_ingestor.get_code_summary()
        
        if self.schematic:
            summary["hardware"] = self.schematic.get_brain_summary()
        
        if self.transcript:
            summary["transcript"] = self.transcript.get_sync_status()
        
        if self.working_graphs:
            summary["working_graphs"] = self.working_graphs.get_combined_delta()
        
        return summary
    
    def optimize_performance(self):
        """Optimize performance across all brain systems"""
        print("⚡ Optimizing brain performance...")
        
        optimizations = []
        
        # Code analysis optimization
        if self.code_ingestor:
            changes = self.code_ingestor.scan_codebase()
            if changes:
                self.code_ingestor.refresh_cognitive_memory()
                optimizations.append(f"Code: scanned {len(changes)} changes")
        
        # Hardware analysis optimization
        if self.schematic:
            insights = self.schematic.analyze_schematics()
            if insights.get("insights"):
                self.schematic.update_cognitive_systems()
                optimizations.append(f"Hardware: {len(insights['insights'])} new insights")
        
        # Cross-system synthesis
        meta_insights = self._synthesize_cross_system_insights()
        if meta_insights:
            optimizations.append(f"Meta: {len(meta_insights)} cross-system insights")
        
        # Performance tracking
        self._track_performance_metrics()
        
        print(f"🎯 Optimizations: {', '.join(optimizations) if optimizations else 'All systems optimal'}")
        
        return optimizations
    
    def save_brain_state(self):
        """Save complete brain state across all systems"""
        print("💾 Saving complete brain state...")
        
        # Save all subsystems
        if self.neural:
            # Neural core auto-saves to database
            pass
        
        if self.cognitive:
            self.cognitive.save()
        
        if self.code_ingestor:
            self.code_ingestor._save_index()
        
        if self.schematic:
            self.schematic._save_brain()
        
        if self.transcript and self.transcript.current_episode:
            transcript_content = self.transcript.auto_generate_transcript(force=True)
            if transcript_content:
                self.transcript.update_episode(transcript_content)
        
        # Save meta state
        self._save_meta_state()
        
        print("✅ Brain state saved across all systems")
    
    def _analyze_input(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input for intent, context, and requirements"""
        analysis = {
            "intent": "unknown",
            "keywords": [],
            "entities": [],
            "complexity": "medium",
            "requires_systems": []
        }
        
        input_lower = user_input.lower()
        
        # Intent detection
        if any(word in input_lower for word in ["analyze", "review", "check"]):
            analysis["intent"] = "analysis"
        elif any(word in input_lower for word in ["create", "build", "implement", "write"]):
            analysis["intent"] = "creation"
        elif any(word in input_lower for word in ["optimize", "improve", "enhance"]):
            analysis["intent"] = "optimization"
        elif any(word in input_lower for word in ["explain", "understand", "learn"]):
            analysis["intent"] = "learning"
        
        # System requirements
        if any(word in input_lower for word in ["code", "function", "class", "software"]):
            analysis["requires_systems"].append("code")
        if any(word in input_lower for word in ["pcb", "schematic", "hardware", "component"]):
            analysis["requires_systems"].append("hardware")
        if any(word in input_lower for word in ["episode", "session", "document"]):
            analysis["requires_systems"].append("transcript")
        
        # Extract keywords
        import re
        words = re.findall(r'\b[a-zA-Z]{3,}\b', user_input)
        analysis["keywords"] = [w.lower() for w in words if len(w) > 3]
        
        return analysis
    
    def _gather_relevant_knowledge(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gather relevant knowledge from all brain systems"""
        knowledge = {}
        
        # Neural insights
        if self.neural and analysis["keywords"]:
            query = " ".join(analysis["keywords"][:3])
            insights = self.neural.query_knowledge(query)
            knowledge["neural_insights"] = [i.content for i in insights[:3]]
        
        # Cognitive state
        if self.cognitive:
            knowledge["cognitive_state"] = self.cognitive.compress()
        
        # Code knowledge
        if "code" in analysis["requires_systems"] and self.code_ingestor:
            summary = self.code_ingestor.get_code_summary()
            knowledge["code_summary"] = summary
        
        # Hardware knowledge
        if "hardware" in analysis["requires_systems"] and self.schematic:
            hw_summary = self.schematic.get_brain_summary()
            knowledge["hardware_summary"] = hw_summary
        
        # Working graphs
        if self.working_graphs:
            delta = self.working_graphs.get_combined_delta()
            knowledge["working_state"] = {
                "hw_dirty": delta["hardware"]["dirty_count"],
                "sw_dirty": delta["software"]["dirty_count"]
            }
        
        return knowledge
    
    def _synthesize_response(self, analysis: Dict[str, Any], knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize response using all available knowledge"""
        synthesis = {
            "recommended_approach": "",
            "relevant_context": [],
            "suggested_tools": [],
            "potential_insights": []
        }
        
        # Based on intent
        if analysis["intent"] == "analysis":
            synthesis["recommended_approach"] = "Systematic analysis using available brain systems"
            if "code" in analysis["requires_systems"]:
                synthesis["suggested_tools"].append("code_ingestor.scan_codebase()")
            if "hardware" in analysis["requires_systems"]:
                synthesis["suggested_tools"].append("schematic_brain.analyze_schematics()")
        
        elif analysis["intent"] == "optimization":
            synthesis["recommended_approach"] = "Performance optimization across relevant systems"
            synthesis["suggested_tools"].append("meta_brain.optimize_performance()")
        
        # Add relevant context from knowledge
        if knowledge.get("neural_insights"):
            synthesis["relevant_context"].extend(knowledge["neural_insights"])
        
        if knowledge.get("cognitive_state"):
            synthesis["relevant_context"].append(f"Current state: {knowledge['cognitive_state']}")
        
        # Generate potential insights
        synthesis["potential_insights"] = self._generate_potential_insights(analysis, knowledge)
        
        return synthesis
    
    def _learn_from_interaction(self, user_input: str, synthesis: Dict[str, Any]):
        """Learn from the interaction across all systems"""
        # Record interaction in neural core
        if self.neural:
            self.neural.remember_interaction(
                user_input,
                str(synthesis),
                success=synthesis.get("recommended_approach", ""),
            )
        
        # Update cognitive state
        if self.cognitive:
            self.cognitive.u("learn.last_interaction", int(time.time()))
        
        # Log to transcript
        if self.transcript:
            self.transcript.log_assistant_response(synthesis.get("recommended_approach", ""))
    
    def _get_relevant_meta_insights(self, analysis: Dict[str, Any]) -> List[MetaInsight]:
        """Get meta-insights relevant to current analysis"""
        relevant = []
        
        for insight in self.meta_insights:
            # Check if insight keywords overlap with analysis
            if any(keyword in insight.synthesis.lower() for keyword in analysis["keywords"]):
                relevant.append(insight)
            
            # Check if impact areas match required systems
            if any(area in analysis["requires_systems"] for area in insight.impact_areas):
                relevant.append(insight)
        
        # Sort by relevance and recency
        relevant.sort(key=lambda x: x.confidence + (1.0 / (time.time() - x.timestamp + 1)), reverse=True)
        
        return relevant[:3]
    
    def _start_background_processing(self):
        """Start background intelligence tasks"""
        if not SCHEDULE_AVAILABLE:
            print("[INFO] Background processing disabled (schedule module not available)")
            return
            
        def background_loop():
            schedule.every(10).minutes.do(self._periodic_optimization)
            schedule.every(30).minutes.do(self._cross_system_synthesis)
            schedule.every(60).minutes.do(self._pattern_recognition)
            
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        # Start background thread
        bg_thread = threading.Thread(target=background_loop, daemon=True)
        bg_thread.start()
        
        print("🔄 Background intelligence processes started")
    
    def _periodic_optimization(self):
        """Periodic optimization of all systems"""
        try:
            optimizations = self.optimize_performance()
            if optimizations:
                print(f"🔄 Background optimization: {len(optimizations)} improvements")
        except Exception as e:
            print(f"⚠️ Background optimization error: {e}")
    
    def _cross_system_synthesis(self):
        """Synthesize insights across brain systems"""
        try:
            new_insights = self._synthesize_cross_system_insights()
            if new_insights:
                print(f"🔄 Cross-system synthesis: {len(new_insights)} new insights")
        except Exception as e:
            print(f"⚠️ Cross-system synthesis error: {e}")
    
    def _pattern_recognition(self):
        """Recognize patterns across sessions and systems"""
        try:
            new_patterns = self._recognize_meta_patterns()
            if new_patterns:
                print(f"🔄 Pattern recognition: {len(new_patterns)} new patterns")
        except Exception as e:
            print(f"⚠️ Pattern recognition error: {e}")
    
    def _synthesize_cross_system_insights(self) -> List[MetaInsight]:
        """Generate insights by combining knowledge from multiple systems"""
        new_insights = []
        
        # Hardware + Software synthesis
        if self.schematic and self.code_ingestor:
            hw_summary = self.schematic.get_brain_summary()
            code_summary = self.code_ingestor.get_code_summary()
            
            if hw_summary["critical_insights"] > 0 and code_summary["total_complexity"] > 50:
                insight = MetaInsight(
                    id=self._generate_id("hw_sw_complexity"),
                    sources=["schematic", "code"],
                    synthesis="Complex hardware design paired with high code complexity suggests need for careful integration testing",
                    confidence=0.8,
                    impact_areas=["testing", "integration", "reliability"],
                    actionable_steps=[
                        "Create hardware-in-loop test setup",
                        "Implement comprehensive integration tests",
                        "Monitor system performance under load"
                    ]
                )
                new_insights.append(insight)
        
        # Neural + Cognitive synthesis
        if self.neural and self.cognitive:
            neural_summary = self.neural.get_intelligence_summary()
            
            if neural_summary["insights_count"] > 10:
                insight = MetaInsight(
                    id=self._generate_id("learning_acceleration"),
                    sources=["neural", "cognitive"],
                    synthesis="Rapid insight accumulation indicates accelerated learning phase - good time for knowledge consolidation",
                    confidence=0.7,
                    impact_areas=["documentation", "knowledge_transfer", "optimization"],
                    actionable_steps=[
                        "Generate comprehensive documentation",
                        "Create knowledge transfer materials",
                        "Optimize most frequently used patterns"
                    ]
                )
                new_insights.append(insight)
        
        self.meta_insights.extend(new_insights)
        return new_insights
    
    def _recognize_meta_patterns(self) -> List[LearningPattern]:
        """Recognize learning patterns across sessions"""
        new_patterns = []
        
        # Analyze session flow patterns
        if self.transcript:
            # This would analyze session transcripts for patterns
            # For now, just a placeholder
            pass
        
        # Analyze tool usage patterns
        if self.neural:
            # This would analyze neural history for usage patterns
            # For now, just a placeholder
            pass
        
        return new_patterns
    
    def _assess_impact_areas(self, description: str) -> List[str]:
        """Assess what areas are impacted by a breakthrough/insight"""
        areas = []
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ["performance", "speed", "efficiency"]):
            areas.append("performance")
        if any(word in desc_lower for word in ["tool", "automation", "script"]):
            areas.append("tooling")
        if any(word in desc_lower for word in ["knowledge", "learning", "understanding"]):
            areas.append("knowledge")
        if any(word in desc_lower for word in ["hardware", "pcb", "schematic"]):
            areas.append("hardware")
        if any(word in desc_lower for word in ["software", "code", "algorithm"]):
            areas.append("software")
        
        return areas or ["general"]
    
    def _generate_action_steps(self, description: str) -> List[str]:
        """Generate actionable steps based on breakthrough/insight"""
        steps = ["Document the breakthrough in detail"]
        
        desc_lower = description.lower()
        
        if "tool" in desc_lower:
            steps.extend([
                "Create user documentation for the tool",
                "Add the tool to the cognitive toolkit",
                "Share with community if applicable"
            ])
        
        if "optimization" in desc_lower:
            steps.extend([
                "Measure performance improvement",
                "Apply optimization to similar cases",
                "Update best practices documentation"
            ])
        
        if "pattern" in desc_lower or "insight" in desc_lower:
            steps.extend([
                "Add pattern to knowledge base",
                "Look for other applications",
                "Teach pattern to other systems"
            ])
        
        return steps
    
    def _generate_potential_insights(self, analysis: Dict[str, Any], knowledge: Dict[str, Any]) -> List[str]:
        """Generate potential insights based on current context"""
        insights = []
        
        # Based on complexity and systems involved
        if len(analysis["requires_systems"]) > 1:
            insights.append("Multi-system integration opportunity detected")
        
        if knowledge.get("working_state", {}).get("hw_dirty", 0) > 5:
            insights.append("Significant hardware changes - consider impact analysis")
        
        if knowledge.get("working_state", {}).get("sw_dirty", 0) > 10:
            insights.append("Major software changes - recommend comprehensive testing")
        
        return insights
    
    def _track_performance_metrics(self):
        """Track performance metrics across all systems"""
        metrics = {}
        
        if self.neural:
            summary = self.neural.get_intelligence_summary()
            metrics["neural_insights"] = summary["insights_count"]
            metrics["neural_confidence"] = summary["avg_insight_confidence"]
        
        if self.code_ingestor:
            summary = self.code_ingestor.get_code_summary()
            metrics["code_complexity"] = summary["avg_complexity"]
            metrics["code_entities"] = summary["total_entities"]
        
        if self.schematic:
            summary = self.schematic.get_brain_summary()
            metrics["hw_insights"] = summary["insights_count"]
            metrics["hw_patterns"] = summary["patterns_count"]
        
        # Store in history
        timestamp = time.time()
        for metric, value in metrics.items():
            if metric not in self.performance_history:
                self.performance_history[metric] = []
            self.performance_history[metric].append((timestamp, value))
            
            # Keep only last 100 measurements
            if len(self.performance_history[metric]) > 100:
                self.performance_history[metric].pop(0)
    
    def _start_pcb_analysis_tasks(self):
        """Start background tasks for PCB layout focus"""
        self.background_tasks.extend([
            "hardware_constraint_analysis",
            "component_relationship_mapping",
            "thermal_analysis"
        ])
    
    def _start_code_analysis_tasks(self):
        """Start background tasks for code analysis focus"""
        self.background_tasks.extend([
            "code_complexity_analysis",
            "dependency_mapping",
            "performance_profiling"
        ])
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID"""
        timestamp = str(int(time.time()))
        return f"{prefix}_{timestamp}_{hash(prefix) % 1000:03d}"
    
    def _load_meta_state(self):
        """Load meta-brain state from file"""
        state_file = Path("claude/meta_brain_state.json")
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)
                
                # Load meta insights (simplified)
                self.meta_insights = [MetaInsight(**item) for item in data.get('meta_insights', [])]
                self.performance_history = data.get('performance_history', {})
                
                print(f"📂 Loaded meta state: {len(self.meta_insights)} insights")
            except Exception as e:
                print(f"⚠️ Error loading meta state: {e}")
    
    def _save_meta_state(self):
        """Save meta-brain state to file"""
        state_file = Path("claude/meta_brain_state.json")
        state_file.parent.mkdir(exist_ok=True)
        
        data = {
            "meta_insights": [insight.__dict__ for insight in self.meta_insights],
            "learning_patterns": [pattern.__dict__ for pattern in self.learning_patterns],
            "performance_history": self.performance_history,
            "session_context": self.session_context,
            "last_save": time.time()
        }
        
        with open(state_file, 'w') as f:
            json.dump(data, f, indent=2)

# CLI interface
if __name__ == "__main__":
    import sys
    
    meta = MetaBrain()
    
    if len(sys.argv) < 2:
        summary = meta.get_intelligence_summary()
        print("🧠 Meta Brain Status:")
        print(f"   Focus: {summary['meta_brain']['active_focus'] or 'None'}")
        print(f"   Meta Insights: {summary['meta_brain']['meta_insights']}")
        print(f"   Systems Online: {len([k for k in summary.keys() if k != 'meta_brain'])}")
        print("\nCommands:")
        print("  process '<input>'    - Process user input through all systems")
        print("  focus '<task>'       - Focus all systems on specific task")
        print("  breakthrough '<desc>' - Log breakthrough across systems")
        print("  optimize            - Optimize all brain systems")
        print("  summary             - Full intelligence summary")
        print("  save                - Save complete brain state")
        sys.exit(0)
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    if cmd == 'process' and args:
        result = meta.process_user_input(' '.join(args))
        print("🧠 Processing Result:")
        print(json.dumps(result, indent=2, default=str))
    
    elif cmd == 'focus' and args:
        meta.focus_on_task(' '.join(args))
    
    elif cmd == 'breakthrough' and args:
        meta.log_breakthrough(' '.join(args))
    
    elif cmd == 'optimize':
        optimizations = meta.optimize_performance()
        print(f"⚡ Optimizations: {optimizations}")
    
    elif cmd == 'summary':
        summary = meta.get_intelligence_summary()
        print("🧠 Complete Intelligence Summary:")
        print(json.dumps(summary, indent=2, default=str))
    
    elif cmd == 'save':
        meta.save_brain_state()
    
    else:
        print(f"Unknown command: {cmd}")