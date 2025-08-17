#!/usr/bin/env python3
"""
Predictive Cognitive Planning v1.0 - Anticipate future cognitive needs
Predicts what knowledge/tools will be needed and pre-compiles brain systems
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import re

# Import our existing systems for data and learning
from cognitive_performance_profiler import CognitivePerformanceProfiler
from knowledge_crystallization_engine import KnowledgeCrystallizationEngine
from failure_driven_evolution import FailureDrivenEvolution
from cross_domain_intelligence import CrossDomainIntelligence

@dataclass
class CognitivePrediction:
    """Prediction of future cognitive needs"""
    prediction_id: str
    predicted_need: str
    need_category: str  # tool, knowledge, brain_system, optimization
    confidence: float
    time_horizon: str  # immediate, short_term, medium_term, long_term
    trigger_conditions: List[str]
    preparation_actions: List[str]
    resource_requirements: Dict[str, Any]
    created: str

@dataclass
class PrecompiledBrain:
    """Pre-compiled brain system ready for deployment"""
    brain_id: str
    specialization: str
    compiled_knowledge: Dict[str, Any]
    decision_trees: Dict[str, Any]
    optimization_rules: List[str]
    activation_triggers: List[str]
    performance_metrics: Dict[str, float]
    ready_timestamp: str

@dataclass
class CognitiveFuture:
    """Anticipated future cognitive state"""
    future_id: str
    time_horizon: timedelta
    predicted_challenges: List[str]
    required_capabilities: List[str]
    knowledge_gaps: List[str]
    optimization_opportunities: List[str]
    preparation_plan: Dict[str, Any]
    confidence_score: float

class PredictiveCognitivePlanning:
    """Anticipates and prepares for future cognitive needs"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.predictions_db = self.project_root / 'claude' / 'brain_systems' / 'cognitive_predictions.json'
        self.precompiled_db = self.project_root / 'claude' / 'brain_systems' / 'precompiled_brains.json'
        self.futures_db = self.project_root / 'claude' / 'brain_systems' / 'cognitive_futures.json'
        
        # Connect to existing systems for data
        self.profiler = CognitivePerformanceProfiler(project_root)
        self.crystallizer = KnowledgeCrystallizationEngine(project_root)
        self.evolution = FailureDrivenEvolution(project_root)
        self.cross_domain = CrossDomainIntelligence(project_root)
        
        # Prediction storage
        self.predictions: List[CognitivePrediction] = []
        self.precompiled_brains: Dict[str, PrecompiledBrain] = {}
        self.cognitive_futures: List[CognitiveFuture] = []
        
        # Prediction models and patterns
        self.usage_patterns = defaultdict(list)
        self.temporal_patterns = defaultdict(list)
        self.context_transitions = defaultdict(list)
        
        # Planning parameters
        self.time_horizons = {
            'immediate': timedelta(minutes=5),
            'short_term': timedelta(hours=1),
            'medium_term': timedelta(hours=8),
            'long_term': timedelta(days=1)
        }
        
        self.prediction_confidence_threshold = 0.6
        self.precompilation_threshold = 0.7
        
        self.load_prediction_data()
        self._analyze_historical_patterns()
        
    def load_prediction_data(self):
        """Load existing prediction and planning data"""
        if self.predictions_db.exists():
            with open(self.predictions_db, 'r') as f:
                data = json.load(f)
                predictions_data = data.get('predictions', [])
                self.predictions = [
                    CognitivePrediction(**pred) for pred in predictions_data
                ]
                
        if self.precompiled_db.exists():
            with open(self.precompiled_db, 'r') as f:
                data = json.load(f)
                brains_data = data.get('brains', {})
                self.precompiled_brains = {
                    k: PrecompiledBrain(**v) for k, v in brains_data.items()
                }
                
        if self.futures_db.exists():
            with open(self.futures_db, 'r') as f:
                data = json.load(f)
                futures_data = data.get('futures', [])
                self.cognitive_futures = [
                    CognitiveFuture(**future) for future in futures_data
                ]
                
    def save_prediction_data(self):
        """Save prediction and planning data"""
        # Save predictions
        predictions_data = {
            'timestamp': datetime.now().isoformat(),
            'predictions': [asdict(pred) for pred in self.predictions],
            'total_predictions': len(self.predictions)
        }
        
        self.predictions_db.parent.mkdir(parents=True, exist_ok=True)
        with open(self.predictions_db, 'w') as f:
            json.dump(predictions_data, f, indent=2)
            
        # Save precompiled brains
        brains_data = {
            'timestamp': datetime.now().isoformat(),
            'brains': {k: asdict(v) for k, v in self.precompiled_brains.items()},
            'total_brains': len(self.precompiled_brains)
        }
        
        with open(self.precompiled_db, 'w') as f:
            json.dump(brains_data, f, indent=2)
            
        # Save cognitive futures (convert timedelta to string)
        futures_serializable = []
        for future in self.cognitive_futures:
            future_dict = asdict(future)
            # Convert timedelta to string
            if isinstance(future_dict['time_horizon'], timedelta):
                future_dict['time_horizon'] = str(future_dict['time_horizon'])
            futures_serializable.append(future_dict)
            
        futures_data = {
            'timestamp': datetime.now().isoformat(),
            'futures': futures_serializable,
            'total_futures': len(self.cognitive_futures)
        }
        
        with open(self.futures_db, 'w') as f:
            json.dump(futures_data, f, indent=2)
            
    def _analyze_historical_patterns(self):
        """Analyze historical data to identify predictive patterns"""
        print("[PREDICTIVE] Analyzing historical patterns for prediction models...")
        
        # Load historical performance data
        self.profiler.load_existing_data()
        historical_metrics = list(self.profiler.metrics)
        
        if not historical_metrics:
            print("[PREDICTIVE] No historical data available for pattern analysis")
            return
            
        # Analyze usage patterns
        for metric in historical_metrics:
            operation = metric.operation
            timestamp = datetime.fromisoformat(metric.timestamp)
            
            self.usage_patterns[operation].append({
                'timestamp': timestamp,
                'duration': metric.duration_ms,
                'outcome': metric.outcome,
                'context_complexity': metric.context_complexity
            })
            
        # Analyze temporal patterns (time-based usage)
        for operation, usage_list in self.usage_patterns.items():
            if len(usage_list) >= 3:
                # Group by hour of day
                hourly_usage = defaultdict(list)
                for usage in usage_list:
                    hour = usage['timestamp'].hour
                    hourly_usage[hour].append(usage)
                    
                self.temporal_patterns[operation] = dict(hourly_usage)
                
        # Analyze context transitions (what follows what)
        for i in range(len(historical_metrics) - 1):
            current_op = historical_metrics[i].operation
            next_op = historical_metrics[i + 1].operation
            
            if current_op != next_op:  # Transition between different operations
                self.context_transitions[current_op].append(next_op)
                
        print(f"[PREDICTIVE] Analyzed patterns for {len(self.usage_patterns)} operations")
        
    def predict_cognitive_needs(self, current_context: Dict[str, Any], 
                              prediction_horizon: str = 'short_term') -> List[CognitivePrediction]:
        """Predict future cognitive needs based on current context and patterns"""
        predictions = []
        
        print(f"[PREDICTIVE] Generating {prediction_horizon} cognitive predictions...")
        
        # 1. Predict based on usage patterns
        usage_predictions = self._predict_from_usage_patterns(current_context, prediction_horizon)
        predictions.extend(usage_predictions)
        
        # 2. Predict based on temporal patterns
        temporal_predictions = self._predict_from_temporal_patterns(current_context, prediction_horizon)
        predictions.extend(temporal_predictions)
        
        # 3. Predict based on context transitions
        transition_predictions = self._predict_from_context_transitions(current_context, prediction_horizon)
        predictions.extend(transition_predictions)
        
        # 4. Predict based on failure patterns
        failure_predictions = self._predict_from_failure_patterns(current_context, prediction_horizon)
        predictions.extend(failure_predictions)
        
        # 5. Predict based on cross-domain opportunities
        cross_domain_predictions = self._predict_from_cross_domain(current_context, prediction_horizon)
        predictions.extend(cross_domain_predictions)
        
        # Filter and rank predictions
        high_confidence_predictions = [
            pred for pred in predictions 
            if pred.confidence >= self.prediction_confidence_threshold
        ]
        
        # Sort by confidence
        high_confidence_predictions.sort(key=lambda x: x.confidence, reverse=True)
        
        # Add to prediction history
        self.predictions.extend(high_confidence_predictions)
        
        print(f"[PREDICTIVE] Generated {len(high_confidence_predictions)} high-confidence predictions")
        
        return high_confidence_predictions
        
    def _predict_from_usage_patterns(self, context: Dict[str, Any], horizon: str) -> List[CognitivePrediction]:
        """Predict needs based on usage patterns"""
        predictions = []
        
        current_operation = context.get('operation', 'unknown')
        
        # Find operations that frequently follow current operation
        if current_operation in self.context_transitions:
            transitions = self.context_transitions[current_operation]
            transition_freq = defaultdict(int)
            
            for next_op in transitions:
                transition_freq[next_op] += 1
                
            # Create predictions for frequent transitions
            total_transitions = len(transitions)
            for next_op, freq in transition_freq.items():
                confidence = freq / total_transitions
                
                if confidence > 0.3:  # Significant pattern
                    prediction = CognitivePrediction(
                        prediction_id=f"usage_{current_operation}_{next_op}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        predicted_need=f"Optimization for {next_op} operation",
                        need_category='optimization',
                        confidence=confidence,
                        time_horizon=horizon,
                        trigger_conditions=[f"After {current_operation} operation"],
                        preparation_actions=[f"Pre-load {next_op} optimization", f"Warm up {next_op} cache"],
                        resource_requirements={'cpu': 'low', 'memory': 'medium'},
                        created=datetime.now().isoformat()
                    )
                    predictions.append(prediction)
                    
        return predictions
        
    def _predict_from_temporal_patterns(self, context: Dict[str, Any], horizon: str) -> List[CognitivePrediction]:
        """Predict needs based on temporal patterns"""
        predictions = []
        
        current_hour = datetime.now().hour
        
        # Predict operations likely to be needed in next time window
        for operation, hourly_data in self.temporal_patterns.items():
            # Check if this operation has high usage in upcoming hours
            upcoming_hours = [(current_hour + i) % 24 for i in range(1, 4)]  # Next 3 hours
            
            upcoming_usage = sum(len(hourly_data.get(hour, [])) for hour in upcoming_hours)
            total_usage = sum(len(hourly_data.get(hour, [])) for hour in range(24))
            
            if total_usage > 0:
                upcoming_ratio = upcoming_usage / total_usage
                
                if upcoming_ratio > 0.2:  # High upcoming usage
                    prediction = CognitivePrediction(
                        prediction_id=f"temporal_{operation}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        predicted_need=f"Increased demand for {operation}",
                        need_category='tool',
                        confidence=upcoming_ratio,
                        time_horizon=horizon,
                        trigger_conditions=[f"Approaching high-usage hours for {operation}"],
                        preparation_actions=[f"Pre-compile {operation} brain", f"Optimize {operation} performance"],
                        resource_requirements={'cpu': 'medium', 'memory': 'high'},
                        created=datetime.now().isoformat()
                    )
                    predictions.append(prediction)
                    
        return predictions
        
    def _predict_from_context_transitions(self, context: Dict[str, Any], horizon: str) -> List[CognitivePrediction]:
        """Predict needs based on context transitions"""
        predictions = []
        
        # Look for patterns in context evolution
        context_keys = set(context.keys())
        
        # Predict missing context elements that often appear together
        for operation, usage_list in self.usage_patterns.items():
            if len(usage_list) >= 3:
                # Find common context patterns
                common_contexts = []
                for usage in usage_list[-10:]:  # Recent usage
                    if hasattr(usage, 'context'):
                        common_contexts.append(set(usage.context.keys()) if usage.context else set())
                        
                if common_contexts:
                    # Find contexts that often appear together
                    from collections import Counter
                    all_context_elements = [elem for ctx in common_contexts for elem in ctx]
                    frequent_elements = Counter(all_context_elements)
                    
                    for element, freq in frequent_elements.items():
                        if element not in context_keys and freq > len(common_contexts) * 0.5:
                            prediction = CognitivePrediction(
                                prediction_id=f"context_{operation}_{element}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                predicted_need=f"Context element: {element}",
                                need_category='knowledge',
                                confidence=freq / len(common_contexts),
                                time_horizon=horizon,
                                trigger_conditions=[f"Pattern suggests {element} will be needed"],
                                preparation_actions=[f"Prepare {element} context", f"Load {element} knowledge"],
                                resource_requirements={'memory': 'low'},
                                created=datetime.now().isoformat()
                            )
                            predictions.append(prediction)
                            
        return predictions
        
    def _predict_from_failure_patterns(self, context: Dict[str, Any], horizon: str) -> List[CognitivePrediction]:
        """Predict needs based on failure patterns"""
        predictions = []
        
        # Load failure data
        self.evolution.load_failure_data()
        
        # Predict potential failures and needed preventions
        for signature_id, signature in self.evolution.failure_signatures.items():
            # Calculate risk based on context similarity
            current_fingerprint = self.evolution._create_context_fingerprint({'context': context})
            
            # Simple similarity check
            similarity = len(set(signature.context_fingerprint) & set(current_fingerprint)) / max(len(signature.context_fingerprint), 1)
            
            if similarity > 0.3:  # Context suggests potential for this failure
                risk_score = similarity * signature.severity * (signature.frequency / 10.0)
                
                if risk_score > 0.2:  # Significant risk
                    prediction = CognitivePrediction(
                        prediction_id=f"failure_prevention_{signature_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        predicted_need=f"Prevention for {signature.error_pattern}",
                        need_category='brain_system',
                        confidence=risk_score,
                        time_horizon=horizon,
                        trigger_conditions=[f"Context similar to {signature.error_pattern} failures"],
                        preparation_actions=[f"Load immunity response", f"Enable preventive measures"],
                        resource_requirements={'cpu': 'low', 'memory': 'low'},
                        created=datetime.now().isoformat()
                    )
                    predictions.append(prediction)
                    
        return predictions
        
    def _predict_from_cross_domain(self, context: Dict[str, Any], horizon: str) -> List[CognitivePrediction]:
        """Predict needs based on cross-domain opportunities"""
        predictions = []
        
        current_domain = context.get('domain', 'unknown')
        
        # Load cross-domain data
        self.cross_domain.load_domain_data()
        
        # Predict cross-domain knowledge that might be useful
        for mapping_id, mapping in self.cross_domain.cross_mappings.items():
            if mapping.target_domain == current_domain and mapping.similarity_score > 0.6:
                prediction = CognitivePrediction(
                    prediction_id=f"cross_domain_{mapping_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    predicted_need=f"Cross-domain insight from {mapping.source_domain}",
                    need_category='knowledge',
                    confidence=mapping.similarity_score,
                    time_horizon=horizon,
                    trigger_conditions=[f"Working in {current_domain} domain"],
                    preparation_actions=[f"Load {mapping.source_domain} knowledge", f"Prepare transfer mechanisms"],
                    resource_requirements={'memory': 'medium'},
                    created=datetime.now().isoformat()
                )
                predictions.append(prediction)
                
        return predictions
        
    def precompile_brain_systems(self, predictions: List[CognitivePrediction]) -> List[PrecompiledBrain]:
        """Pre-compile brain systems based on predictions"""
        new_brains = []
        
        print("[PREDICTIVE] Pre-compiling brain systems...")
        
        # Group predictions by need type
        brain_needs = defaultdict(list)
        for pred in predictions:
            if pred.confidence >= self.precompilation_threshold:
                brain_needs[pred.need_category].append(pred)
                
        # Compile brains for each need type
        for need_category, pred_list in brain_needs.items():
            if len(pred_list) >= 2:  # Need multiple predictions to justify compilation
                brain = self._compile_specialized_brain(need_category, pred_list)
                if brain:
                    new_brains.append(brain)
                    self.precompiled_brains[brain.brain_id] = brain
                    
        print(f"[PREDICTIVE] Pre-compiled {len(new_brains)} brain systems")
        return new_brains
        
    def _compile_specialized_brain(self, specialization: str, predictions: List[CognitivePrediction]) -> Optional[PrecompiledBrain]:
        """Compile a specialized brain system"""
        
        # Aggregate knowledge from predictions
        compiled_knowledge = {
            'specialization': specialization,
            'predicted_scenarios': [pred.predicted_need for pred in predictions],
            'confidence_scores': [pred.confidence for pred in predictions],
            'preparation_actions': [action for pred in predictions for action in pred.preparation_actions]
        }
        
        # Create decision trees based on trigger conditions
        decision_trees = {}
        for i, pred in enumerate(predictions):
            decision_trees[f"scenario_{i}"] = {
                'conditions': pred.trigger_conditions,
                'actions': pred.preparation_actions,
                'confidence': pred.confidence
            }
            
        # Create optimization rules
        optimization_rules = []
        for pred in predictions:
            if pred.need_category == 'optimization':
                optimization_rules.append(f"IF {pred.trigger_conditions[0]} THEN {pred.preparation_actions[0]}")
                
        # Set activation triggers
        activation_triggers = list(set([trigger for pred in predictions for trigger in pred.trigger_conditions]))
        
        # Calculate performance metrics
        avg_confidence = sum(pred.confidence for pred in predictions) / len(predictions)
        coverage_score = len(set(pred.predicted_need for pred in predictions)) / len(predictions)
        
        performance_metrics = {
            'average_confidence': avg_confidence,
            'scenario_coverage': coverage_score,
            'prediction_count': len(predictions),
            'specialization_focus': specialization
        }
        
        brain = PrecompiledBrain(
            brain_id=f"precompiled_{specialization}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            specialization=specialization,
            compiled_knowledge=compiled_knowledge,
            decision_trees=decision_trees,
            optimization_rules=optimization_rules,
            activation_triggers=activation_triggers,
            performance_metrics=performance_metrics,
            ready_timestamp=datetime.now().isoformat()
        )
        
        return brain
        
    def plan_cognitive_future(self, time_horizon: str = 'medium_term') -> CognitiveFuture:
        """Plan for future cognitive state based on predictions"""
        
        horizon_delta = self.time_horizons[time_horizon]
        future_time = datetime.now() + horizon_delta
        
        print(f"[PREDICTIVE] Planning cognitive future for {time_horizon} ({horizon_delta})")
        
        # Aggregate predictions for this time horizon
        relevant_predictions = [
            pred for pred in self.predictions 
            if pred.time_horizon == time_horizon
        ]
        
        # Identify challenges
        predicted_challenges = []
        for pred in relevant_predictions:
            if pred.need_category == 'brain_system':  # These represent challenges
                predicted_challenges.append(pred.predicted_need)
                
        # Identify required capabilities
        required_capabilities = []
        for pred in relevant_predictions:
            if pred.need_category in ['tool', 'optimization']:
                required_capabilities.extend(pred.preparation_actions)
                
        # Identify knowledge gaps
        knowledge_gaps = []
        for pred in relevant_predictions:
            if pred.need_category == 'knowledge':
                knowledge_gaps.append(pred.predicted_need)
                
        # Identify optimization opportunities
        optimization_opportunities = []
        for pred in relevant_predictions:
            if pred.need_category == 'optimization':
                optimization_opportunities.append(pred.predicted_need)
                
        # Create preparation plan
        preparation_plan = {
            'immediate_actions': [action for pred in relevant_predictions[:3] for action in pred.preparation_actions],
            'resource_allocation': self._aggregate_resource_requirements(relevant_predictions),
            'priority_order': [pred.predicted_need for pred in sorted(relevant_predictions, key=lambda x: x.confidence, reverse=True)],
            'contingency_plans': self._create_contingency_plans(relevant_predictions)
        }
        
        # Calculate confidence
        if relevant_predictions:
            confidence_score = sum(pred.confidence for pred in relevant_predictions) / len(relevant_predictions)
        else:
            confidence_score = 0.5  # Default moderate confidence
            
        cognitive_future = CognitiveFuture(
            future_id=f"future_{time_horizon}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            time_horizon=horizon_delta,
            predicted_challenges=predicted_challenges[:5],  # Top 5
            required_capabilities=required_capabilities[:5],
            knowledge_gaps=knowledge_gaps[:5],
            optimization_opportunities=optimization_opportunities[:5],
            preparation_plan=preparation_plan,
            confidence_score=confidence_score
        )
        
        self.cognitive_futures.append(cognitive_future)
        
        return cognitive_future
        
    def _aggregate_resource_requirements(self, predictions: List[CognitivePrediction]) -> Dict[str, str]:
        """Aggregate resource requirements from predictions"""
        cpu_levels = []
        memory_levels = []
        
        level_values = {'low': 1, 'medium': 2, 'high': 3}
        value_levels = {1: 'low', 2: 'medium', 3: 'high'}
        
        for pred in predictions:
            reqs = pred.resource_requirements
            if 'cpu' in reqs:
                cpu_levels.append(level_values.get(reqs['cpu'], 2))
            if 'memory' in reqs:
                memory_levels.append(level_values.get(reqs['memory'], 2))
                
        # Calculate aggregate levels
        avg_cpu = sum(cpu_levels) / len(cpu_levels) if cpu_levels else 2
        avg_memory = sum(memory_levels) / len(memory_levels) if memory_levels else 2
        
        return {
            'cpu': value_levels[round(avg_cpu)],
            'memory': value_levels[round(avg_memory)],
            'storage': 'medium',  # Default
            'network': 'low'      # Default
        }
        
    def _create_contingency_plans(self, predictions: List[CognitivePrediction]) -> List[str]:
        """Create contingency plans for predictions"""
        plans = []
        
        # Plan for prediction failures
        plans.append("If predictions fail: Fall back to reactive optimization")
        plans.append("If resources insufficient: Prioritize high-confidence predictions")
        plans.append("If new patterns emerge: Update prediction models")
        
        # Specific contingencies based on prediction types
        need_categories = set(pred.need_category for pred in predictions)
        
        if 'brain_system' in need_categories:
            plans.append("If brain systems fail: Activate backup general-purpose systems")
        if 'optimization' in need_categories:
            plans.append("If optimizations don't work: Revert to baseline performance")
        if 'knowledge' in need_categories:
            plans.append("If knowledge gaps persist: Initiate learning protocols")
            
        return plans[:5]  # Top 5 contingencies
        
    def activate_precompiled_brain(self, brain_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Activate a pre-compiled brain system"""
        if brain_id not in self.precompiled_brains:
            return {'error': f'Brain {brain_id} not found'}
            
        brain = self.precompiled_brains[brain_id]
        
        # Check activation triggers
        context_matches = any(
            trigger.lower() in str(context).lower() 
            for trigger in brain.activation_triggers
        )
        
        if not context_matches:
            return {'error': 'Activation triggers not met', 'triggers': brain.activation_triggers}
            
        # Activate the brain
        activation_result = {
            'brain_id': brain_id,
            'specialization': brain.specialization,
            'activated': True,
            'knowledge_loaded': brain.compiled_knowledge,
            'decision_trees_available': len(brain.decision_trees),
            'optimization_rules_active': len(brain.optimization_rules),
            'performance_metrics': brain.performance_metrics
        }
        
        print(f"[PREDICTIVE] Activated precompiled brain: {brain_id}")
        
        return activation_result
        
    def generate_planning_report(self) -> str:
        """Generate comprehensive predictive planning report"""
        report = f"""# Predictive Cognitive Planning Report
Generated: {datetime.now().isoformat()}

## Planning Summary
- **Cognitive Predictions**: {len(self.predictions)}
- **Precompiled Brains**: {len(self.precompiled_brains)}
- **Cognitive Futures**: {len(self.cognitive_futures)}
- **Usage Patterns Analyzed**: {len(self.usage_patterns)}

## Prediction Analysis
"""
        
        # Prediction categories
        category_counts = defaultdict(int)
        for pred in self.predictions:
            category_counts[pred.need_category] += 1
            
        for category, count in category_counts.items():
            report += f"- **{category.title()}**: {count} predictions\n"
            
        # High-confidence predictions
        high_conf_predictions = [p for p in self.predictions if p.confidence > 0.8]
        report += f"\n## High-Confidence Predictions ({len(high_conf_predictions)})\n"
        
        for pred in high_conf_predictions[:5]:  # Top 5
            report += f"- **{pred.predicted_need}**\n"
            report += f"  - Confidence: {pred.confidence:.1%}\n"
            report += f"  - Horizon: {pred.time_horizon}\n"
            report += f"  - Category: {pred.need_category}\n"
            
        # Precompiled brains
        report += f"\n## Precompiled Brain Systems ({len(self.precompiled_brains)})\n"
        
        for brain_id, brain in self.precompiled_brains.items():
            report += f"- **{brain.specialization.title()}** (ID: {brain_id})\n"
            report += f"  - Scenarios: {brain.performance_metrics.get('prediction_count', 0)}\n"
            report += f"  - Confidence: {brain.performance_metrics.get('average_confidence', 0):.1%}\n"
            report += f"  - Triggers: {len(brain.activation_triggers)}\n"
            
        # Cognitive futures
        if self.cognitive_futures:
            latest_future = self.cognitive_futures[-1]
            report += f"\n## Latest Cognitive Future Plan\n"
            report += f"- **Time Horizon**: {latest_future.time_horizon}\n"
            report += f"- **Confidence**: {latest_future.confidence_score:.1%}\n"
            report += f"- **Predicted Challenges**: {len(latest_future.predicted_challenges)}\n"
            report += f"- **Required Capabilities**: {len(latest_future.required_capabilities)}\n"
            report += f"- **Knowledge Gaps**: {len(latest_future.knowledge_gaps)}\n"
            
        return report

def main():
    """Test predictive cognitive planning system"""
    planner = PredictiveCognitivePlanning()
    
    print("[PREDICTIVE] ===== PREDICTIVE COGNITIVE PLANNING =====")
    
    # Test prediction with sample context
    test_context = {
        'operation': 'file_search',
        'domain': 'software_engineering',
        'complexity': 6,
        'time_of_day': datetime.now().hour
    }
    
    # Generate predictions
    predictions = planner.predict_cognitive_needs(test_context, 'short_term')
    
    # Pre-compile brain systems
    precompiled_brains = planner.precompile_brain_systems(predictions)
    
    # Plan cognitive future
    future_plan = planner.plan_cognitive_future('medium_term')
    
    # Test brain activation
    if precompiled_brains:
        activation_result = planner.activate_precompiled_brain(
            precompiled_brains[0].brain_id, 
            test_context
        )
        print(f"[PREDICTIVE] Brain activation result: {activation_result.get('activated', False)}")
        
    # Generate report
    report = planner.generate_planning_report()
    
    # Save all data
    planner.save_prediction_data()
    
    report_path = planner.project_root / 'predictive_planning_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"[PREDICTIVE] Planning report saved to: {report_path}")
    print(f"[PREDICTIVE] Predictions generated: {len(predictions)}")
    print(f"[PREDICTIVE] Brains precompiled: {len(precompiled_brains)}")
    print(f"[PREDICTIVE] Future confidence: {future_plan.confidence_score:.1%}")
    
    return planner

if __name__ == "__main__":
    main()