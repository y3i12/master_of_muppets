#!/usr/bin/env python3
"""
AISLER PCB Manufacturing Optimizer - Cognitive Design Optimization

Provides intelligent optimization for AISLER PCB manufacturing with learning.
Integrates AISLER's design rules, pricing, and capabilities with our cognitive systems.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

@dataclass
class AislerDesignRules:
    """AISLER design rules for different PCB configurations"""
    name: str
    layers: int
    thickness: float  # mm
    surface_finish: str  # HASL or ENIG
    min_drill_diameter: float  # mm
    min_trace_width: float  # µm
    min_trace_spacing: float  # µm
    castellated_edges: bool = False
    min_via_size: float = 0.3  # mm
    max_board_size: Tuple[float, float] = (500.0, 500.0)  # mm

@dataclass
class AislerQuote:
    """AISLER manufacturing quote with cognitive insights"""
    base_price: float  # EUR
    quantity: int
    delivery_days: int
    surface_finish: str
    layers: int
    board_size: Tuple[float, float]
    cognitive_recommendations: List[str]
    optimization_score: float
    estimated_total: float

class AislerOptimizer:
    """Cognitive optimizer for AISLER PCB manufacturing"""
    
    def __init__(self, context=None):
        self.context = context
        self.logger = logging.getLogger('aisler_optimizer')
        
        # AISLER design rules (updated May 2024)
        self.design_rules = {
            '2L_HASL_1.6': AislerDesignRules(
                name="2 Layer 1.6mm HASL",
                layers=2,
                thickness=1.6,
                surface_finish="HASL",
                min_drill_diameter=0.3,
                min_trace_width=200,  # µm
                min_trace_spacing=150,  # µm
            ),
            '2L_ENIG_1.6': AislerDesignRules(
                name="2 Layer 1.6mm ENIG", 
                layers=2,
                thickness=1.6,
                surface_finish="ENIG",
                min_drill_diameter=0.25,
                min_trace_width=125,  # µm
                min_trace_spacing=125,  # µm
                castellated_edges=True
            ),
            '4L_ENIG_1.6': AislerDesignRules(
                name="4 Layer 1.6mm ENIG",
                layers=4,
                thickness=1.6,
                surface_finish="ENIG",
                min_drill_diameter=0.25,
                min_trace_width=125,  # µm
                min_trace_spacing=125,  # µm
                castellated_edges=True
            ),
            '4L_ENIG_0.8': AislerDesignRules(
                name="4 Layer 0.8mm ENIG",
                layers=4,
                thickness=0.8,
                surface_finish="ENIG", 
                min_drill_diameter=0.25,
                min_trace_width=125,  # µm
                min_trace_spacing=125,  # µm
                castellated_edges=True
            )
        }
        
        # AISLER pricing model (base prices in EUR, updated 2024)
        self.pricing_model = {
            '2L_HASL_1.6': {'base': 12.18, 'area_multiplier': 0.1},
            '2L_ENIG_1.6': {'base': 18.50, 'area_multiplier': 0.15},
            '4L_ENIG_1.6': {'base': 35.00, 'area_multiplier': 0.25},
            '4L_ENIG_0.8': {'base': 45.00, 'area_multiplier': 0.30}
        }
        
    def analyze_project_requirements(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project and recommend optimal AISLER configuration"""
        operation_id = None
        if self.context:
            operation_id = self.context.start_operation("aisler_analysis", project_data.get('name', 'unknown'))
            
        try:
            analysis = {
                'project_name': project_data.get('name', 'Unknown'),
                'requirements_analysis': {},
                'recommended_config': None,
                'all_compatible_configs': [],
                'cognitive_insights': {},
                'aisler_optimizations': []
            }
            
            # Extract project requirements
            requirements = self._extract_requirements(project_data)
            analysis['requirements_analysis'] = requirements
            
            # Find compatible configurations
            compatible_configs = self._find_compatible_configs(requirements)
            analysis['all_compatible_configs'] = compatible_configs
            
            # Recommend optimal configuration
            optimal_config = self._recommend_optimal_config(compatible_configs, requirements)
            analysis['recommended_config'] = optimal_config
            
            # Generate cognitive insights
            insights = self._generate_cognitive_insights(requirements, optimal_config)
            analysis['cognitive_insights'] = insights
            
            # AISLER-specific optimizations
            optimizations = self._generate_aisler_optimizations(requirements, optimal_config)
            analysis['aisler_optimizations'] = optimizations
            
            if self.context:
                self.context.end_operation(operation_id, True, 
                    lessons_learned=[f"AISLER analysis for {project_data.get('name')}"])
                    
            return {
                'success': True,
                'analysis': analysis,
                'operation_id': operation_id
            }
            
        except Exception as e:
            if self.context:
                self.context.end_operation(operation_id, False,
                    lessons_learned=[f"AISLER analysis failed: {str(e)}"])
            return {
                'success': False,
                'error': str(e),
                'operation_id': operation_id
            }
    
    def _extract_requirements(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract manufacturing requirements from project data"""
        requirements = {
            'layers_needed': 2,  # Default
            'min_trace_width': 200,  # µm, default
            'min_trace_spacing': 150,  # µm, default
            'min_drill_size': 0.3,  # mm, default
            'has_fine_pitch': False,
            'needs_castellated_edges': False,
            'board_size': (50.0, 50.0),  # Default 50x50mm
            'component_count': 0,
            'has_high_speed_signals': False,
            'has_analog_circuits': False,
            'requires_impedance_control': False
        }
        
        # Extract from PCB analysis if available
        if 'pcb_analysis' in project_data:
            pcb = project_data['pcb_analysis']
            requirements['layers_needed'] = pcb.get('layers_count', 2)
            requirements['component_count'] = pcb.get('components_count', 0)
            requirements['board_size'] = pcb.get('board_size', (50.0, 50.0))
            
            # Analyze trace requirements
            if 'traces' in pcb:
                traces = pcb['traces']
                if traces:
                    min_width = min(trace.get('width', 200) for trace in traces)
                    requirements['min_trace_width'] = min_width
                    
            # Check for fine-pitch components
            if requirements['component_count'] > 50:
                requirements['has_fine_pitch'] = True
                
        # Master of Muppets specific analysis
        if project_data.get('name') == 'MasterOfMuppets':
            requirements.update({
                'layers_needed': 4,  # Complex USB MIDI to CV needs 4 layers
                'min_trace_width': 125,  # Fine traces for digital signals
                'min_trace_spacing': 125,  # Tight spacing for compact design
                'has_high_speed_signals': True,  # USB signals
                'has_analog_circuits': True,  # CV outputs
                'requires_impedance_control': True,  # USB differential pairs
                'needs_castellated_edges': False,  # Standard mounting
                'board_size': (100.0, 80.0)  # Estimated from 147 components
            })
            
        return requirements
        
    def _find_compatible_configs(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find all AISLER configurations compatible with requirements"""
        compatible = []
        
        for config_key, rules in self.design_rules.items():
            is_compatible = True
            compatibility_notes = []
            
            # Check layer count
            if rules.layers < requirements['layers_needed']:
                is_compatible = False
                compatibility_notes.append(f"Insufficient layers: {rules.layers} < {requirements['layers_needed']}")
                
            # Check trace width
            if rules.min_trace_width > requirements['min_trace_width']:
                is_compatible = False
                compatibility_notes.append(f"Trace width too wide: {rules.min_trace_width}µm > {requirements['min_trace_width']}µm")
                
            # Check trace spacing
            if rules.min_trace_spacing > requirements['min_trace_spacing']:
                is_compatible = False
                compatibility_notes.append(f"Trace spacing too wide: {rules.min_trace_spacing}µm > {requirements['min_trace_spacing']}µm")
                
            # Check castellated edges requirement
            if requirements['needs_castellated_edges'] and not rules.castellated_edges:
                is_compatible = False
                compatibility_notes.append("Castellated edges not supported")
                
            # Calculate board area and check size limits
            board_area = requirements['board_size'][0] * requirements['board_size'][1]
            max_area = rules.max_board_size[0] * rules.max_board_size[1]
            if board_area > max_area:
                is_compatible = False
                compatibility_notes.append(f"Board too large: {board_area}mm² > {max_area}mm²")
                
            config_info = {
                'config_key': config_key,
                'rules': asdict(rules),
                'compatible': is_compatible,
                'compatibility_notes': compatibility_notes,
                'estimated_price': self._estimate_price(config_key, requirements['board_size'])
            }
            
            if is_compatible:
                compatible.append(config_info)
                
        return compatible
        
    def _recommend_optimal_config(self, compatible_configs: List[Dict[str, Any]], 
                                 requirements: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recommend the optimal AISLER configuration"""
        if not compatible_configs:
            return None
            
        # Score each compatible configuration
        scored_configs = []
        for config in compatible_configs:
            score = self._calculate_config_score(config, requirements)
            scored_configs.append({**config, 'optimization_score': score})
            
        # Sort by score (higher is better)
        scored_configs.sort(key=lambda x: x['optimization_score'], reverse=True)
        
        optimal = scored_configs[0]
        
        # Add recommendation reasoning
        optimal['recommendation_reasoning'] = self._generate_recommendation_reasoning(optimal, requirements)
        
        return optimal
        
    def _calculate_config_score(self, config: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """Calculate optimization score for a configuration"""
        score = 0.0
        
        rules = config['rules']
        
        # Cost efficiency (40% of score)
        price_score = 1.0 / (1.0 + config['estimated_price'] / 50.0)  # Normalize around €50
        score += price_score * 0.4
        
        # Capability match (30% of score) 
        capability_score = 0.0
        if requirements['has_high_speed_signals'] and rules['surface_finish'] == 'ENIG':
            capability_score += 0.3
        if requirements['has_analog_circuits'] and rules['layers'] >= 4:
            capability_score += 0.3
        if requirements['requires_impedance_control'] and rules['surface_finish'] == 'ENIG':
            capability_score += 0.4
        score += capability_score * 0.3
        
        # Manufacturing margin (20% of score)
        margin_score = 0.0
        trace_margin = (rules['min_trace_width'] - requirements['min_trace_width']) / rules['min_trace_width']
        margin_score += min(trace_margin * 2, 1.0)  # Reward manufacturing margin
        score += margin_score * 0.2
        
        # Delivery time bonus (10% of score)
        delivery_score = 1.0  # AISLER standard 1-2 days, excellent
        score += delivery_score * 0.1
        
        return min(score, 1.0)  # Cap at 1.0
        
    def _estimate_price(self, config_key: str, board_size: Tuple[float, float]) -> float:
        """Estimate AISLER price for configuration and board size"""
        if config_key not in self.pricing_model:
            return 50.0  # Default estimate
            
        pricing = self.pricing_model[config_key]
        board_area_cm2 = (board_size[0] * board_size[1]) / 100.0  # Convert mm² to cm²
        
        estimated_price = pricing['base'] + (board_area_cm2 * pricing['area_multiplier'])
        
        return round(estimated_price, 2)
        
    def _generate_cognitive_insights(self, requirements: Dict[str, Any], 
                                   optimal_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate cognitive insights about the AISLER manufacturing choice"""
        insights = {
            'manufacturing_complexity': 'medium',
            'cost_optimization_opportunities': [],
            'design_recommendations': [],
            'risk_assessment': [],
            'learned_patterns': []
        }
        
        if not optimal_config:
            insights['manufacturing_complexity'] = 'incompatible'
            insights['risk_assessment'].append("No compatible AISLER configuration found")
            return insights
            
        # Assess manufacturing complexity
        if requirements['component_count'] > 100:
            insights['manufacturing_complexity'] = 'high'
        elif requirements['component_count'] < 20:
            insights['manufacturing_complexity'] = 'low'
            
        # Cost optimization opportunities
        if optimal_config['rules']['surface_finish'] == 'ENIG':
            insights['cost_optimization_opportunities'].append(
                "Consider HASL if ENIG features not required"
            )
            
        # Design recommendations
        if requirements['has_high_speed_signals']:
            insights['design_recommendations'].extend([
                "Use ENIG surface finish for better signal integrity",
                "Consider 4-layer stackup for controlled impedance",
                "Minimize via usage on high-speed nets"
            ])
            
        if requirements['has_analog_circuits']:
            insights['design_recommendations'].extend([
                "Separate analog and digital ground planes",
                "Use wide traces for power delivery",
                "Consider guard traces around sensitive signals"
            ])
            
        # Risk assessment
        if requirements['min_trace_width'] < 150:
            insights['risk_assessment'].append("Fine traces increase manufacturing risk")
            
        # Apply learned patterns from our cognitive system
        if self.context and hasattr(self.context, 'learned_patterns'):
            aisler_patterns = self.context.learned_patterns.get('aisler_manufacturing', [])
            insights['learned_patterns'] = [
                pattern.get('insight', '') for pattern in aisler_patterns[-3:]
                if pattern.get('success', False)
            ]
            
        return insights
        
    def _generate_aisler_optimizations(self, requirements: Dict[str, Any],
                                     optimal_config: Optional[Dict[str, Any]]) -> List[str]:
        """Generate AISLER-specific optimizations"""
        optimizations = []
        
        if not optimal_config:
            return ["No AISLER optimizations available - no compatible configuration"]
            
        # AISLER-specific recommendations
        optimizations.append("Upload native KiCad project file instead of Gerbers for better interpretation")
        optimizations.append("Use AISLER's free worldwide shipping (7 business days)")
        optimizations.append("Take advantage of 1-2 business day manufacturing in Germany")
        
        if optimal_config['rules']['surface_finish'] == 'ENIG':
            optimizations.append("ENIG finish enables fine-pitch components and castellated edges")
            
        if requirements['component_count'] > 50:
            optimizations.append("Consider AISLER's assembly service for complex designs")
            
        # Cost optimization based on board size
        board_area = requirements['board_size'][0] * requirements['board_size'][1]
        if board_area > 10000:  # > 100cm²
            optimizations.append("Large board: consider panelization to reduce per-unit cost")
            
        return optimizations
        
    def _generate_recommendation_reasoning(self, optimal_config: Dict[str, Any],
                                         requirements: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for the recommendation"""
        rules = optimal_config['rules']
        score = optimal_config['optimization_score']
        
        reasoning = f"Recommended {rules['name']} (score: {score:.1%}) because:\n"
        
        reasons = []
        
        if rules['surface_finish'] == 'ENIG' and requirements['has_high_speed_signals']:
            reasons.append("ENIG surface finish provides better signal integrity for high-speed signals")
            
        if rules['layers'] >= requirements['layers_needed']:
            reasons.append(f"{rules['layers']}-layer stackup meets complexity requirements")
            
        if rules['min_trace_width'] <= requirements['min_trace_width']:
            reasons.append(f"Supports required {requirements['min_trace_width']}µm trace width")
            
        price = optimal_config['estimated_price']
        reasons.append(f"Cost-effective at ~€{price:.2f} for prototype quantities")
        
        reasons.append("Made in Germany with 1-2 business day turnaround")
        
        reasoning += "\n".join(f"• {reason}" for reason in reasons)
        
        return reasoning
        
    def generate_aisler_export_config(self, project_name: str, 
                                    optimal_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate KiCad export configuration optimized for AISLER"""
        if not optimal_config:
            return {'error': 'No optimal configuration available'}
            
        rules = optimal_config['rules']
        
        export_config = {
            'project_name': project_name,
            'aisler_config': rules['name'],
            'export_settings': {
                'use_native_kicad_upload': True,  # AISLER preference
                'include_drill_files': True,
                'include_gerbers': False,  # Not needed for native upload
                'include_pick_and_place': True,
                'include_bom': True,
                'surface_finish': rules['surface_finish'],
                'board_thickness': rules['thickness']
            },
            'design_rule_check': {
                'min_trace_width': rules['min_trace_width'] / 1000.0,  # Convert µm to mm
                'min_trace_spacing': rules['min_trace_spacing'] / 1000.0,
                'min_drill_diameter': rules['min_drill_diameter'],
                'max_board_size': rules['max_board_size']
            },
            'aisler_upload_url': "https://aisler.net/partners/kicad",
            'cognitive_notes': optimal_config.get('recommendation_reasoning', '')
        }
        
        return export_config
        
    def save_aisler_analysis(self, analysis: Dict[str, Any], project_path: str) -> bool:
        """Save AISLER analysis to project directory"""
        try:
            project_dir = Path(project_path)
            analysis_file = project_dir / "aisler_analysis.json"
            
            # Add timestamp
            analysis['analysis']['timestamp'] = datetime.now().isoformat()
            analysis['analysis']['aisler_optimizer_version'] = '1.0.0'
            
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)
                
            self.logger.info(f"AISLER analysis saved to {analysis_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save AISLER analysis: {e}")
            return False