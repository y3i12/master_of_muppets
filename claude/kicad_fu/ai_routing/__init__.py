#!/usr/bin/env python3
"""
AI-Enhanced Routing and Placement Module
Complete AI-driven PCB layout automation with cognitive learning
"""

from .placement_optimizer import CognitivePlacementEngine, Component, Connection, PlacementResult
from .routing_engine import CognitiveRoutingEngine, Net, RoutingResult, RoutingConstraints
from .ai_layout_interface import AILayoutInterface

__all__ = [
    'CognitivePlacementEngine',
    'CognitiveRoutingEngine', 
    'AILayoutInterface',
    'Component',
    'Connection', 
    'Net',
    'PlacementResult',
    'RoutingResult',
    'RoutingConstraints'
]

__version__ = "1.0.0"
__author__ = "Claude - KiCad-Fu Cognitive System"