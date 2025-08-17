#!/usr/bin/env python3
"""
KiCad-Fu Context Manager - Cognitive Context for KiCad Operations

Maintains intelligent context about KiCad projects, operations, and learning state.
Integrates with our autonomous learning architecture.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from collections import defaultdict, deque

# Import our cognitive systems
sys.path.append(str(Path(__file__).parent.parent))
try:
    from brain_systems.core_systems.cognitive_performance_profiler import CognitivePerformanceProfiler
    from brain_systems.core_systems.predictive_cognitive_planning import PredictiveCognitivePlanning
    from brain_systems.core_systems.failure_driven_evolution import FailureDrivenEvolution
except ImportError:
    # Fallback for missing cognitive systems
    CognitivePerformanceProfiler = None
    PredictiveCognitivePlanning = None
    FailureDrivenEvolution = None

@dataclass
class KiCadProject:
    """KiCad project information with cognitive enhancements"""
    name: str
    path: str
    last_modified: str
    components_count: int = 0
    nets_count: int = 0
    layers_count: int = 0
    complexity_score: float = 0.0
    design_rules_status: str = "unknown"
    last_opened: Optional[str] = None
    predicted_next_operations: List[str] = field(default_factory=list)
    learned_patterns: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KiCadOperation:
    """KiCad operation with cognitive tracking"""
    operation_id: str
    operation_type: str
    project_name: str
    start_time: str
    end_time: Optional[str] = None
    success: bool = True
    duration_ms: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    lessons_learned: List[str] = field(default_factory=list)
    optimization_opportunities: List[str] = field(default_factory=list)

class KiCadContext:
    """Intelligent context manager for KiCad operations with cognitive integration"""
    
    def __init__(self, config=None):
        from .config import get_config
        self.config = config or get_config()
        
        # Context storage
        self.current_project: Optional[KiCadProject] = None
        self.active_operations: Dict[str, KiCadOperation] = {}
        self.project_registry: Dict[str, KiCadProject] = {}
        self.operation_history: deque[KiCadOperation] = deque(maxlen=1000)
        
        # Cognitive integration
        self.profiler = None
        self.predictor = None
        self.evolution = None
        
        if self.config.performance_profiling and CognitivePerformanceProfiler:
            try:
                self.profiler = CognitivePerformanceProfiler(self.config.project_root)
            except:
                self.profiler = None
            
        if self.config.enable_predictive_planning and PredictiveCognitivePlanning:
            try:
                self.predictor = PredictiveCognitivePlanning(self.config.project_root)
            except:
                self.predictor = None
            
        if self.config.enable_failure_evolution and FailureDrivenEvolution:
            try:
                self.evolution = FailureDrivenEvolution(self.config.project_root)
            except:
                self.evolution = None
        
        # Learning state
        self.learned_patterns = defaultdict(list)
        self.optimization_cache = {}
        self.prediction_cache = {}
        
        # Load existing context
        self._load_context()
        
    def discover_projects(self) -> List[KiCadProject]:
        """Discover KiCad projects in search paths with cognitive analysis"""
        projects = []
        
        print("[KICAD_FU] Discovering KiCad projects...")
        
        for search_path in self.config.kicad_search_paths:
            search_path = Path(search_path)
            if not search_path.exists():
                continue
                
            # Find .kicad_pro files
            for pro_file in search_path.rglob("*.kicad_pro"):
                try:
                    project = self._analyze_project(pro_file)
                    if project:
                        projects.append(project)
                        self.project_registry[project.name] = project
                except Exception as e:
                    print(f"[KICAD_FU] Error analyzing project {pro_file}: {e}")
                    
        print(f"[KICAD_FU] Discovered {len(projects)} KiCad projects")
        
        # Apply cognitive enhancements
        self._enhance_project_discovery(projects)
        
        return projects
        
    def _analyze_project(self, pro_file: Path) -> Optional[KiCadProject]:
        """Analyze a KiCad project file"""
        try:
            with open(pro_file, 'r') as f:
                project_data = json.load(f)
        except:
            # Skip invalid project files
            return None
            
        project_dir = pro_file.parent
        project_name = pro_file.stem
        
        # Check for associated files
        pcb_file = project_dir / f"{project_name}.kicad_pcb"
        sch_file = project_dir / f"{project_name}.kicad_sch"
        
        # Basic project info
        project = KiCadProject(
            name=project_name,
            path=str(project_dir),
            last_modified=datetime.fromtimestamp(pro_file.stat().st_mtime).isoformat(),
            complexity_score=self._calculate_complexity_score(project_dir, project_name)
        )
        
        # Analyze PCB if available
        if pcb_file.exists():
            pcb_info = self._analyze_pcb_file(pcb_file)
            project.components_count = pcb_info.get('components', 0)
            project.nets_count = pcb_info.get('nets', 0)
            project.layers_count = pcb_info.get('layers', 0)
            
        return project
        
    def _analyze_pcb_file(self, pcb_file: Path) -> Dict[str, int]:
        """Quick analysis of PCB file"""
        try:
            # Use our existing PCB parser
            sys.path.append(str(Path(__file__).parent.parent / "tools"))
            from kicad_pcb_parser import KiCadPCBParser
            
            parser = KiCadPCBParser(str(pcb_file))
            
            return {
                'components': len(parser.components),
                'nets': len(parser.nets),
                'layers': len(getattr(parser, 'layers', []))
            }
        except Exception as e:
            print(f"[KICAD_FU] Error parsing PCB {pcb_file}: {e}")
            return {'components': 0, 'nets': 0, 'layers': 0}
            
    def _calculate_complexity_score(self, project_dir: Path, project_name: str) -> float:
        """Calculate project complexity score"""
        complexity = 0.0
        
        # File count factor
        file_count = len(list(project_dir.glob("*")))
        complexity += min(file_count / 20.0, 1.0) * 0.3
        
        # PCB size factor (if available)
        pcb_file = project_dir / f"{project_name}.kicad_pcb"
        if pcb_file.exists():
            pcb_size = pcb_file.stat().st_size
            complexity += min(pcb_size / (1024 * 1024), 1.0) * 0.4  # Normalize to MB
            
        # Schematic complexity
        sch_file = project_dir / f"{project_name}.kicad_sch"
        if sch_file.exists():
            complexity += 0.3
            
        return min(complexity, 1.0)
        
    def _enhance_project_discovery(self, projects: List[KiCadProject]):
        """Apply cognitive enhancements to discovered projects"""
        if not self.predictor:
            return
            
        # Predict likely next operations for each project
        for project in projects:
            context = {
                'project_name': project.name,
                'complexity': project.complexity_score,
                'components': project.components_count,
                'last_modified': project.last_modified
            }
            
            # Use predictive planning to anticipate needs
            try:
                predictions = self.predictor.predict_cognitive_needs(context, 'short_term')
                project.predicted_next_operations = [pred.predicted_need for pred in predictions[:3]]
            except Exception as e:
                print(f"[KICAD_FU] Prediction error for {project.name}: {e}")
                
    def start_operation(self, operation_type: str, project_name: str = None, 
                       context: Dict[str, Any] = None) -> str:
        """Start tracking a KiCad operation with cognitive profiling"""
        operation_id = f"{operation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        operation = KiCadOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            project_name=project_name or "unknown",
            start_time=datetime.now().isoformat(),
            context=context or {}
        )
        
        self.active_operations[operation_id] = operation
        
        # Cognitive profiling
        if self.profiler:
            # Use profiler decorator for the operation
            pass  # Will be implemented in operation handlers
            
        print(f"[KICAD_FU] Started operation: {operation_type} ({operation_id})")
        
        return operation_id
        
    def end_operation(self, operation_id: str, success: bool = True, 
                     lessons_learned: List[str] = None) -> Optional[KiCadOperation]:
        """End tracking a KiCad operation and apply learning"""
        if operation_id not in self.active_operations:
            return None
            
        operation = self.active_operations[operation_id]
        operation.end_time = datetime.now().isoformat()
        operation.success = success
        operation.lessons_learned = lessons_learned or []
        
        # Calculate duration
        start_time = datetime.fromisoformat(operation.start_time)
        end_time = datetime.fromisoformat(operation.end_time)
        operation.duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Move to history
        self.operation_history.append(operation)
        del self.active_operations[operation_id]
        
        # Apply cognitive learning
        self._apply_operation_learning(operation)
        
        print(f"[KICAD_FU] Completed operation: {operation.operation_type} "
              f"({operation.duration_ms:.1f}ms, {'success' if success else 'failed'})")
        
        return operation
        
    def _apply_operation_learning(self, operation: KiCadOperation):
        """Apply cognitive learning from completed operation"""
        
        # Record in performance profiler
        if self.profiler:
            try:
                self.profiler.record_metric(operation)
            except Exception as e:
                print(f"[KICAD_FU] Profiling error: {e}")
                
        # Record failures for evolution
        if not operation.success and self.evolution:
            try:
                error_info = {
                    'error_type': f"KiCadOperation:{operation.operation_type}",
                    'error_message': f"Operation {operation.operation_type} failed",
                    'operation': operation.operation_type,
                    'context': operation.context
                }
                self.evolution.analyze_failure(error_info)
            except Exception as e:
                print(f"[KICAD_FU] Evolution learning error: {e}")
                
        # Learn patterns
        pattern_key = f"{operation.operation_type}_{operation.project_name}"
        self.learned_patterns[pattern_key].append({
            'duration': operation.duration_ms,
            'success': operation.success,
            'context': operation.context,
            'timestamp': operation.end_time
        })
        
    def get_project_predictions(self, project_name: str) -> List[str]:
        """Get predictions for a specific project"""
        if project_name in self.project_registry:
            return self.project_registry[project_name].predicted_next_operations
        return []
        
    def get_operation_stats(self) -> Dict[str, Any]:
        """Get operation statistics"""
        if not self.operation_history:
            return {'total_operations': 0}
            
        operations = list(self.operation_history)
        
        # Calculate statistics
        total_ops = len(operations)
        successful_ops = len([op for op in operations if op.success])
        avg_duration = sum(op.duration_ms for op in operations) / total_ops
        
        # Most common operations
        operation_counts = defaultdict(int)
        for op in operations:
            operation_counts[op.operation_type] += 1
            
        return {
            'total_operations': total_ops,
            'success_rate': successful_ops / total_ops if total_ops > 0 else 0,
            'average_duration_ms': avg_duration,
            'most_common_operations': dict(sorted(operation_counts.items(), 
                                                key=lambda x: x[1], reverse=True)[:5])
        }
        
    def _load_context(self):
        """Load saved context from disk"""
        context_file = Path(self.config.project_root) / 'claude' / 'kicad_fu' / 'context.json'
        
        if not context_file.exists():
            return
            
        try:
            with open(context_file, 'r') as f:
                data = json.load(f)
                
            # Restore project registry
            if 'projects' in data:
                for proj_data in data['projects']:
                    project = KiCadProject(**proj_data)
                    self.project_registry[project.name] = project
                    
            # Restore learned patterns
            if 'learned_patterns' in data:
                self.learned_patterns = defaultdict(list, data['learned_patterns'])
                
            print(f"[KICAD_FU] Loaded context: {len(self.project_registry)} projects")
            
        except Exception as e:
            print(f"[KICAD_FU] Error loading context: {e}")
            
    def save_context(self):
        """Save context to disk"""
        context_file = Path(self.config.project_root) / 'claude' / 'kicad_fu' / 'context.json'
        context_file.parent.mkdir(parents=True, exist_ok=True)
        
        context_data = {
            'timestamp': datetime.now().isoformat(),
            'projects': [asdict(proj) for proj in self.project_registry.values()],
            'learned_patterns': dict(self.learned_patterns),
            'stats': self.get_operation_stats()
        }
        
        try:
            with open(context_file, 'w') as f:
                json.dump(context_data, f, indent=2)
            print(f"[KICAD_FU] Saved context to {context_file}")
        except Exception as e:
            print(f"[KICAD_FU] Error saving context: {e}")
            
    def __enter__(self):
        """Context manager entry"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        # End any active operations
        for operation_id in list(self.active_operations.keys()):
            self.end_operation(operation_id, success=(exc_type is None))
            
        # Save context
        self.save_context()