"""
KiCad-Fu: The Art of Intelligent KiCad Interaction

A cognitive KiCad MCP server that integrates with our autonomous learning architecture
to provide intelligent, learning-enhanced PCB design automation.

Built during Season 02, Episode 04: KiCad-Fu Training
"""

__version__ = "1.0.0"
__author__ = "Claude (Autonomous Learning Architecture)"

from .server import KiCadFuServer
from .config import KiCadFuConfig
from .context import KiCadContext

__all__ = [
    "KiCadFuServer",
    "KiCadFuConfig", 
    "KiCadContext"
]