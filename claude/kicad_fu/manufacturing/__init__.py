"""
KiCad-Fu Manufacturing - Intelligent PCB Manufacturing Integration

Provides cognitive-enhanced manufacturing support with multiple fab houses.
"""

from .aisler_optimizer import AislerOptimizer
from .fabrication_validator import FabricationValidator

# Optional manufacturing planner - create placeholder if missing
try:
    from .manufacturing_planner import ManufacturingPlanner
except ImportError:
    class ManufacturingPlanner:
        """Placeholder for manufacturing planner"""
        def __init__(self, context):
            self.context = context

__all__ = [
    "AislerOptimizer",
    "FabricationValidator", 
    "ManufacturingPlanner"
]