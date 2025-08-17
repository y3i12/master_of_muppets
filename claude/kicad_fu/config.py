#!/usr/bin/env python3
"""
KiCad-Fu Configuration - Cognitive-Enhanced KiCad Settings

Integrates with our autonomous learning architecture for adaptive configuration.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class KiCadFuConfig:
    """Configuration for KiCad-Fu cognitive server"""
    
    # KiCad Settings
    kicad_executable: str = "kicad"
    kicad_version: str = "8.0"
    kicad_search_paths: List[str] = None
    
    # Project Settings
    project_root: str = None
    master_of_muppets_path: str = "CADfiles/MasterOfMuppets"
    
    # Cognitive Integration
    brain_systems_path: str = "claude/brain_systems"
    enable_predictive_planning: bool = True
    enable_failure_evolution: bool = True
    enable_cross_domain_learning: bool = True
    
    # MCP Server Settings
    server_host: str = "localhost"
    server_port: int = 8000
    max_concurrent_operations: int = 10
    
    # Learning Parameters
    performance_profiling: bool = True
    knowledge_crystallization: bool = True
    adaptive_optimization: bool = True
    
    def __post_init__(self):
        """Initialize default values and validate configuration"""
        if self.project_root is None:
            self.project_root = str(Path.cwd())
            
        if self.kicad_search_paths is None:
            self.kicad_search_paths = [
                os.path.join(self.project_root, "CADfiles"),
                os.path.join(self.project_root, "PCB"),
                os.path.join(self.project_root, "Electronics"),
                os.path.expanduser("~/KiCad"),
                os.path.expanduser("~/Documents/KiCad")
            ]
            
        # Ensure paths exist or are creatable
        self._validate_paths()
        
    def _validate_paths(self):
        """Validate and create necessary paths"""
        # Ensure brain systems path exists
        brain_path = Path(self.project_root) / self.brain_systems_path
        brain_path.mkdir(parents=True, exist_ok=True)
        
        # Check KiCad executable
        if not self._check_kicad_available():
            print(f"[KICAD_FU] Warning: KiCad executable '{self.kicad_executable}' not found in PATH")
            
    def _check_kicad_available(self) -> bool:
        """Check if KiCad is available"""
        import shutil
        return shutil.which(self.kicad_executable) is not None
        
    def get_master_of_muppets_path(self) -> Path:
        """Get full path to Master of Muppets project"""
        return Path(self.project_root) / self.master_of_muppets_path
        
    def get_brain_systems_path(self) -> Path:
        """Get full path to brain systems"""
        return Path(self.project_root) / self.brain_systems_path
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)
        
    def save_config(self, config_path: Optional[str] = None) -> str:
        """Save configuration to file"""
        if config_path is None:
            config_path = Path(self.project_root) / 'claude' / 'kicad_fu' / 'config.json'
            
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'config': self.to_dict()
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
            
        return str(config_path)
        
    @classmethod
    def load_config(cls, config_path: str) -> 'KiCadFuConfig':
        """Load configuration from file"""
        with open(config_path, 'r') as f:
            data = json.load(f)
            
        config_dict = data.get('config', {})
        return cls(**config_dict)
        
    @classmethod
    def from_environment(cls) -> 'KiCadFuConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Override with environment variables
        if os.getenv('KICAD_EXECUTABLE'):
            config.kicad_executable = os.getenv('KICAD_EXECUTABLE')
            
        if os.getenv('KICAD_SEARCH_PATHS'):
            paths = os.getenv('KICAD_SEARCH_PATHS').split(':')
            config.kicad_search_paths = [p.strip() for p in paths if p.strip()]
            
        if os.getenv('PROJECT_ROOT'):
            config.project_root = os.getenv('PROJECT_ROOT')
            
        if os.getenv('KICAD_FU_PORT'):
            config.server_port = int(os.getenv('KICAD_FU_PORT'))
            
        # Cognitive settings
        config.enable_predictive_planning = os.getenv('ENABLE_PREDICTIVE', 'true').lower() == 'true'
        config.enable_failure_evolution = os.getenv('ENABLE_EVOLUTION', 'true').lower() == 'true'
        config.enable_cross_domain_learning = os.getenv('ENABLE_CROSS_DOMAIN', 'true').lower() == 'true'
        
        return config
        
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"""KiCad-Fu Configuration:
  KiCad: {self.kicad_executable} v{self.kicad_version}
  Project Root: {self.project_root}
  Search Paths: {len(self.kicad_search_paths)} configured
  Server: {self.server_host}:{self.server_port}
  Cognitive Features: {'✓' if self.enable_predictive_planning else '✗'} Predictive, {'✓' if self.enable_failure_evolution else '✗'} Evolution, {'✓' if self.enable_cross_domain_learning else '✗'} Cross-Domain"""

# Global configuration instance
_config_instance = None

def get_config() -> KiCadFuConfig:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = KiCadFuConfig.from_environment()
    return _config_instance

def set_config(config: KiCadFuConfig):
    """Set global configuration instance"""
    global _config_instance
    _config_instance = config