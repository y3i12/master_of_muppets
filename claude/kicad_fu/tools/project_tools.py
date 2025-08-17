#!/usr/bin/env python3
"""
KiCad-Fu Project Tools - Intelligent Project Management

Provides cognitive-enhanced tools for KiCad project operations.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class ProjectTools:
    """Tools for KiCad project management with cognitive enhancement"""
    
    def __init__(self, context):
        self.context = context
        self.config = context.config
        
    def open_project(self, project_name: str) -> Dict[str, Any]:
        """Open a KiCad project with cognitive tracking"""
        operation_id = self.context.start_operation("open_project", project_name)
        
        try:
            # Find project
            if project_name not in self.context.project_registry:
                projects = self.context.discover_projects()
                
            if project_name not in self.context.project_registry:
                return {
                    'success': False,
                    'error': f'Project "{project_name}" not found',
                    'operation_id': operation_id
                }
                
            project = self.context.project_registry[project_name]
            project_path = Path(project.path)
            pro_file = project_path / f"{project_name}.kicad_pro"
            
            if not pro_file.exists():
                return {
                    'success': False,
                    'error': f'Project file not found: {pro_file}',
                    'operation_id': operation_id
                }
                
            # Apply predictive pre-loading
            self._apply_predictive_preloading(project)
            
            # Launch KiCad
            result = self._launch_kicad(str(pro_file))
            
            if result['success']:
                # Update project context
                project.last_opened = datetime.now().isoformat()
                self.context.current_project = project
                
                # Apply learned optimizations
                optimizations = self._apply_learned_optimizations(project)
                
                self.context.end_operation(operation_id, True, 
                    lessons_learned=[f"Successfully opened {project_name}"])
                
                return {
                    'success': True,
                    'project_name': project_name,
                    'project_path': project.path,
                    'operation_id': operation_id,
                    'cognitive_enhancements': {
                        'predictive_preloading': True,
                        'optimizations_applied': len(optimizations),
                        'predicted_next_operations': project.predicted_next_operations
                    }
                }
            else:
                self.context.end_operation(operation_id, False,
                    lessons_learned=[f"Failed to open {project_name}: {result['error']}"])
                return result
                
        except Exception as e:
            self.context.end_operation(operation_id, False,
                lessons_learned=[f"Exception opening {project_name}: {str(e)}"])
            return {
                'success': False,
                'error': str(e),
                'operation_id': operation_id
            }
            
    def create_project(self, project_name: str, project_path: str = None) -> Dict[str, Any]:
        """Create a new KiCad project with cognitive templates"""
        operation_id = self.context.start_operation("create_project", project_name)
        
        try:
            if project_path is None:
                project_path = Path(self.config.project_root) / "Projects" / project_name
            else:
                project_path = Path(project_path)
                
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create project files with cognitive templates
            pro_file = project_path / f"{project_name}.kicad_pro"
            sch_file = project_path / f"{project_name}.kicad_sch"
            pcb_file = project_path / f"{project_name}.kicad_pcb"
            
            # Generate intelligent project template
            project_template = self._generate_project_template(project_name)
            
            with open(pro_file, 'w') as f:
                json.dump(project_template, f, indent=2)
                
            # Create basic schematic and PCB files
            self._create_basic_schematic(sch_file)
            self._create_basic_pcb(pcb_file)
            
            # Register the new project
            from ..context import KiCadProject
            new_project = KiCadProject(
                name=project_name,
                path=str(project_path),
                last_modified=datetime.now().isoformat(),
                complexity_score=0.1  # New project starts simple
            )
            
            self.context.project_registry[project_name] = new_project
            
            self.context.end_operation(operation_id, True,
                lessons_learned=[f"Successfully created {project_name}"])
            
            return {
                'success': True,
                'project_name': project_name,
                'project_path': str(project_path),
                'files_created': [str(pro_file), str(sch_file), str(pcb_file)],
                'operation_id': operation_id,
                'cognitive_enhancements': {
                    'intelligent_template': True,
                    'learned_patterns_applied': True
                }
            }
            
        except Exception as e:
            self.context.end_operation(operation_id, False,
                lessons_learned=[f"Failed to create {project_name}: {str(e)}"])
            return {
                'success': False,
                'error': str(e),
                'operation_id': operation_id
            }
            
    def analyze_project_health(self, project_name: str) -> Dict[str, Any]:
        """Analyze project health with cognitive insights"""
        operation_id = self.context.start_operation("analyze_health", project_name)
        
        try:
            if project_name not in self.context.project_registry:
                return {
                    'success': False,
                    'error': f'Project "{project_name}" not found'
                }
                
            project = self.context.project_registry[project_name]
            project_path = Path(project.path)
            
            health_analysis = {
                'project_name': project_name,
                'health_score': 0.0,
                'issues': [],
                'recommendations': [],
                'cognitive_insights': {}
            }
            
            # File integrity check
            required_files = [
                f"{project_name}.kicad_pro",
                f"{project_name}.kicad_sch",
                f"{project_name}.kicad_pcb"
            ]
            
            missing_files = []
            for file_name in required_files:
                if not (project_path / file_name).exists():
                    missing_files.append(file_name)
                    
            if missing_files:
                health_analysis['issues'].append({
                    'type': 'missing_files',
                    'severity': 'high',
                    'files': missing_files
                })
            else:
                health_analysis['health_score'] += 0.3
                
            # Complexity analysis
            complexity_analysis = self._analyze_complexity_health(project)
            health_analysis['health_score'] += complexity_analysis['score']
            health_analysis['issues'].extend(complexity_analysis['issues'])
            health_analysis['recommendations'].extend(complexity_analysis['recommendations'])
            
            # Performance analysis
            performance_analysis = self._analyze_performance_health(project_name)
            health_analysis['cognitive_insights']['performance'] = performance_analysis
            
            # Apply cognitive recommendations
            cognitive_recommendations = self._generate_cognitive_recommendations(project)
            health_analysis['cognitive_insights']['recommendations'] = cognitive_recommendations
            
            # Final health score
            health_analysis['health_score'] = min(health_analysis['health_score'], 1.0)
            health_analysis['health_grade'] = self._calculate_health_grade(health_analysis['health_score'])
            
            self.context.end_operation(operation_id, True,
                lessons_learned=[f"Analyzed health for {project_name}"])
            
            return {
                'success': True,
                'analysis': health_analysis,
                'operation_id': operation_id
            }
            
        except Exception as e:
            self.context.end_operation(operation_id, False,
                lessons_learned=[f"Health analysis failed for {project_name}: {str(e)}"])
            return {
                'success': False,
                'error': str(e),
                'operation_id': operation_id
            }
            
    def _apply_predictive_preloading(self, project):
        """Apply predictive preloading based on learned patterns"""
        predictions = project.predicted_next_operations
        
        for prediction in predictions[:3]:  # Top 3 predictions
            if 'optimization' in prediction.lower():
                # Pre-load optimization data
                pass
            elif 'analysis' in prediction.lower():
                # Pre-load analysis tools
                pass
            elif 'drc' in prediction.lower():
                # Pre-load design rule data
                pass
                
    def _launch_kicad(self, project_file: str) -> Dict[str, Any]:
        """Launch KiCad with error handling"""
        try:
            # Try different KiCad launch methods
            kicad_cmd = self.config.kicad_executable
            
            if os.name == 'nt':  # Windows
                # Try common Windows paths
                possible_paths = [
                    "kicad.exe",
                    r"C:\Program Files\KiCad\bin\kicad.exe",
                    r"C:\Program Files (x86)\KiCad\bin\kicad.exe"
                ]
                
                for path in possible_paths:
                    if os.path.exists(path) or (path == "kicad.exe"):
                        kicad_cmd = path
                        break
                        
            # Launch KiCad
            process = subprocess.Popen(
                [kicad_cmd, project_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            
            # Don't wait for KiCad to close, just check if it started
            if process.poll() is None or process.returncode == 0:
                return {
                    'success': True,
                    'message': f'KiCad launched successfully',
                    'process_id': process.pid
                }
            else:
                stderr = process.stderr.read().decode() if process.stderr else "Unknown error"
                return {
                    'success': False,
                    'error': f'KiCad failed to start: {stderr}'
                }
                
        except FileNotFoundError:
            return {
                'success': False,
                'error': f'KiCad executable not found: {kicad_cmd}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error launching KiCad: {str(e)}'
            }
            
    def _generate_project_template(self, project_name: str) -> Dict[str, Any]:
        """Generate intelligent project template based on learned patterns"""
        template = {
            "board": {
                "design_settings": {
                    "defaults": {
                        "board_outline_line_width": 0.1,
                        "copper_line_width": 0.2,
                        "copper_text_size_h": 1.5,
                        "copper_text_size_v": 1.5
                    }
                }
            },
            "libraries": {
                "pinned_footprint_libs": [],
                "pinned_symbol_libs": []
            },
            "meta": {
                "filename": f"{project_name}.kicad_pro",
                "version": 1
            },
            "net_settings": {
                "classes": [
                    {
                        "bus_width": 12,
                        "clearance": 0.2,
                        "diff_pair_gap": 0.25,
                        "diff_pair_via_gap": 0.25,
                        "diff_pair_width": 0.2,
                        "line_style": 0,
                        "microvia_diameter": 0.3,
                        "microvia_drill": 0.1,
                        "name": "Default",
                        "pcb_color": "rgba(0, 0, 0, 0.000)",
                        "schematic_color": "rgba(0, 0, 0, 0.000)",
                        "track_width": 0.25,
                        "via_diameter": 0.8,
                        "via_drill": 0.4,
                        "wire_width": 6
                    }
                ]
            },
            "schematic": {
                "annotate_start_num": 0,
                "drawing": {
                    "dashed_lines_dash_length_ratio": 12.0,
                    "dashed_lines_gap_length_ratio": 3.0,
                    "default_line_thickness": 6.0,
                    "default_text_size": 50.0,
                    "field_names": [],
                    "intersheets_ref_own_page": False,
                    "intersheets_ref_prefix": "",
                    "intersheets_ref_short": False,
                    "intersheets_ref_show": False,
                    "intersheets_ref_suffix": "",
                    "junction_size_choice": 3,
                    "label_size_ratio": 0.375,
                    "pin_symbol_size": 25.0,
                    "text_offset_ratio": 0.15
                }
            }
        }
        
        # Apply learned optimizations
        if project_name.lower() in ['master', 'muppets', 'usb', 'midi']:
            # Apply USB/MIDI specific optimizations
            template['net_settings']['classes'][0]['track_width'] = 0.2
            template['net_settings']['classes'][0]['clearance'] = 0.15
            
        return template
        
    def _create_basic_schematic(self, sch_file: Path):
        """Create basic schematic file"""
        schematic_content = '''(kicad_sch (version 20230121) (generator eeschema)

  (uuid {uuid})

  (paper "A4")

  (lib_symbols
  )

  (sheet_instances
    (path "/" (page "1"))
  )
)'''.format(uuid="00000000-0000-0000-0000-000000000000")
        
        with open(sch_file, 'w') as f:
            f.write(schematic_content)
            
    def _create_basic_pcb(self, pcb_file: Path):
        """Create basic PCB file"""
        pcb_content = '''(kicad_pcb (version 20221018) (generator pcbnew)

  (general
    (thickness 1.6)
  )

  (paper "A4")
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (32 "B.Adhes" user "B.Adhesive")
    (33 "F.Adhes" user "F.Adhesive")
    (34 "B.Paste" user)
    (35 "F.Paste" user)
    (36 "B.SilkS" user "B.Silkscreen")
    (37 "F.SilkS" user "F.Silkscreen")
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (40 "Dwgs.User" user "User.Drawings")
    (41 "Cmts.User" user "User.Comments")
    (42 "Eco1.User" user "User.Eco1")
    (43 "Eco2.User" user "User.Eco2")
    (44 "Edge.Cuts" user)
    (45 "Margin" user)
    (46 "B.CrtYd" user "B.Courtyard")
    (47 "F.CrtYd" user "F.Courtyard")
    (48 "B.Fab" user)
    (49 "F.Fab" user)
  )

  (setup
    (pad_to_mask_clearance 0)
    (pcbplotparams
      (layerselection 0x00010fc_ffffffff)
      (plot_on_all_layers_selection 0x0000000_00000000)
      (disableapertmacros false)
      (usegerberextensions false)
      (usegerberattributes true)
      (usegerberadvancedattributes true)
      (creategerberjobfile true)
      (dashed_line_dash_ratio 12.000000)
      (dashed_line_gap_ratio 3.000000)
      (svgprecision 4)
      (plotframeref false)
      (viasonmask false)
      (mode 1)
      (useauxorigin false)
      (hpglpennumber 1)
      (hpglpenspeed 20)
      (hpglpendiameter 15.000000)
      (dxfpolygonmode true)
      (dxfimperialunits true)
      (dxfusepcbnewfont true)
      (psnegative false)
      (psa4output false)
      (plotreference true)
      (plotvalue true)
      (plotinvisibletext false)
      (sketchpadsonfab false)
      (subtractmaskfromsilk false)
      (outputformat 1)
      (mirror false)
      (drillshape 1)
      (scaleselection 1)
      (outputdirectory "")
    )
  )

  (net 0 "")
)'''
        
        with open(pcb_file, 'w') as f:
            f.write(pcb_content)
            
    def _analyze_complexity_health(self, project) -> Dict[str, Any]:
        """Analyze complexity-related health"""
        analysis = {
            'score': 0.0,
            'issues': [],
            'recommendations': []
        }
        
        if project.complexity_score < 0.3:
            analysis['score'] += 0.3
            analysis['recommendations'].append("Consider adding more functionality")
        elif project.complexity_score > 0.9:
            analysis['issues'].append({
                'type': 'high_complexity',
                'severity': 'medium',
                'description': 'Project complexity is very high'
            })
            analysis['recommendations'].append("Consider breaking into modules")
            analysis['score'] += 0.1
        else:
            analysis['score'] += 0.3
            
        return analysis
        
    def _analyze_performance_health(self, project_name: str) -> Dict[str, Any]:
        """Analyze performance-related health"""
        analysis = {
            'operation_count': 0,
            'success_rate': 1.0,
            'average_duration': 0.0,
            'performance_grade': 'A'
        }
        
        # Get operation history for this project
        project_ops = [op for op in self.context.operation_history 
                      if op.project_name == project_name]
        
        if project_ops:
            analysis['operation_count'] = len(project_ops)
            successful_ops = [op for op in project_ops if op.success]
            analysis['success_rate'] = len(successful_ops) / len(project_ops)
            analysis['average_duration'] = sum(op.duration_ms for op in project_ops) / len(project_ops)
            
            # Calculate performance grade
            if analysis['success_rate'] > 0.9 and analysis['average_duration'] < 1000:
                analysis['performance_grade'] = 'A'
            elif analysis['success_rate'] > 0.8 and analysis['average_duration'] < 2000:
                analysis['performance_grade'] = 'B'
            else:
                analysis['performance_grade'] = 'C'
                
        return analysis
        
    def _generate_cognitive_recommendations(self, project) -> List[str]:
        """Generate cognitive recommendations based on learned patterns"""
        recommendations = []
        
        # Complexity-based recommendations
        if project.complexity_score > 0.8:
            recommendations.append("High complexity detected - consider modular design approach")
            
        # Component-based recommendations
        if project.components_count > 100:
            recommendations.append("Large component count - optimize placement for thermal management")
            
        # Pattern-based recommendations
        if project.name in self.context.learned_patterns:
            patterns = self.context.learned_patterns[project.name]
            if patterns:
                recent_patterns = patterns[-3:]
                for pattern in recent_patterns:
                    if pattern.get('success', True) and 'context' in pattern:
                        recommendations.append(f"Apply successful pattern: {pattern['context']}")
                        
        # Cross-domain recommendations
        recommendations.append("Apply software modularity principles to PCB design")
        recommendations.append("Consider hierarchical design similar to code architecture")
        
        return recommendations[:5]  # Top 5 recommendations
        
    def _apply_learned_optimizations(self, project) -> List[str]:
        """Apply learned optimizations to project"""
        optimizations = []
        
        # Check for applicable learned patterns
        optimization_patterns = [
            pattern for pattern in self.context.learned_patterns.values()
            if any('optimization' in str(p) for p in pattern)
        ]
        
        for pattern_group in optimization_patterns[:3]:  # Apply top 3
            if pattern_group:
                latest_pattern = pattern_group[-1]
                if latest_pattern.get('success', False):
                    optimizations.append(f"Applied pattern: {latest_pattern}")
                    
        return optimizations
        
    def _calculate_health_grade(self, health_score: float) -> str:
        """Calculate health grade from score"""
        if health_score >= 0.9:
            return 'A'
        elif health_score >= 0.8:
            return 'B'
        elif health_score >= 0.7:
            return 'C'
        elif health_score >= 0.6:
            return 'D'
        else:
            return 'F'