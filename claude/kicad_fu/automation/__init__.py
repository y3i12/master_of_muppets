"""
KiCad-Fu Production Automation - Intelligent Manufacturing Workflows

Provides cognitive-enhanced production automation with KiBot integration and CI/CD workflows.
"""

from .kibot_integration import KiBotAutomator

# Optional automation modules - create placeholders if missing
try:
    from .workflow_generator import WorkflowGenerator
except ImportError:
    class WorkflowGenerator:
        """Placeholder for workflow generator"""
        def __init__(self, context):
            self.context = context

try:
    from .fabrication_pipeline import FabricationPipeline
except ImportError:
    class FabricationPipeline:
        """Placeholder for fabrication pipeline"""
        def __init__(self, context):
            self.context = context

__all__ = [
    "KiBotAutomator",
    "WorkflowGenerator", 
    "FabricationPipeline"
]