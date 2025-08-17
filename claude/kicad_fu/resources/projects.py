#!/usr/bin/env python3
"""
KiCad-Fu Project Resources - Intelligent Project Data Access

Provides cognitive-enhanced access to KiCad project information.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import asdict

class ProjectResource:
    """Resource handler for KiCad project data with cognitive enhancements"""
    
    def __init__(self, context):
        self.context = context
        self.config = context.config
        
    def get_projects_list(self) -> Dict[str, Any]:
        """Get list of all discovered projects with cognitive insights"""
        projects = self.context.discover_projects()
        
        # Enhanced project data with predictions
        enhanced_projects = []
        for project in projects:
            project_data = asdict(project)
            
            # Add cognitive enhancements
            project_data['cognitive_insights'] = {
                'predicted_operations': project.predicted_next_operations,
                'complexity_assessment': self._assess_complexity(project),
                'optimization_opportunities': self._identify_optimizations(project),
                'learned_patterns': project.learned_patterns
            }
            
            enhanced_projects.append(project_data)
            
        return {
            'projects': enhanced_projects,
            'total_count': len(enhanced_projects),
            'cognitive_enhancements': {
                'predictions_enabled': self.config.enable_predictive_planning,
                'learning_enabled': self.config.knowledge_crystallization,
                'evolution_enabled': self.config.enable_failure_evolution
            },
            'discovery_timestamp': projects[0].last_modified if projects else None
        }
        
    def get_project_details(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific project"""
        if project_name not in self.context.project_registry:
            return None
            
        project = self.context.project_registry[project_name]
        project_data = asdict(project)
        
        # Add deep cognitive analysis
        project_data['deep_analysis'] = {
            'performance_history': self._get_performance_history(project_name),
            'operation_patterns': self._analyze_operation_patterns(project_name),
            'risk_assessment': self._assess_project_risks(project),
            'optimization_recommendations': self._generate_optimizations(project),
            'cross_domain_insights': self._get_cross_domain_insights(project)
        }
        
        # Add real-time predictions
        project_data['real_time_predictions'] = self.context.get_project_predictions(project_name)
        
        return project_data
        
    def get_master_of_muppets_status(self) -> Dict[str, Any]:
        """Get special status for our Master of Muppets project"""
        mom_path = self.config.get_master_of_muppets_path()
        
        if not mom_path.exists():
            return {'status': 'not_found', 'path': str(mom_path)}
            
        # Analyze Master of Muppets project
        project_name = "MasterOfMuppets"
        
        status = {
            'status': 'found',
            'path': str(mom_path),
            'project_name': project_name,
            'cognitive_enhancements': {}
        }
        
        # Get project details if available
        if project_name in self.context.project_registry:
            project = self.context.project_registry[project_name]
            status.update({
                'components_count': project.components_count,
                'nets_count': project.nets_count,
                'complexity_score': project.complexity_score,
                'last_modified': project.last_modified
            })
            
            # Master of Muppets specific analysis
            status['master_of_muppets_analysis'] = {
                'pcb_components': project.components_count,
                'expected_components': 147,  # From our previous analysis
                'component_match': project.components_count == 147,
                'design_status': 'complete' if project.components_count >= 140 else 'in_progress',
                'optimization_score': self._calculate_mom_optimization_score(project)
            }
            
        return status
        
    def _assess_complexity(self, project) -> str:
        """Assess project complexity level"""
        if project.complexity_score < 0.3:
            return "simple"
        elif project.complexity_score < 0.7:
            return "moderate"
        else:
            return "complex"
            
    def _identify_optimizations(self, project) -> List[str]:
        """Identify optimization opportunities for project"""
        opportunities = []
        
        if project.components_count > 100:
            opportunities.append("Consider component placement optimization")
            
        if project.nets_count > 200:
            opportunities.append("Analyze routing efficiency")
            
        if project.complexity_score > 0.8:
            opportunities.append("Review design rule constraints")
            
        # Add learned optimizations from patterns
        pattern_key = f"optimization_{project.name}"
        if pattern_key in self.context.learned_patterns:
            recent_patterns = self.context.learned_patterns[pattern_key][-5:]
            for pattern in recent_patterns:
                if 'optimization' in pattern:
                    opportunities.append(pattern['optimization'])
                    
        return opportunities
        
    def _get_performance_history(self, project_name: str) -> List[Dict[str, Any]]:
        """Get performance history for project operations"""
        history = []
        
        for operation in self.context.operation_history:
            if operation.project_name == project_name:
                history.append({
                    'operation_type': operation.operation_type,
                    'duration_ms': operation.duration_ms,
                    'success': operation.success,
                    'timestamp': operation.end_time
                })
                
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)[:10]
        
    def _analyze_operation_patterns(self, project_name: str) -> Dict[str, Any]:
        """Analyze patterns in project operations"""
        patterns = {}
        
        # Collect operations for this project
        project_ops = [op for op in self.context.operation_history 
                      if op.project_name == project_name]
        
        if not project_ops:
            return patterns
            
        # Most common operations
        op_counts = {}
        for op in project_ops:
            op_counts[op.operation_type] = op_counts.get(op.operation_type, 0) + 1
            
        patterns['most_common_operations'] = sorted(op_counts.items(), 
                                                  key=lambda x: x[1], reverse=True)[:5]
        
        # Average durations
        op_durations = {}
        for op in project_ops:
            if op.operation_type not in op_durations:
                op_durations[op.operation_type] = []
            op_durations[op.operation_type].append(op.duration_ms)
            
        patterns['average_durations'] = {
            op_type: sum(durations) / len(durations)
            for op_type, durations in op_durations.items()
        }
        
        return patterns
        
    def _assess_project_risks(self, project) -> List[Dict[str, Any]]:
        """Assess potential risks for project"""
        risks = []
        
        if project.complexity_score > 0.8:
            risks.append({
                'type': 'complexity',
                'level': 'high',
                'description': 'High complexity project may have design challenges',
                'mitigation': 'Consider modular design approach'
            })
            
        if project.components_count > 200:
            risks.append({
                'type': 'component_count',
                'level': 'medium',
                'description': 'Large component count may affect manufacturability',
                'mitigation': 'Review BOM and consider component consolidation'
            })
            
        return risks
        
    def _generate_optimizations(self, project) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        optimizations = []
        
        # Component placement optimization
        if project.components_count > 50:
            optimizations.append({
                'type': 'component_placement',
                'priority': 'medium',
                'description': 'Optimize component placement for thermal and signal integrity',
                'estimated_benefit': 'Improved performance and manufacturability'
            })
            
        # Routing optimization
        if project.nets_count > 100:
            optimizations.append({
                'type': 'routing',
                'priority': 'high',
                'description': 'Analyze and optimize trace routing',
                'estimated_benefit': 'Reduced EMI and improved signal quality'
            })
            
        return optimizations
        
    def _get_cross_domain_insights(self, project) -> List[str]:
        """Get cross-domain insights from our cognitive systems"""
        insights = []
        
        # Apply software engineering principles to PCB design
        insights.append("Apply modular design principles from software architecture")
        insights.append("Consider hierarchical organization similar to code structure")
        
        # Apply our cognitive patterns
        if hasattr(self.context, 'profiler') and self.context.profiler:
            insights.append("Performance profiling suggests monitoring critical paths")
            
        if project.complexity_score > 0.7:
            insights.append("High complexity suggests need for systematic testing approach")
            
        return insights
        
    def _calculate_mom_optimization_score(self, project) -> float:
        """Calculate optimization score for Master of Muppets project"""
        score = 0.0
        
        # Component count accuracy
        if project.components_count == 147:
            score += 0.3
        elif abs(project.components_count - 147) < 10:
            score += 0.2
            
        # Complexity appropriateness
        if 0.6 <= project.complexity_score <= 0.8:
            score += 0.3
            
        # Design completeness
        if project.design_rules_status == "passed":
            score += 0.4
        elif project.design_rules_status == "unknown":
            score += 0.2
            
        return min(score, 1.0)