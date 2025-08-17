#!/usr/bin/env python3
"""
Fabrication Validator - Intelligent Design for Manufacturing (DFM) Analysis

Validates PCB designs against multiple manufacturer requirements with cognitive learning.
Supports AISLER, JLCPCB, and other fab houses with adaptive rule checking.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

@dataclass
class DFMRule:
    """Design for Manufacturing rule definition"""
    name: str
    category: str  # trace, via, spacing, etc.
    severity: str  # error, warning, info
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""
    manufacturer_specific: bool = False

@dataclass
class DFMViolation:
    """DFM rule violation with context"""
    rule_name: str
    severity: str
    location: str
    actual_value: float
    required_value: float
    description: str
    cognitive_suggestion: str = ""

class FabricationValidator:
    """Cognitive DFM validator for multiple manufacturers"""
    
    def __init__(self, context=None):
        self.context = context
        self.logger = logging.getLogger('fabrication_validator')
        
        # DFM rules for different manufacturers
        self.manufacturer_rules = {
            'aisler': self._get_aisler_rules(),
            'jlcpcb': self._get_jlcpcb_rules(),
            'generic': self._get_generic_rules()
        }
        
    def validate_design(self, project_data: Dict[str, Any], 
                       manufacturer: str = 'aisler',
                       config: str = 'auto') -> Dict[str, Any]:
        """Validate design against manufacturer DFM rules"""
        operation_id = None
        if self.context:
            operation_id = self.context.start_operation("dfm_validation", 
                                                       f"{project_data.get('name', 'unknown')}_{manufacturer}")
        
        try:
            validation_result = {
                'project_name': project_data.get('name', 'Unknown'),
                'manufacturer': manufacturer,
                'configuration': config,
                'validation_timestamp': datetime.now().isoformat(),
                'overall_status': 'unknown',
                'violations': [],
                'warnings': [],
                'recommendations': [],
                'cognitive_insights': {},
                'dfm_score': 0.0
            }
            
            # Get manufacturer rules
            rules = self._get_rules_for_manufacturer(manufacturer, config)
            if not rules:
                raise ValueError(f"No rules found for manufacturer: {manufacturer}")
                
            # Validate against rules
            violations = self._check_design_rules(project_data, rules)
            validation_result['violations'] = violations
            
            # Categorize violations
            errors = [v for v in violations if v.severity == 'error']
            warnings = [v for v in violations if v.severity == 'warning']
            validation_result['warnings'] = warnings
            
            # Determine overall status
            if errors:
                validation_result['overall_status'] = 'failed'
            elif warnings:
                validation_result['overall_status'] = 'warning'
            else:
                validation_result['overall_status'] = 'passed'
                
            # Calculate DFM score
            dfm_score = self._calculate_dfm_score(violations, len(rules))
            validation_result['dfm_score'] = dfm_score
            
            # Generate recommendations
            recommendations = self._generate_dfm_recommendations(violations, manufacturer)
            validation_result['recommendations'] = recommendations
            
            # Cognitive insights
            insights = self._generate_cognitive_insights(violations, project_data, manufacturer)
            validation_result['cognitive_insights'] = insights
            
            if self.context:
                lesson = f"DFM validation for {manufacturer}: {validation_result['overall_status']}"
                self.context.end_operation(operation_id, True, lessons_learned=[lesson])
                
            return {
                'success': True,
                'validation': validation_result,
                'operation_id': operation_id
            }
            
        except Exception as e:
            if self.context:
                self.context.end_operation(operation_id, False,
                    lessons_learned=[f"DFM validation failed: {str(e)}"])
            return {
                'success': False,
                'error': str(e),
                'operation_id': operation_id
            }
    
    def _get_aisler_rules(self) -> List[DFMRule]:
        """Get AISLER-specific DFM rules (updated May 2024)"""
        return [
            # HASL Surface Finish Rules
            DFMRule(
                name="aisler_hasl_min_drill",
                category="drill",
                severity="error",
                min_value=0.3,  # mm
                description="AISLER HASL minimum drill diameter",
                manufacturer_specific=True
            ),
            DFMRule(
                name="aisler_hasl_min_trace_width",
                category="trace",
                severity="error", 
                min_value=0.2,  # mm (200µm)
                description="AISLER HASL minimum trace width",
                manufacturer_specific=True
            ),
            DFMRule(
                name="aisler_hasl_min_trace_spacing",
                category="spacing",
                severity="error",
                min_value=0.15,  # mm (150µm)
                description="AISLER HASL minimum trace spacing",
                manufacturer_specific=True
            ),
            
            # ENIG Surface Finish Rules
            DFMRule(
                name="aisler_enig_min_drill",
                category="drill",
                severity="error",
                min_value=0.25,  # mm
                description="AISLER ENIG minimum drill diameter",
                manufacturer_specific=True
            ),
            DFMRule(
                name="aisler_enig_min_trace_width",
                category="trace",
                severity="error",
                min_value=0.125,  # mm (125µm)
                description="AISLER ENIG minimum trace width",
                manufacturer_specific=True
            ),
            DFMRule(
                name="aisler_enig_min_trace_spacing", 
                category="spacing",
                severity="error",
                min_value=0.125,  # mm (125µm)
                description="AISLER ENIG minimum trace spacing",
                manufacturer_specific=True
            ),
            
            # Board size rules
            DFMRule(
                name="aisler_min_board_size",
                category="board",
                severity="error",
                min_value=10.0,  # mm
                description="AISLER minimum board dimension",
                manufacturer_specific=True
            ),
            DFMRule(
                name="aisler_max_board_size",
                category="board",
                severity="error",
                max_value=500.0,  # mm
                description="AISLER maximum board dimension",
                manufacturer_specific=True
            ),
            
            # Assembly rules
            DFMRule(
                name="aisler_assembly_min_pitch",
                category="assembly",
                severity="warning",
                min_value=0.5,  # mm
                description="AISLER recommended minimum component pitch for assembly",
                manufacturer_specific=True
            )
        ]
        
    def _get_jlcpcb_rules(self) -> List[DFMRule]:
        """Get JLCPCB-specific DFM rules for comparison"""
        return [
            DFMRule(
                name="jlcpcb_min_drill",
                category="drill", 
                severity="error",
                min_value=0.2,  # mm
                description="JLCPCB minimum drill diameter",
                manufacturer_specific=True
            ),
            DFMRule(
                name="jlcpcb_min_trace_width",
                category="trace",
                severity="error",
                min_value=0.09,  # mm (90µm)
                description="JLCPCB minimum trace width",
                manufacturer_specific=True
            ),
            DFMRule(
                name="jlcpcb_min_trace_spacing",
                category="spacing",
                severity="error",
                min_value=0.09,  # mm (90µm)
                description="JLCPCB minimum trace spacing", 
                manufacturer_specific=True
            )
        ]
        
    def _get_generic_rules(self) -> List[DFMRule]:
        """Get generic PCB manufacturing rules"""
        return [
            DFMRule(
                name="generic_min_annular_ring",
                category="via",
                severity="warning",
                min_value=0.05,  # mm
                description="Minimum annular ring for reliability"
            ),
            DFMRule(
                name="generic_solder_mask_bridge",
                category="solder_mask",
                severity="warning",
                min_value=0.1,  # mm
                description="Minimum solder mask bridge"
            ),
            DFMRule(
                name="generic_copper_to_edge",
                category="spacing",
                severity="error",
                min_value=0.2,  # mm
                description="Minimum copper to board edge clearance"
            )
        ]
        
    def _get_rules_for_manufacturer(self, manufacturer: str, config: str) -> List[DFMRule]:
        """Get DFM rules for specific manufacturer and configuration"""
        base_rules = self.manufacturer_rules.get(manufacturer, [])
        generic_rules = self.manufacturer_rules.get('generic', [])
        
        # Combine manufacturer-specific and generic rules
        all_rules = base_rules + generic_rules
        
        # Filter rules based on configuration (e.g., HASL vs ENIG for AISLER)
        if manufacturer == 'aisler' and config != 'auto':
            if 'hasl' in config.lower():
                # Filter to HASL rules only
                all_rules = [r for r in all_rules if 'enig' not in r.name.lower()]
            elif 'enig' in config.lower():
                # Filter to ENIG rules only  
                all_rules = [r for r in all_rules if 'hasl' not in r.name.lower()]
                
        return all_rules
        
    def _check_design_rules(self, project_data: Dict[str, Any], 
                           rules: List[DFMRule]) -> List[DFMViolation]:
        """Check design against DFM rules"""
        violations = []
        
        # Extract design data
        pcb_data = project_data.get('pcb_analysis', {})
        
        for rule in rules:
            violation = self._check_single_rule(rule, pcb_data, project_data)
            if violation:
                violations.append(violation)
                
        return violations
        
    def _check_single_rule(self, rule: DFMRule, pcb_data: Dict[str, Any],
                          project_data: Dict[str, Any]) -> Optional[DFMViolation]:
        """Check a single DFM rule against design data"""
        
        # Extract relevant values based on rule category
        actual_value = None
        location = "Unknown"
        
        if rule.category == "trace":
            traces = pcb_data.get('traces', [])
            if traces:
                trace_widths = [t.get('width', 0.2) for t in traces]
                actual_value = min(trace_widths)
                location = "Minimum trace width found"
                
        elif rule.category == "drill":
            vias = pcb_data.get('vias', [])
            if vias:
                drill_sizes = [v.get('drill_diameter', 0.3) for v in vias]
                actual_value = min(drill_sizes)
                location = "Minimum drill size found"
                
        elif rule.category == "spacing":
            # This would require more complex PCB parsing
            # For now, use estimated values
            if 'min_spacing' in pcb_data:
                actual_value = pcb_data['min_spacing']
                location = "Minimum spacing analysis"
            else:
                # Skip spacing checks if no data available
                return None
                
        elif rule.category == "board":
            board_size = pcb_data.get('board_size', (50.0, 50.0))
            if rule.name.endswith('min_board_size'):
                actual_value = min(board_size)
                location = "Board minimum dimension"
            elif rule.name.endswith('max_board_size'):
                actual_value = max(board_size)
                location = "Board maximum dimension"
                
        # Check if we have data to validate
        if actual_value is None:
            return None
            
        # Check rule violations
        violation_found = False
        required_value = None
        
        if rule.min_value is not None and actual_value < rule.min_value:
            violation_found = True
            required_value = rule.min_value
            
        if rule.max_value is not None and actual_value > rule.max_value:
            violation_found = True
            required_value = rule.max_value
            
        if not violation_found:
            return None
            
        # Generate cognitive suggestion
        cognitive_suggestion = self._generate_cognitive_suggestion(rule, actual_value, required_value)
        
        return DFMViolation(
            rule_name=rule.name,
            severity=rule.severity,
            location=location,
            actual_value=actual_value,
            required_value=required_value,
            description=rule.description,
            cognitive_suggestion=cognitive_suggestion
        )
        
    def _generate_cognitive_suggestion(self, rule: DFMRule, actual: float, required: float) -> str:
        """Generate intelligent suggestion for fixing DFM violation"""
        suggestions = {
            'trace': f"Increase trace width from {actual:.3f}mm to {required:.3f}mm. Consider using wider traces or different routing strategy.",
            'drill': f"Increase drill size from {actual:.3f}mm to {required:.3f}mm. Check via sizes and component requirements.",
            'spacing': f"Increase spacing from {actual:.3f}mm to {required:.3f}mm. Move traces apart or use different layer.",
            'board': f"Adjust board size from {actual:.1f}mm to meet {required:.1f}mm requirement."
        }
        
        base_suggestion = suggestions.get(rule.category, "Adjust design to meet requirement.")
        
        # Add manufacturer-specific advice
        if 'aisler' in rule.name:
            if 'enig' in rule.name:
                base_suggestion += " Consider AISLER ENIG process for finer features."
            else:
                base_suggestion += " AISLER HASL process limitations apply."
                
        return base_suggestion
        
    def _calculate_dfm_score(self, violations: List[DFMViolation], total_rules: int) -> float:
        """Calculate overall DFM score (0.0 to 1.0)"""
        if total_rules == 0:
            return 1.0
            
        # Weight violations by severity
        violation_weight = 0
        for violation in violations:
            if violation.severity == 'error':
                violation_weight += 1.0
            elif violation.severity == 'warning':
                violation_weight += 0.5
            else:  # info
                violation_weight += 0.1
                
        # Calculate score
        max_possible_weight = total_rules * 1.0  # All errors would be worst case
        score = max(0.0, 1.0 - (violation_weight / max_possible_weight))
        
        return round(score, 3)
        
    def _generate_dfm_recommendations(self, violations: List[DFMViolation], 
                                    manufacturer: str) -> List[str]:
        """Generate prioritized DFM recommendations"""
        recommendations = []
        
        # Group violations by category
        violation_categories = {}
        for violation in violations:
            category = violation.rule_name.split('_')[1] if '_' in violation.rule_name else 'general'
            if category not in violation_categories:
                violation_categories[category] = []
            violation_categories[category].append(violation)
            
        # Generate category-specific recommendations
        for category, category_violations in violation_categories.items():
            error_count = sum(1 for v in category_violations if v.severity == 'error')
            warning_count = sum(1 for v in category_violations if v.severity == 'warning')
            
            if error_count > 0:
                recommendations.append(
                    f"CRITICAL: Fix {error_count} {category} errors for {manufacturer} compatibility"
                )
                
            if warning_count > 0:
                recommendations.append(
                    f"Optimize {warning_count} {category} warnings for better manufacturability"
                )
                
        # Add manufacturer-specific advice
        if manufacturer == 'aisler':
            recommendations.append("Consider uploading native KiCad files to AISLER for best results")
            recommendations.append("Review AISLER design rules at community.aisler.net")
            
        return recommendations
        
    def _generate_cognitive_insights(self, violations: List[DFMViolation],
                                   project_data: Dict[str, Any], 
                                   manufacturer: str) -> Dict[str, Any]:
        """Generate cognitive insights about DFM violations"""
        insights = {
            'violation_patterns': [],
            'optimization_opportunities': [],
            'learned_fixes': [],
            'cross_manufacturer_comparison': {}
        }
        
        # Analyze violation patterns
        if len(violations) > 5:
            insights['violation_patterns'].append("High violation count suggests design needs optimization")
            
        trace_violations = [v for v in violations if 'trace' in v.rule_name]
        if len(trace_violations) > 2:
            insights['violation_patterns'].append("Multiple trace width issues - consider design rule review")
            
        # Optimization opportunities
        if manufacturer == 'aisler':
            enig_violations = [v for v in violations if 'hasl' in v.rule_name]
            if enig_violations:
                insights['optimization_opportunities'].append(
                    "Switch to AISLER ENIG process for finer features"
                )
                
        # Apply learned patterns from cognitive system
        if self.context and hasattr(self.context, 'learned_patterns'):
            dfm_patterns = self.context.learned_patterns.get('dfm_fixes', [])
            insights['learned_fixes'] = [
                pattern.get('fix', '') for pattern in dfm_patterns[-3:]
                if pattern.get('success', False)
            ]
            
        return insights
        
    def compare_manufacturers(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare project against multiple manufacturers"""
        comparison = {
            'project_name': project_data.get('name', 'Unknown'),
            'manufacturer_results': {},
            'recommendations': []
        }
        
        manufacturers = ['aisler', 'jlcpcb']
        
        for manufacturer in manufacturers:
            result = self.validate_design(project_data, manufacturer)
            if result['success']:
                validation = result['validation']
                comparison['manufacturer_results'][manufacturer] = {
                    'overall_status': validation['overall_status'],
                    'dfm_score': validation['dfm_score'],
                    'error_count': len([v for v in validation['violations'] if v.severity == 'error']),
                    'warning_count': len([v for v in validation['violations'] if v.severity == 'warning'])
                }
                
        # Generate cross-manufacturer recommendations
        if comparison['manufacturer_results']:
            best_manufacturer = max(
                comparison['manufacturer_results'].items(),
                key=lambda x: x[1]['dfm_score']
            )
            comparison['recommendations'].append(
                f"Best DFM compatibility: {best_manufacturer[0]} (score: {best_manufacturer[1]['dfm_score']:.1%})"
            )
            
        return comparison