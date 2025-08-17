"""
KiCad-Fu Tools - Cognitive-Enhanced KiCad Operations

Provides intelligent KiCad operation tools with learning and optimization.
"""

from .project_tools import ProjectTools

# Optional tools - create placeholder classes if modules don't exist
try:
    from .analysis_tools import AnalysisTools
except ImportError:
    class AnalysisTools:
        """Placeholder for missing analysis tools"""
        def __init__(self, context):
            self.context = context

try:
    from .optimization_tools import OptimizationTools
except ImportError:
    class OptimizationTools:
        """Placeholder for missing optimization tools"""
        def __init__(self, context):
            self.context = context

__all__ = [
    "ProjectTools",
    "AnalysisTools", 
    "OptimizationTools"
]