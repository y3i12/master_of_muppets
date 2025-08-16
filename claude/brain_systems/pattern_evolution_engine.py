#!/usr/bin/env python3
"""
Pattern Evolution Engine v1.0 - Self-evolving tooling system
Detects repetitive patterns, creates tools, and evolves them automatically
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class PatternDetection:
    """Detected pattern in task execution"""
    pattern_id: str
    pattern_type: str  # file_ops, search, analysis, generation, transformation
    frequency: int
    last_seen: float
    examples: List[str] = field(default_factory=list)
    tool_exists: bool = False
    tool_path: Optional[str] = None
    efficiency_gain: float = 1.0

@dataclass 
class ToolEvolution:
    """Tool evolution tracking"""
    tool_name: str
    version: float
    creation_time: float
    usage_count: int
    average_time_saved: float
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)
    pending_improvements: List[str] = field(default_factory=list)

class PatternEvolutionEngine:
    """Self-evolving pattern detection and tool creation system"""
    
    def __init__(self, evolution_path: str = "claude/brain_systems/evolution"):
        self.evolution_path = Path(evolution_path)
        self.evolution_path.mkdir(exist_ok=True)
        
        self.pattern_memory = defaultdict(lambda: defaultdict(int))
        self.detected_patterns = {}
        self.evolved_tools = {}
        self.task_history = []
        self.evolution_threshold = 3  # Pattern must occur 3+ times
        
        self._load_evolution_state()
        print("[EVOLUTION] Pattern Evolution Engine initialized")
    
    def observe_task(self, task_type: str, task_details: Dict[str, Any]) -> Optional[str]:
        """Observe a task and detect patterns"""
        
        # Create task signature
        task_signature = self._create_task_signature(task_type, task_details)
        
        # Record in pattern memory
        self.pattern_memory[task_type][task_signature] += 1
        frequency = self.pattern_memory[task_type][task_signature]
        
        # Record in history
        self.task_history.append({
            "type": task_type,
            "signature": task_signature,
            "details": task_details,
            "timestamp": time.time()
        })
        
        # Check if pattern threshold reached
        if frequency == self.evolution_threshold:
            print(f"[PATTERN] Detected repetitive pattern: {task_type}")
            tool_name = self._evolve_tool_for_pattern(task_type, task_signature, task_details)
            return tool_name
        
        elif frequency > self.evolution_threshold:
            # Check if tool needs evolution
            if task_signature in self.detected_patterns:
                pattern = self.detected_patterns[task_signature]
                if pattern.tool_exists and frequency % 10 == 0:  # Every 10 uses
                    self._evolve_existing_tool(pattern)
        
        return None
    
    def _create_task_signature(self, task_type: str, task_details: Dict[str, Any]) -> str:
        """Create unique signature for task pattern"""
        
        # Extract key patterns
        pattern_keys = []
        
        if task_type == "file_ops":
            pattern_keys = ["operation", "file_pattern", "directory_pattern"]
        elif task_type == "search":
            pattern_keys = ["search_type", "target_pattern", "scope"]
        elif task_type == "analysis":
            pattern_keys = ["analysis_type", "input_format", "output_format"]
        elif task_type == "generation":
            pattern_keys = ["template_type", "output_type", "parameters"]
        elif task_type == "transformation":
            pattern_keys = ["input_type", "output_type", "transformation"]
        
        # Build signature from relevant keys
        sig_parts = [task_type]
        for key in pattern_keys:
            if key in task_details:
                sig_parts.append(str(task_details[key]))
        
        signature = ":".join(sig_parts)
        return hashlib.md5(signature.encode()).hexdigest()[:8]
    
    def _evolve_tool_for_pattern(self, task_type: str, signature: str, details: Dict[str, Any]) -> str:
        """Create or evolve tool for detected pattern"""
        
        tool_name = f"{task_type}_{signature}_tool"
        tool_path = self.evolution_path / f"{tool_name}.py"
        
        # Generate tool code based on pattern
        tool_code = self._generate_tool_code(task_type, details)
        
        # Write tool
        with open(tool_path, 'w', encoding='utf-8') as f:
            f.write(tool_code)
        
        # Register pattern and tool
        self.detected_patterns[signature] = PatternDetection(
            pattern_id=signature,
            pattern_type=task_type,
            frequency=self.evolution_threshold,
            last_seen=time.time(),
            examples=[str(details)],
            tool_exists=True,
            tool_path=str(tool_path),
            efficiency_gain=2.0  # Estimated
        )
        
        # Register tool evolution
        self.evolved_tools[tool_name] = ToolEvolution(
            tool_name=tool_name,
            version=1.0,
            creation_time=time.time(),
            usage_count=0,
            average_time_saved=0.0
        )
        
        print(f"[EVOLVED] Created {tool_name} for pattern {signature}")
        self._save_evolution_state()
        
        return tool_name
    
    def _generate_tool_code(self, task_type: str, details: Dict[str, Any]) -> str:
        """Generate tool code for pattern"""
        
        templates = {
            "file_ops": '''#!/usr/bin/env python3
"""Auto-evolved tool for file operations pattern"""

import sys
from pathlib import Path

def execute_{task_type}_{signature}(target_path: str = "."):
    """Automated {operation} operation"""
    path = Path(target_path)
    
    # Pattern: {pattern}
    results = []
    for file in path.glob("{file_pattern}"):
        # Perform operation
        results.append(str(file))
    
    return results

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    results = execute_{task_type}_{signature}(target)
    print(f"Processed {{len(results)}} items")
''',
            
            "search": '''#!/usr/bin/env python3
"""Auto-evolved tool for search pattern"""

import sys
import re
from pathlib import Path

def search_{signature}(pattern: str, scope: str = "."):
    """Automated search for {search_type}"""
    
    results = []
    search_path = Path(scope)
    
    # Pattern-specific search
    for file in search_path.rglob("*"):
        if file.is_file():
            try:
                content = file.read_text()
                if re.search(pattern, content):
                    results.append(str(file))
            except:
                pass
    
    return results

if __name__ == "__main__":
    pattern = sys.argv[1] if len(sys.argv) > 1 else r".*"
    results = search_{signature}(pattern)
    for result in results:
        print(result)
''',
            
            "analysis": '''#!/usr/bin/env python3
"""Auto-evolved tool for analysis pattern"""

import json
import sys
from pathlib import Path

def analyze_{signature}(input_file: str):
    """Automated {analysis_type} analysis"""
    
    # Load input
    with open(input_file, 'r') as f:
        data = json.load(f) if input_file.endswith('.json') else f.read()
    
    # Pattern-specific analysis
    results = {{
        "type": "{analysis_type}",
        "metrics": {{}},
        "insights": []
    }}
    
    # Perform analysis
    if isinstance(data, dict):
        results["metrics"]["keys"] = len(data.keys())
    elif isinstance(data, list):
        results["metrics"]["items"] = len(data)
    
    return results

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.json"
    results = analyze_{signature}(input_file)
    print(json.dumps(results, indent=2))
'''
        }
        
        # Get template and format
        template = templates.get(task_type, templates["file_ops"])
        
        # Format with details
        formatted = template.format(
            task_type=task_type,
            signature=details.get('signature', 'auto'),
            operation=details.get('operation', 'process'),
            pattern=details.get('pattern', '*'),
            file_pattern=details.get('file_pattern', '*.py'),
            search_type=details.get('search_type', 'regex'),
            analysis_type=details.get('analysis_type', 'structural')
        )
        
        return formatted
    
    def _evolve_existing_tool(self, pattern: PatternDetection):
        """Evolve an existing tool based on usage patterns"""
        
        if not pattern.tool_path:
            return
        
        tool_path = Path(pattern.tool_path)
        if not tool_path.exists():
            return
        
        # Read current tool
        with open(tool_path, 'r', encoding='utf-8') as f:
            current_code = f.read()
        
        # Analyze recent usage for optimization opportunities
        recent_tasks = [t for t in self.task_history[-20:] 
                       if t.get('signature') == pattern.pattern_id]
        
        if len(recent_tasks) < 5:
            return  # Not enough data
        
        # Detect optimization opportunities
        optimizations = []
        
        # Check for common parameters
        param_usage = defaultdict(int)
        for task in recent_tasks:
            for key, value in task.get('details', {}).items():
                param_usage[f"{key}={value}"] += 1
        
        # Find most common parameters (could be defaults)
        common_params = [param for param, count in param_usage.items() 
                        if count > len(recent_tasks) * 0.7]
        
        if common_params:
            optimizations.append(f"# Common parameters: {', '.join(common_params)}")
        
        # Check for performance patterns
        if pattern.frequency > 20:
            optimizations.append("# Consider caching results")
        
        if pattern.frequency > 50:
            optimizations.append("# Consider parallel processing")
        
        # Apply optimizations
        if optimizations:
            # Add optimization comments to tool
            optimization_block = "\n".join(optimizations)
            evolved_code = current_code.replace(
                '"""',
                f'"""\n{optimization_block}\n',
                1
            )
            
            # Increment version
            evolved_code = re.sub(
                r'version = (\d+\.\d+)',
                lambda m: f"version = {float(m.group(1)) + 0.1:.1f}",
                evolved_code
            )
            
            # Write evolved tool
            with open(tool_path, 'w', encoding='utf-8') as f:
                f.write(evolved_code)
            
            print(f"[EVOLVED] Updated {pattern.pattern_id} with {len(optimizations)} optimizations")
            
            # Update evolution tracking
            if pattern.pattern_id in self.evolved_tools:
                tool = self.evolved_tools[pattern.pattern_id]
                tool.version += 0.1
                tool.evolution_history.append({
                    "timestamp": time.time(),
                    "optimizations": optimizations,
                    "frequency_at_evolution": pattern.frequency
                })
    
    def get_pattern_insights(self) -> Dict[str, Any]:
        """Get insights about detected patterns and evolved tools"""
        
        return {
            "total_patterns": len(self.detected_patterns),
            "patterns_with_tools": sum(1 for p in self.detected_patterns.values() if p.tool_exists),
            "total_evolved_tools": len(self.evolved_tools),
            "average_efficiency_gain": sum(p.efficiency_gain for p in self.detected_patterns.values()) / max(1, len(self.detected_patterns)),
            "most_frequent_pattern": max(self.detected_patterns.values(), key=lambda p: p.frequency).pattern_type if self.detected_patterns else None,
            "total_task_observations": len(self.task_history),
            "evolution_velocity": len(self.evolved_tools) / max(1, len(self.task_history) / 100)
        }
    
    def suggest_tool_creation(self) -> List[Dict[str, Any]]:
        """Suggest tools that should be created based on patterns"""
        
        suggestions = []
        
        # Analyze pattern memory for near-threshold patterns
        for task_type, signatures in self.pattern_memory.items():
            for signature, frequency in signatures.items():
                if frequency == self.evolution_threshold - 1:
                    suggestions.append({
                        "task_type": task_type,
                        "signature": signature,
                        "frequency": frequency,
                        "one_more_to_evolve": True,
                        "estimated_time_savings": f"{frequency * 5}s per session"
                    })
        
        return suggestions
    
    def _save_evolution_state(self):
        """Save evolution state to disk"""
        
        state_file = self.evolution_path / "evolution_state.json"
        
        state = {
            "patterns": {
                sig: {
                    "type": p.pattern_type,
                    "frequency": p.frequency,
                    "tool_exists": p.tool_exists,
                    "tool_path": p.tool_path,
                    "efficiency_gain": p.efficiency_gain
                }
                for sig, p in self.detected_patterns.items()
            },
            "tools": {
                name: {
                    "version": t.version,
                    "usage_count": t.usage_count,
                    "average_time_saved": t.average_time_saved
                }
                for name, t in self.evolved_tools.items()
            },
            "statistics": self.get_pattern_insights()
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    
    def _load_evolution_state(self):
        """Load evolution state from disk"""
        
        state_file = self.evolution_path / "evolution_state.json"
        
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                # Restore patterns
                for sig, data in state.get("patterns", {}).items():
                    self.detected_patterns[sig] = PatternDetection(
                        pattern_id=sig,
                        pattern_type=data["type"],
                        frequency=data["frequency"],
                        last_seen=time.time(),
                        tool_exists=data["tool_exists"],
                        tool_path=data.get("tool_path"),
                        efficiency_gain=data.get("efficiency_gain", 1.0)
                    )
                
                print(f"[LOAD] Restored {len(self.detected_patterns)} patterns")
                
            except Exception as e:
                print(f"[WARNING] Could not load evolution state: {e}")

# Integration with self-improvement framework
class EvolutionIntegration:
    """Integrate pattern evolution with velocity improvement"""
    
    @staticmethod
    def hook_into_velocity(evolution_engine: PatternEvolutionEngine):
        """Hook pattern evolution into velocity optimization"""
        
        # This would be called by velocity_optimizer during improvement cycles
        insights = evolution_engine.get_pattern_insights()
        
        if insights["evolution_velocity"] > 0.5:
            # High evolution velocity - system is learning fast
            return {"evolution_boost": 1.2}
        
        return {"evolution_boost": 1.0}
    
    @staticmethod  
    def auto_evolve_during_improvement(evolution_engine: PatternEvolutionEngine):
        """Automatically evolve tools during improvement cycles"""
        
        # Check for patterns near threshold
        suggestions = evolution_engine.suggest_tool_creation()
        
        for suggestion in suggestions:
            if suggestion.get("one_more_to_evolve"):
                # Simulate one more occurrence to trigger evolution
                evolution_engine.observe_task(
                    suggestion["task_type"],
                    {"auto_evolved": True, "signature": suggestion["signature"]}
                )

# CLI interface
if __name__ == "__main__":
    import sys
    
    engine = PatternEvolutionEngine()
    
    if len(sys.argv) < 2:
        print("[EVOLUTION] Pattern Evolution Engine")
        print("Commands:")
        print("  observe <type> <details_json>  - Observe a task")
        print("  insights                        - Get pattern insights")
        print("  suggest                         - Suggest tool creation")
        print("  evolve                          - Force evolution check")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "observe" and len(sys.argv) > 3:
        task_type = sys.argv[2]
        details = json.loads(sys.argv[3])
        tool_name = engine.observe_task(task_type, details)
        if tool_name:
            print(f"[EVOLVED] Created tool: {tool_name}")
        else:
            print(f"[OBSERVED] Task recorded")
    
    elif cmd == "insights":
        insights = engine.get_pattern_insights()
        print(f"[INSIGHTS] {json.dumps(insights, indent=2)}")
    
    elif cmd == "suggest":
        suggestions = engine.suggest_tool_creation()
        for s in suggestions:
            print(f"[SUGGEST] {s['task_type']}: {s['frequency']}/{engine.evolution_threshold} occurrences")
    
    elif cmd == "evolve":
        integration = EvolutionIntegration()
        integration.auto_evolve_during_improvement(engine)
        print("[EVOLVE] Evolution cycle complete")
    
    else:
        print(f"[ERROR] Unknown command: {cmd}")