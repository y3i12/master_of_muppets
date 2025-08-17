"""
KiCad-Fu Resources - Cognitive-Enhanced Data Access

Provides intelligent access to KiCad project data with learning enhancements.
"""

from .projects import ProjectResource

# Optional resources - create placeholder classes if modules don't exist
try:
    from .analysis import AnalysisResource
except ImportError:
    class AnalysisResource:
        """Placeholder for missing analysis resource"""
        def __init__(self, context):
            self.context = context

try:
    from .insights import InsightResource
except ImportError:
    class InsightResource:
        """Placeholder for missing insights resource"""
        def __init__(self, context):
            self.context = context

__all__ = [
    "ProjectResource",
    "AnalysisResource", 
    "InsightResource"
]