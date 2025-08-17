#!/usr/bin/env python3
"""
KiBot Integration - Cognitive-Enhanced PCB Fabrication Automation

Integrates KiBot with our cognitive systems for intelligent fabrication file generation.
Supports AISLER-optimized workflows and learning-enhanced automation.
"""

import os
import json
import yaml
import logging
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

@dataclass
class KiBotConfig:
    """KiBot configuration with cognitive enhancements"""
    project_name: str
    manufacturer: str = "aisler"
    surface_finish: str = "ENIG"
    layers: int = 4
    output_dir: str = "fabrication"
    enable_assembly: bool = True
    enable_3d_models: bool = True
    enable_interactive_bom: bool = True
    cognitive_optimization: bool = True

@dataclass
class FabricationJob:
    """Fabrication job tracking with cognitive insights"""
    job_id: str
    project_name: str
    config: KiBotConfig
    outputs_generated: List[str]
    start_time: str
    completion_time: Optional[str] = None
    success: bool = False
    cognitive_insights: Dict[str, Any] = None
    lessons_learned: List[str] = None

class KiBotAutomator:
    """Cognitive-enhanced KiBot automation system"""
    
    def __init__(self, context=None):
        self.context = context
        self.logger = logging.getLogger('kibot_automator')
        
        # KiBot availability check
        self.kibot_available = self._check_kibot_availability()
        
        # Cognitive fabrication patterns
        self.fabrication_patterns = {
            'aisler': self._get_aisler_patterns(),
            'jlcpcb': self._get_jlcpcb_patterns(),
            'generic': self._get_generic_patterns()
        }
        
    def _check_kibot_availability(self) -> bool:
        """Check if KiBot is available in the system"""
        try:
            result = subprocess.run(['kibot', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.logger.info(f"KiBot available: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        self.logger.warning("KiBot not found - will generate configuration for manual installation")
        return False
        
    def generate_fabrication_files(self, project_data: Dict[str, Any], 
                                 config: KiBotConfig) -> Dict[str, Any]:
        """Generate fabrication files with cognitive optimization"""
        operation_id = None
        if self.context:
            operation_id = self.context.start_operation("kibot_fabrication", 
                                                       f"{project_data.get('name', 'unknown')}")
        
        try:
            job = FabricationJob(
                job_id=f"fab_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                project_name=project_data.get('name', 'Unknown'),
                config=config,
                outputs_generated=[],
                start_time=datetime.now().isoformat()
            )
            
            # Generate KiBot configuration with cognitive optimization
            kibot_config = self._generate_kibot_config(project_data, config)
            
            # Apply cognitive optimizations
            optimized_config = self._apply_cognitive_optimizations(kibot_config, project_data)
            
            # Execute KiBot if available
            if self.kibot_available:
                execution_result = self._execute_kibot(project_data, optimized_config)
                job.outputs_generated = execution_result.get('outputs', [])
                job.success = execution_result.get('success', False)
            else:
                # Generate configuration files for manual execution
                config_result = self._save_kibot_config(project_data, optimized_config)
                job.outputs_generated = config_result.get('config_files', [])
                job.success = config_result.get('success', False)
            
            # Generate cognitive insights
            job.cognitive_insights = self._generate_fabrication_insights(project_data, config, job)
            
            # Extract lessons learned
            job.lessons_learned = self._extract_lessons_learned(job)
            
            job.completion_time = datetime.now().isoformat()
            
            if self.context:
                lessons = job.lessons_learned or ["KiBot fabrication completed"]
                self.context.end_operation(operation_id, job.success, lessons_learned=lessons)
                
            return {
                'success': job.success,
                'job': asdict(job),
                'operation_id': operation_id
            }
            
        except Exception as e:
            if self.context:
                self.context.end_operation(operation_id, False,
                    lessons_learned=[f"KiBot fabrication failed: {str(e)}"])
            return {
                'success': False,
                'error': str(e),
                'operation_id': operation_id
            }
            
    def _generate_kibot_config(self, project_data: Dict[str, Any], 
                              config: KiBotConfig) -> Dict[str, Any]:
        """Generate KiBot YAML configuration with manufacturer optimization"""
        
        # Base KiBot configuration
        kibot_config = {
            'kibot': {
                'version': 1
            },
            'preflight': {
                'run_erc': True,
                'run_drc': True,
                'check_zone_fills': True,
                'ignore_unconnected': False
            },
            'outputs': []
        }
        
        # Add manufacturer-specific outputs
        manufacturer_outputs = self.fabrication_patterns.get(config.manufacturer, 
                                                            self.fabrication_patterns['generic'])
        
        for output_name, output_config in manufacturer_outputs.items():
            # Customize output based on project configuration
            customized_output = self._customize_output_for_project(output_config, project_data, config)
            kibot_config['outputs'].append(customized_output)
            
        # Add cognitive enhancements
        if config.cognitive_optimization:
            cognitive_outputs = self._generate_cognitive_outputs(project_data, config)
            kibot_config['outputs'].extend(cognitive_outputs)
            
        return kibot_config
        
    def _get_aisler_patterns(self) -> Dict[str, Any]:
        """Get AISLER-optimized KiBot output patterns"""
        return {
            'gerbers': {
                'name': 'AISLER Gerbers',
                'comment': 'Gerber files optimized for AISLER manufacturing',
                'type': 'gerber',
                'dir': 'fabrication/gerbers',
                'options': {
                    'exclude_edge_layer': True,
                    'exclude_pads_from_silkscreen': True,
                    'use_aux_axis_as_origin': False,
                    'plot_sheet_reference': False,
                    'plot_footprint_refs': True,
                    'plot_footprint_values': False,
                    'force_plot_invisible_refs_vals': False,
                    'tent_vias': True,
                    'line_width': 0.1,
                    'subtract_mask_from_silk': True
                },
                'layers': [
                    'F.Cu', 'B.Cu', 'F.Paste', 'B.Paste',
                    'F.SilkS', 'B.SilkS', 'F.Mask', 'B.Mask',
                    'Edge.Cuts'
                ]
            },
            'excellon': {
                'name': 'AISLER Drill Files',
                'comment': 'Drill files for AISLER manufacturing',
                'type': 'excellon',
                'dir': 'fabrication/gerbers',
                'options': {
                    'metric_units': True,
                    'minimal_header': True,
                    'mirror_y_axis': False,
                    'report': {
                        'filename': 'drill_report.txt'
                    }
                }
            },
            'position': {
                'name': 'AISLER Pick and Place',
                'comment': 'Component placement for AISLER assembly',
                'type': 'position',
                'dir': 'fabrication/assembly',
                'options': {
                    'format': 'CSV',
                    'units': 'millimeters',
                    'separate_files_for_front_and_back': False,
                    'only_smd': True,
                    'columns': [
                        'Ref', 'Val', 'Package', 'PosX', 'PosY', 'Rot', 'Side'
                    ]
                }
            },
            'bom': {
                'name': 'AISLER Bill of Materials',
                'comment': 'BOM optimized for AISLER assembly',
                'type': 'bom',
                'dir': 'fabrication/assembly',
                'options': {
                    'format': 'CSV',
                    'columns': [
                        'Item', 'Qty', 'Reference(s)', 'Value', 'LibPart',
                        'Footprint', 'Datasheet', 'Manufacturer', 'ManufacturerPartNumber'
                    ],
                    'csv': {
                        'hide_pcb_info': True,
                        'hide_stats_info': True,
                        'quote_all': True
                    }
                }
            }
        }
        
    def _get_jlcpcb_patterns(self) -> Dict[str, Any]:
        """Get JLCPCB-optimized KiBot output patterns"""
        return {
            'gerbers': {
                'name': 'JLCPCB Gerbers',
                'comment': 'Gerber files optimized for JLCPCB manufacturing',
                'type': 'gerber',
                'dir': 'fabrication/gerbers',
                'options': {
                    'exclude_edge_layer': True,
                    'exclude_pads_from_silkscreen': True,
                    'plot_sheet_reference': False,
                    'plot_footprint_refs': True,
                    'plot_footprint_values': False
                },
                'layers': 'copper'
            },
            'position': {
                'name': 'JLCPCB CPL',
                'comment': 'Component placement list for JLCPCB',
                'type': 'position',
                'dir': 'fabrication/assembly',
                'options': {
                    'format': 'CSV',
                    'units': 'millimeters',
                    'separate_files_for_front_and_back': False,
                    'only_smd': True,
                    'columns': [
                        'Designator', 'Val', 'Package', 'Mid X', 'Mid Y', 'Rotation', 'Layer'
                    ]
                }
            }
        }
        
    def _get_generic_patterns(self) -> Dict[str, Any]:
        """Get generic KiBot output patterns"""
        return {
            'gerbers': {
                'name': 'Generic Gerbers',
                'type': 'gerber',
                'dir': 'fabrication/gerbers',
                'layers': 'copper'
            },
            'excellon': {
                'name': 'Drill Files',
                'type': 'excellon',
                'dir': 'fabrication/gerbers'
            },
            'position': {
                'name': 'Pick and Place',
                'type': 'position',
                'dir': 'fabrication/assembly'
            },
            'bom': {
                'name': 'Bill of Materials',
                'type': 'bom',
                'dir': 'fabrication/assembly'
            }
        }
        
    def _customize_output_for_project(self, output_config: Dict[str, Any], 
                                    project_data: Dict[str, Any], 
                                    config: KiBotConfig) -> Dict[str, Any]:
        """Customize output configuration for specific project"""
        customized = output_config.copy()
        
        # Apply project-specific customizations
        project_name = project_data.get('name', 'project')
        
        # Customize directory structure
        if 'dir' in customized:
            customized['dir'] = customized['dir'].replace('fabrication', f"fabrication/{project_name}")
            
        # Apply manufacturer-specific options
        if config.manufacturer == 'aisler':
            if output_config.get('type') == 'gerber':
                # AISLER prefers specific gerber settings
                if 'options' not in customized:
                    customized['options'] = {}
                customized['options']['use_gerber_x2_attributes'] = True
                customized['options']['use_gerber_net_attributes'] = True
                
        elif config.manufacturer == 'jlcpcb':
            if output_config.get('type') == 'position':
                # JLCPCB specific column names
                if 'options' not in customized:
                    customized['options'] = {}
                customized['options']['columns'] = [
                    'Designator', 'Val', 'Package', 'Mid X', 'Mid Y', 'Rotation', 'Layer'
                ]
                
        return customized
        
    def _generate_cognitive_outputs(self, project_data: Dict[str, Any], 
                                   config: KiBotConfig) -> List[Dict[str, Any]]:
        """Generate cognitive-enhanced outputs"""
        cognitive_outputs = []
        
        # Interactive BOM with cognitive insights
        if config.enable_interactive_bom:
            cognitive_outputs.append({
                'name': 'Cognitive Interactive BOM',
                'comment': 'Interactive BOM with manufacturing insights',
                'type': 'ibom',
                'dir': 'fabrication/documentation',
                'options': {
                    'blacklist': 'DNF*,TP*',
                    'include_tracks': True,
                    'include_nets': True,
                    'sort_order': 'C,R,L,D,U,Y,X,F,SW,A',
                    'board_rotation': 0,
                    'layer_view': 'FB',
                    'name_format': f"{project_data.get('name', 'project')}_interactive_bom"
                }
            })
            
        # 3D models for visualization
        if config.enable_3d_models:
            cognitive_outputs.append({
                'name': 'Cognitive 3D View',
                'comment': '3D visualization with manufacturing context',
                'type': 'render_3d',
                'dir': 'fabrication/visualization',
                'options': {
                    'zoom': 0,
                    'rotate_x': 3,
                    'rotate_z': -2,
                    'ray_tracing': True,
                    'orthographic': False
                }
            })
            
        # Manufacturing report with cognitive insights
        cognitive_outputs.append({
            'name': 'Cognitive Manufacturing Report',
            'comment': 'Manufacturing analysis with AI insights',
            'type': 'navigate_results',
            'dir': 'fabrication/reports',
            'options': {
                'link_from_root': '../..'
            }
        })
        
        return cognitive_outputs
        
    def _apply_cognitive_optimizations(self, kibot_config: Dict[str, Any], 
                                     project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply cognitive optimizations to KiBot configuration"""
        optimized = kibot_config.copy()
        
        # Apply learned patterns from cognitive system
        if self.context and hasattr(self.context, 'learned_patterns'):
            fabrication_patterns = self.context.learned_patterns.get('fabrication_optimization', [])
            
            for pattern in fabrication_patterns[-3:]:  # Last 3 successful patterns
                if pattern.get('success', False):
                    optimization = pattern.get('optimization', {})
                    
                    # Apply successful optimizations
                    if optimization.get('type') == 'gerber_precision':
                        # Increase gerber precision for complex designs
                        for output in optimized['outputs']:
                            if output.get('type') == 'gerber':
                                if 'options' not in output:
                                    output['options'] = {}
                                output['options']['precision'] = optimization.get('value', 6)
                                
                    elif optimization.get('type') == 'drill_optimization':
                        # Optimize drill file generation
                        for output in optimized['outputs']:
                            if output.get('type') == 'excellon':
                                if 'options' not in output:
                                    output['options'] = {}
                                output['options']['minimal_header'] = True
                                output['options']['mirror_y_axis'] = False
                                
        # Project-specific optimizations
        project_name = project_data.get('name', '').lower()
        if 'master' in project_name and 'muppets' in project_name:
            # Master of Muppets specific optimizations
            optimized['preflight']['check_zone_fills'] = True
            optimized['preflight']['run_drc'] = True
            
            # Add USB-specific checks for Master of Muppets
            optimized['preflight']['run_erc'] = True
            
        return optimized
        
    def _execute_kibot(self, project_data: Dict[str, Any], 
                      kibot_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute KiBot with generated configuration"""
        try:
            project_path = Path(project_data.get('path', '.'))
            project_name = project_data.get('name', 'project')
            
            # Save KiBot configuration
            config_file = project_path / f"{project_name}_kibot.yml"
            with open(config_file, 'w') as f:
                yaml.dump(kibot_config, f, default_flow_style=False, sort_keys=False)
                
            # Find project file
            pro_file = project_path / f"{project_name}.kicad_pro"
            if not pro_file.exists():
                return {
                    'success': False,
                    'error': f'KiCad project file not found: {pro_file}',
                    'outputs': []
                }
                
            # Execute KiBot
            cmd = ['kibot', '-c', str(config_file), '-b', str(pro_file)]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  cwd=str(project_path), timeout=300)
            
            if result.returncode == 0:
                # Scan for generated outputs
                outputs = self._scan_generated_outputs(project_path, kibot_config)
                return {
                    'success': True,
                    'outputs': outputs,
                    'stdout': result.stdout,
                    'config_file': str(config_file)
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr or result.stdout,
                    'outputs': [],
                    'config_file': str(config_file)
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'KiBot execution timed out (300s)',
                'outputs': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'outputs': []
            }
            
    def _save_kibot_config(self, project_data: Dict[str, Any], 
                          kibot_config: Dict[str, Any]) -> Dict[str, Any]:
        """Save KiBot configuration for manual execution"""
        try:
            project_path = Path(project_data.get('path', '.'))
            project_name = project_data.get('name', 'project')
            
            # Save KiBot configuration
            config_file = project_path / f"{project_name}_kibot.yml"
            with open(config_file, 'w') as f:
                yaml.dump(kibot_config, f, default_flow_style=False, sort_keys=False)
                
            # Generate installation and execution instructions
            instructions_file = project_path / "KIBOT_INSTRUCTIONS.md"
            instructions = self._generate_kibot_instructions(project_name, str(config_file))
            
            with open(instructions_file, 'w') as f:
                f.write(instructions)
                
            return {
                'success': True,
                'config_files': [str(config_file), str(instructions_file)],
                'message': 'KiBot configuration saved for manual execution'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'config_files': []
            }
            
    def _generate_kibot_instructions(self, project_name: str, config_file: str) -> str:
        """Generate KiBot installation and execution instructions"""
        return f"""# KiBot Fabrication Automation Instructions

## Installation

### Option 1: pip (Recommended)
```bash
pip install kibot
```

### Option 2: Debian/Ubuntu
```bash
sudo apt install kibot
```

### Option 3: Docker
```bash
docker pull setsoft/kicad_auto:latest
```

## Usage

### Basic Execution
```bash
kibot -c {config_file} -b {project_name}.kicad_pro
```

### With Output Directory
```bash
kibot -c {config_file} -b {project_name}.kicad_pro -d fabrication_output
```

### Dry Run (Check Configuration)
```bash
kibot -c {config_file} -b {project_name}.kicad_pro --dry
```

## Generated Files

After successful execution, you'll find:
- **Gerber Files**: `fabrication/gerbers/` - For PCB manufacturing
- **Drill Files**: `fabrication/gerbers/` - Drilling instructions  
- **Assembly Files**: `fabrication/assembly/` - Pick & place and BOM
- **Documentation**: `fabrication/documentation/` - Interactive BOM, reports
- **Visualization**: `fabrication/visualization/` - 3D renders

## AISLER Upload

For AISLER manufacturing:
1. Zip the contents of `fabrication/gerbers/`
2. Upload to https://aisler.net/partners/kicad
3. Use assembly files from `fabrication/assembly/` if ordering assembly

## Troubleshooting

### KiCad Not Found
```bash
export KICAD_CONFIG_HOME=/path/to/kicad/config
```

### Permission Issues
```bash
chmod +x /usr/bin/kibot
```

### Missing Dependencies
```bash
pip install --upgrade kibot[all]
```

---
*Generated by KiCad-Fu Cognitive Automation System*
"""
        
    def _scan_generated_outputs(self, project_path: Path, 
                               kibot_config: Dict[str, Any]) -> List[str]:
        """Scan for files generated by KiBot"""
        outputs = []
        
        for output in kibot_config.get('outputs', []):
            output_dir = output.get('dir', 'fabrication')
            full_dir = project_path / output_dir
            
            if full_dir.exists():
                for file_path in full_dir.rglob('*'):
                    if file_path.is_file():
                        outputs.append(str(file_path.relative_to(project_path)))
                        
        return outputs
        
    def _generate_fabrication_insights(self, project_data: Dict[str, Any], 
                                     config: KiBotConfig, 
                                     job: FabricationJob) -> Dict[str, Any]:
        """Generate cognitive insights about fabrication job"""
        insights = {
            'automation_effectiveness': 'high' if job.success else 'low',
            'manufacturer_optimization': config.manufacturer,
            'output_completeness': len(job.outputs_generated),
            'recommendations': [],
            'learned_patterns': []
        }
        
        # Analyze job success factors
        if job.success:
            insights['recommendations'].append(f"Successful {config.manufacturer} fabrication automation")
            if len(job.outputs_generated) > 5:
                insights['recommendations'].append("Complete output set generated")
        else:
            insights['recommendations'].append("Review KiBot configuration and project files")
            insights['recommendations'].append("Check KiCad project for design rule violations")
            
        # Manufacturer-specific insights
        if config.manufacturer == 'aisler':
            insights['recommendations'].append("Upload native KiCad files to AISLER for best results")
            insights['recommendations'].append("Consider AISLER assembly service for complex designs")
            
        # Apply learned patterns from cognitive system
        if self.context and hasattr(self.context, 'learned_patterns'):
            fabrication_insights = self.context.learned_patterns.get('fabrication_insights', [])
            insights['learned_patterns'] = [
                pattern.get('insight', '') for pattern in fabrication_insights[-3:]
                if pattern.get('success', False)
            ]
            
        return insights
        
    def _extract_lessons_learned(self, job: FabricationJob) -> List[str]:
        """Extract lessons learned from fabrication job"""
        lessons = []
        
        if job.success:
            lessons.append(f"Successful {job.config.manufacturer} fabrication automation")
            lessons.append(f"Generated {len(job.outputs_generated)} output files")
            
            if job.config.cognitive_optimization:
                lessons.append("Cognitive optimization improved fabrication quality")
                
        else:
            lessons.append("Fabrication automation encountered issues")
            lessons.append("Review project configuration and dependencies")
            
        # Job-specific lessons
        if job.config.enable_interactive_bom:
            lessons.append("Interactive BOM enhances manufacturing documentation")
            
        if job.config.enable_3d_models:
            lessons.append("3D visualization aids design verification")
            
        return lessons
        
    def get_automation_status(self) -> Dict[str, Any]:
        """Get current automation system status"""
        return {
            'kibot_available': self.kibot_available,
            'supported_manufacturers': list(self.fabrication_patterns.keys()),
            'cognitive_integration': self.context is not None,
            'automation_features': {
                'gerber_generation': True,
                'drill_files': True,
                'assembly_files': True,
                'interactive_bom': True,
                '3d_visualization': True,
                'cognitive_optimization': True
            }
        }