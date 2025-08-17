#!/usr/bin/env python3
"""
Knowledge Crystallization Engine v1.0 - Transform experience into compressed wisdom
Converts patterns into mathematical formulas, decision trees, and wisdom bytecode
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
import re
import ast

# Import our performance profiler for learning from it
from cognitive_performance_profiler import CognitivePerformanceProfiler, CognitiveMetric

@dataclass
class CrystalizedKnowledge:
    """Compressed knowledge representation"""
    knowledge_id: str
    source_patterns: List[str]
    crystallized_form: str  # mathematical, bytecode, or rule
    compression_ratio: float
    confidence_score: float
    usage_frequency: int
    creation_timestamp: str
    knowledge_type: str  # formula, decision_tree, rule, bytecode

@dataclass
class WisdomFormula:
    """Mathematical formula derived from experience"""
    formula_id: str
    variables: List[str]
    equation: str
    accuracy: float
    domain: str
    examples: List[Dict[str, Any]]

class KnowledgeCrystallizationEngine:
    """Transforms experience patterns into compressed, reusable wisdom"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.crystals_file = self.project_root / 'claude' / 'brain_systems' / 'crystallized_knowledge.json'
        self.formulas_file = self.project_root / 'claude' / 'brain_systems' / 'wisdom_formulas.json'
        self.bytecode_file = self.project_root / 'claude' / 'brain_systems' / 'wisdom_bytecode.json'
        
        # Connect to performance profiler for learning source
        self.profiler = CognitivePerformanceProfiler(project_root)
        
        # Knowledge storage
        self.crystallized_knowledge: List[CrystalizedKnowledge] = []
        self.wisdom_formulas: List[WisdomFormula] = []
        self.decision_trees = {}
        self.bytecode_library = {}
        
        # Crystallization algorithms
        self.pattern_extractors = {
            'performance_patterns': self._extract_performance_patterns,
            'error_patterns': self._extract_error_patterns,
            'success_patterns': self._extract_success_patterns,
            'efficiency_patterns': self._extract_efficiency_patterns
        }
        
        self.load_existing_crystals()
        
    def load_existing_crystals(self):
        """Load existing crystallized knowledge"""
        if self.crystals_file.exists():
            with open(self.crystals_file, 'r') as f:
                data = json.load(f)
                self.crystallized_knowledge = [
                    CrystalizedKnowledge(**crystal) for crystal in data.get('crystals', [])
                ]
                
        if self.formulas_file.exists():
            with open(self.formulas_file, 'r') as f:
                data = json.load(f)
                self.wisdom_formulas = [
                    WisdomFormula(**formula) for formula in data.get('formulas', [])
                ]
                
        if self.bytecode_file.exists():
            with open(self.bytecode_file, 'r') as f:
                self.bytecode_library = json.load(f)
                
    def save_crystallized_knowledge(self):
        """Save all crystallized knowledge"""
        # Save crystals
        crystals_data = {
            'timestamp': datetime.now().isoformat(),
            'crystals': [asdict(crystal) for crystal in self.crystallized_knowledge],
            'total_crystals': len(self.crystallized_knowledge)
        }
        
        self.crystals_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.crystals_file, 'w') as f:
            json.dump(crystals_data, f, indent=2)
            
        # Save formulas
        formulas_data = {
            'timestamp': datetime.now().isoformat(),
            'formulas': [asdict(formula) for formula in self.wisdom_formulas],
            'total_formulas': len(self.wisdom_formulas)
        }
        
        with open(self.formulas_file, 'w') as f:
            json.dump(formulas_data, f, indent=2)
            
        # Save bytecode
        with open(self.bytecode_file, 'w') as f:
            json.dump(self.bytecode_library, f, indent=2)
            
    def crystallize_experience(self, experience_data: List[Dict[str, Any]]) -> List[CrystalizedKnowledge]:
        """Main crystallization process - convert experience to wisdom"""
        new_crystals = []
        
        print("[CRYSTALLIZATION] Starting experience crystallization...")
        
        # Extract patterns using different algorithms
        for pattern_type, extractor in self.pattern_extractors.items():
            patterns = extractor(experience_data)
            
            for pattern in patterns:
                crystal = self._crystallize_pattern(pattern, pattern_type)
                if crystal:
                    new_crystals.append(crystal)
                    self.crystallized_knowledge.append(crystal)
                    
        # Generate mathematical formulas from numeric patterns
        formulas = self._derive_mathematical_formulas(experience_data)
        self.wisdom_formulas.extend(formulas)
        
        # Compile high-value patterns into bytecode
        bytecode_entries = self._compile_to_bytecode(new_crystals)
        self.bytecode_library.update(bytecode_entries)
        
        print(f"[CRYSTALLIZATION] Created {len(new_crystals)} new crystals, {len(formulas)} formulas")
        
        return new_crystals
        
    def _extract_performance_patterns(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract performance optimization patterns"""
        patterns = []
        
        # Group by operation type
        operations = defaultdict(list)
        for item in data:
            if 'operation' in item:
                operations[item['operation']].append(item)
                
        for operation, metrics in operations.items():
            if len(metrics) >= 5:  # Need sufficient data
                durations = [m.get('duration_ms', 0) for m in metrics]
                accuracies = [m.get('accuracy_score', 0) for m in metrics]
                
                # Identify performance pattern
                avg_duration = sum(durations) / len(durations)
                avg_accuracy = sum(accuracies) / len(accuracies)
                
                if avg_duration > 100:  # Slow operation
                    patterns.append({
                        'type': 'slow_operation',
                        'operation': operation,
                        'avg_duration': avg_duration,
                        'sample_count': len(metrics),
                        'optimization_potential': min(avg_duration / 10, 10)  # Max 10x improvement
                    })
                    
                if avg_accuracy > 0.9:  # High accuracy operation
                    patterns.append({
                        'type': 'high_accuracy_operation',
                        'operation': operation,
                        'accuracy': avg_accuracy,
                        'reliability_score': avg_accuracy * (len(metrics) / 10)
                    })
                    
        return patterns
        
    def _extract_error_patterns(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract error prevention patterns"""
        patterns = []
        
        errors = [item for item in data if item.get('outcome') == 'error']
        successes = [item for item in data if item.get('outcome') == 'success']
        
        if errors:
            # Find common error contexts
            error_contexts = [item.get('context', {}) for item in errors]
            success_contexts = [item.get('context', {}) for item in successes]
            
            # Identify error-prone conditions
            error_indicators = self._find_discriminating_features(error_contexts, success_contexts)
            
            if error_indicators:
                patterns.append({
                    'type': 'error_prevention',
                    'error_indicators': error_indicators,
                    'error_count': len(errors),
                    'success_count': len(successes),
                    'prevention_confidence': len(error_indicators) / max(len(error_contexts), 1)
                })
                
        return patterns
        
    def _extract_success_patterns(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract success strategy patterns"""
        patterns = []
        
        successes = [item for item in data if item.get('outcome') == 'success']
        
        if len(successes) >= 3:
            # Find common success factors
            contexts = [item.get('context', {}) for item in successes]
            common_factors = self._find_common_elements(contexts)
            
            if common_factors:
                patterns.append({
                    'type': 'success_strategy',
                    'success_factors': common_factors,
                    'success_count': len(successes),
                    'strategy_confidence': len(common_factors) / max(len(contexts), 1)
                })
                
        return patterns
        
    def _extract_efficiency_patterns(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract efficiency optimization patterns"""
        patterns = []
        
        # Find operations with improving performance over time
        operations = defaultdict(list)
        for item in data:
            if 'operation' in item and 'timestamp' in item:
                operations[item['operation']].append(item)
                
        for operation, metrics in operations.items():
            if len(metrics) >= 5:
                # Sort by timestamp
                sorted_metrics = sorted(metrics, key=lambda x: x['timestamp'])
                
                # Check for improvement trend
                first_half = sorted_metrics[:len(sorted_metrics)//2]
                second_half = sorted_metrics[len(sorted_metrics)//2:]
                
                if first_half and second_half:
                    first_avg = sum([m.get('duration_ms', 0) for m in first_half]) / len(first_half)
                    second_avg = sum([m.get('duration_ms', 0) for m in second_half]) / len(second_half)
                    
                    improvement = (first_avg - second_avg) / first_avg if first_avg > 0 else 0
                    
                    if improvement > 0.1:  # 10% improvement
                        patterns.append({
                            'type': 'efficiency_improvement',
                            'operation': operation,
                            'improvement_rate': improvement,
                            'baseline_duration': first_avg,
                            'optimized_duration': second_avg
                        })
                        
        return patterns
        
    def _find_discriminating_features(self, group_a: List[Dict], group_b: List[Dict]) -> Dict[str, float]:
        """Find features that discriminate between two groups"""
        features = {}
        
        # Count feature frequencies in each group
        features_a = defaultdict(int)
        features_b = defaultdict(int)
        
        for context in group_a:
            for key, value in context.items():
                feature = f"{key}:{value}"
                features_a[feature] += 1
                
        for context in group_b:
            for key, value in context.items():
                feature = f"{key}:{value}"
                features_b[feature] += 1
                
        # Calculate discrimination scores
        for feature in set(features_a.keys()) | set(features_b.keys()):
            freq_a = features_a[feature] / max(len(group_a), 1)
            freq_b = features_b[feature] / max(len(group_b), 1)
            
            # Higher score = better discriminator
            discrimination_score = abs(freq_a - freq_b)
            if discrimination_score > 0.3:  # Threshold for significance
                features[feature] = discrimination_score
                
        return features
        
    def _find_common_elements(self, contexts: List[Dict]) -> Dict[str, float]:
        """Find commonly occurring elements across contexts"""
        element_counts = defaultdict(int)
        
        for context in contexts:
            for key, value in context.items():
                element = f"{key}:{value}"
                element_counts[element] += 1
                
        # Return elements that appear in >50% of contexts
        threshold = len(contexts) * 0.5
        common = {}
        for element, count in element_counts.items():
            if count >= threshold:
                common[element] = count / len(contexts)
                
        return common
        
    def _crystallize_pattern(self, pattern: Dict[str, Any], pattern_type: str) -> Optional[CrystalizedKnowledge]:
        """Crystallize a single pattern into compressed knowledge"""
        pattern_str = json.dumps(pattern, sort_keys=True)
        
        # Create different crystallized forms based on pattern type
        if pattern['type'] == 'slow_operation':
            crystallized_form = self._create_performance_rule(pattern)
        elif pattern['type'] == 'error_prevention':
            crystallized_form = self._create_error_prevention_rule(pattern)
        elif pattern['type'] == 'success_strategy':
            crystallized_form = self._create_success_rule(pattern)
        elif pattern['type'] == 'efficiency_improvement':
            crystallized_form = self._create_efficiency_rule(pattern)
        else:
            crystallized_form = f"PATTERN({pattern['type']}): {pattern_str}"
            
        # Calculate compression ratio
        original_size = len(pattern_str)
        compressed_size = len(crystallized_form)
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
        
        # Calculate confidence score
        confidence = self._calculate_pattern_confidence(pattern)
        
        crystal = CrystalizedKnowledge(
            knowledge_id=f"{pattern_type}_{pattern['type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_patterns=[pattern_type],
            crystallized_form=crystallized_form,
            compression_ratio=compression_ratio,
            confidence_score=confidence,
            usage_frequency=0,
            creation_timestamp=datetime.now().isoformat(),
            knowledge_type='rule'
        )
        
        return crystal
        
    def _create_performance_rule(self, pattern: Dict[str, Any]) -> str:
        """Create performance optimization rule"""
        operation = pattern['operation']
        avg_duration = pattern['avg_duration']
        optimization_potential = pattern.get('optimization_potential', 1)
        
        return f"""
IF operation == '{operation}' AND duration > {avg_duration * 0.8}:
    APPLY optimization_level({optimization_potential})
    CONSIDER caching_strategy()
    LOG performance_optimization('{operation}')
"""
        
    def _create_error_prevention_rule(self, pattern: Dict[str, Any]) -> str:
        """Create error prevention rule"""
        indicators = pattern['error_indicators']
        confidence = pattern['prevention_confidence']
        
        conditions = []
        for indicator, score in indicators.items():
            if score > 0.5:
                conditions.append(f"context.contains('{indicator}')")
                
        rule = f"""
IF {' OR '.join(conditions[:3])}:  # Top 3 indicators
    WARN high_error_risk(confidence={confidence:.2f})
    SUGGEST alternative_approach()
    ENABLE extra_validation()
"""
        return rule
        
    def _create_success_rule(self, pattern: Dict[str, Any]) -> str:
        """Create success strategy rule"""
        factors = pattern['success_factors']
        confidence = pattern['strategy_confidence']
        
        conditions = []
        for factor, score in factors.items():
            if score > 0.6:
                conditions.append(f"context.has('{factor}')")
                
        rule = f"""
FOR optimal_success(confidence={confidence:.2f}):
    ENSURE {' AND '.join(conditions[:3])}  # Top success factors
    APPLY proven_strategy()
    MONITOR success_metrics()
"""
        return rule
        
    def _create_efficiency_rule(self, pattern: Dict[str, Any]) -> str:
        """Create efficiency optimization rule"""
        operation = pattern['operation']
        improvement_rate = pattern['improvement_rate']
        baseline = pattern['baseline_duration']
        optimized = pattern['optimized_duration']
        
        return f"""
EFFICIENCY_PATTERN('{operation}'):
    baseline_duration = {baseline}
    target_duration = {optimized}
    improvement_achieved = {improvement_rate:.1%}
    
    WHEN duration > target_duration * 1.2:
        APPLY learned_optimizations()
        EXPECT improvement_rate >= {improvement_rate * 0.8:.1%}
"""
        
    def _calculate_pattern_confidence(self, pattern: Dict[str, Any]) -> float:
        """Calculate confidence score for a pattern"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on sample size
        if 'sample_count' in pattern:
            sample_bonus = min(0.3, pattern['sample_count'] / 50)
            confidence += sample_bonus
            
        # Increase confidence based on effect size
        if 'improvement_rate' in pattern:
            effect_bonus = min(0.2, pattern['improvement_rate'])
            confidence += effect_bonus
            
        # Specific adjustments per pattern type
        if pattern.get('type') == 'high_accuracy_operation':
            confidence += pattern.get('accuracy', 0) * 0.2
            
        return min(1.0, confidence)
        
    def _derive_mathematical_formulas(self, data: List[Dict[str, Any]]) -> List[WisdomFormula]:
        """Derive mathematical formulas from numeric patterns"""
        formulas = []
        
        # Extract numeric relationships
        numeric_data = []
        for item in data:
            numeric_item = {}
            for key, value in item.items():
                if isinstance(value, (int, float)):
                    numeric_item[key] = value
            if len(numeric_item) >= 2:  # Need at least 2 variables
                numeric_data.append(numeric_item)
                
        if len(numeric_data) >= 5:  # Need sufficient data points
            # Find correlations
            correlations = self._find_correlations(numeric_data)
            
            for (var1, var2), correlation in correlations.items():
                if abs(correlation) > 0.7:  # Strong correlation
                    formula = self._create_correlation_formula(var1, var2, correlation, numeric_data)
                    if formula:
                        formulas.append(formula)
                        
        return formulas
        
    def _find_correlations(self, data: List[Dict[str, float]]) -> Dict[Tuple[str, str], float]:
        """Find correlations between numeric variables"""
        correlations = {}
        
        # Get all variable names
        all_vars = set()
        for item in data:
            all_vars.update(item.keys())
            
        all_vars = list(all_vars)
        
        # Calculate correlations for each pair
        for i, var1 in enumerate(all_vars):
            for var2 in all_vars[i+1:]:
                values1 = [item.get(var1) for item in data if var1 in item and var2 in item]
                values2 = [item.get(var2) for item in data if var1 in item and var2 in item]
                
                if len(values1) >= 3 and all(v is not None for v in values1 + values2):
                    correlation = self._calculate_correlation(values1, values2)
                    correlations[(var1, var2)] = correlation
                    
        return correlations
        
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
            
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
        
        if denominator == 0:
            return 0.0
            
        return numerator / denominator
        
    def _create_correlation_formula(self, var1: str, var2: str, correlation: float, 
                                  data: List[Dict[str, float]]) -> Optional[WisdomFormula]:
        """Create mathematical formula from correlation"""
        # Extract paired values
        pairs = [(item[var1], item[var2]) for item in data if var1 in item and var2 in item]
        
        if len(pairs) < 3:
            return None
            
        x_values = [p[0] for p in pairs]
        y_values = [p[1] for p in pairs]
        
        # Simple linear regression: y = mx + b
        n = len(pairs)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in pairs)
        sum_x2 = sum(x * x for x in x_values)
        
        # Calculate slope and intercept
        if n * sum_x2 - sum_x * sum_x == 0:
            return None
            
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Calculate accuracy (R-squared)
        mean_y = sum_y / n
        ss_tot = sum((y - mean_y) ** 2 for y in y_values)
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in pairs)
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        formula = WisdomFormula(
            formula_id=f"correlation_{var1}_{var2}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            variables=[var1, var2],
            equation=f"{var2} = {slope:.3f} * {var1} + {intercept:.3f}",
            accuracy=r_squared,
            domain=f"{var1}_to_{var2}_prediction",
            examples=[{var1: x, var2: y, 'predicted': slope * x + intercept} for x, y in pairs[:3]]
        )
        
        return formula
        
    def _compile_to_bytecode(self, crystals: List[CrystalizedKnowledge]) -> Dict[str, str]:
        """Compile high-value crystals into executable bytecode"""
        bytecode_entries = {}
        
        for crystal in crystals:
            if crystal.confidence_score > 0.7 and crystal.compression_ratio > 2.0:
                # High-value crystal worth compiling
                bytecode = self._generate_bytecode(crystal)
                bytecode_entries[crystal.knowledge_id] = bytecode
                
        return bytecode_entries
        
    def _generate_bytecode(self, crystal: CrystalizedKnowledge) -> str:
        """Generate executable bytecode from crystallized knowledge"""
        bytecode_template = f"""
# WISDOM_BYTECODE: {crystal.knowledge_id}
# Confidence: {crystal.confidence_score:.2f}
# Compression: {crystal.compression_ratio:.1f}x

INIT wisdom_{crystal.knowledge_id.split('_')[0]}():
    LOAD crystallized_form("{crystal.crystallized_form}")
    SET confidence({crystal.confidence_score})
    REGISTER usage_pattern()
    
EXECUTE:
    {crystal.crystallized_form}
    INCREMENT usage_frequency()
    LOG wisdom_application("{crystal.knowledge_id}")
    
RETURN optimization_result()
"""
        return bytecode_template
        
    def apply_crystallized_wisdom(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply relevant crystallized wisdom to a context"""
        applicable_crystals = []
        
        # Find crystals that match the context
        for crystal in self.crystallized_knowledge:
            if self._crystal_matches_context(crystal, context):
                applicable_crystals.append(crystal)
                
        # Sort by confidence and usage frequency
        applicable_crystals.sort(key=lambda x: (x.confidence_score, x.usage_frequency), reverse=True)
        
        results = {
            'applied_wisdom': [],
            'recommendations': [],
            'predicted_outcomes': []
        }
        
        # Apply top crystals
        for crystal in applicable_crystals[:3]:  # Top 3
            crystal.usage_frequency += 1
            results['applied_wisdom'].append({
                'crystal_id': crystal.knowledge_id,
                'confidence': crystal.confidence_score,
                'wisdom': crystal.crystallized_form
            })
            
        return results
        
    def _crystal_matches_context(self, crystal: CrystalizedKnowledge, context: Dict[str, Any]) -> bool:
        """Check if crystal is applicable to context"""
        # Simple matching - can be enhanced
        crystal_text = crystal.crystallized_form.lower()
        
        for key, value in context.items():
            if key.lower() in crystal_text or str(value).lower() in crystal_text:
                return True
                
        return False
        
    def generate_crystallization_report(self) -> str:
        """Generate comprehensive crystallization report"""
        report = f"""# Knowledge Crystallization Report
Generated: {datetime.now().isoformat()}

## Crystallization Summary
- **Total Crystals**: {len(self.crystallized_knowledge)}
- **Mathematical Formulas**: {len(self.wisdom_formulas)}
- **Bytecode Entries**: {len(self.bytecode_library)}

## Crystal Quality Distribution
"""
        
        # Analyze crystal quality
        high_confidence = len([c for c in self.crystallized_knowledge if c.confidence_score > 0.8])
        high_compression = len([c for c in self.crystallized_knowledge if c.compression_ratio > 3.0])
        frequently_used = len([c for c in self.crystallized_knowledge if c.usage_frequency > 5])
        
        report += f"- High Confidence (>80%): {high_confidence}\n"
        report += f"- High Compression (>3x): {high_compression}\n"
        report += f"- Frequently Used (>5 times): {frequently_used}\n"
        
        # Top crystals
        report += "\n## Top Crystallized Knowledge\n"
        top_crystals = sorted(self.crystallized_knowledge, 
                            key=lambda x: x.confidence_score * x.compression_ratio, 
                            reverse=True)[:5]
        
        for crystal in top_crystals:
            report += f"- **{crystal.knowledge_id}**\n"
            report += f"  - Confidence: {crystal.confidence_score:.1%}\n"
            report += f"  - Compression: {crystal.compression_ratio:.1f}x\n"
            report += f"  - Usage: {crystal.usage_frequency} times\n"
            
        # Mathematical formulas
        if self.wisdom_formulas:
            report += "\n## Derived Mathematical Formulas\n"
            for formula in self.wisdom_formulas[:3]:
                report += f"- **{formula.domain}**: {formula.equation}\n"
                report += f"  - Accuracy: {formula.accuracy:.1%}\n"
                
        return report

def main():
    """Test knowledge crystallization engine"""
    engine = KnowledgeCrystallizationEngine()
    
    print("[CRYSTALLIZATION] ===== KNOWLEDGE CRYSTALLIZATION ENGINE =====")
    
    # Get experience data from performance profiler
    engine.profiler.load_existing_data()
    experience_data = [asdict(metric) for metric in engine.profiler.metrics]
    
    # Add some synthetic experience data for testing
    synthetic_data = [
        {'operation': 'file_search', 'duration_ms': 150, 'accuracy_score': 0.9, 'outcome': 'success', 'context': {'pattern': '*.py'}, 'timestamp': '2024-01-01T10:00:00'},
        {'operation': 'file_search', 'duration_ms': 200, 'accuracy_score': 0.8, 'outcome': 'success', 'context': {'pattern': '*.json'}, 'timestamp': '2024-01-01T10:01:00'},
        {'operation': 'path_resolution', 'duration_ms': 50, 'accuracy_score': 1.0, 'outcome': 'success', 'context': {'file': 'test.py'}, 'timestamp': '2024-01-01T10:02:00'},
        {'operation': 'pattern_analysis', 'duration_ms': 300, 'accuracy_score': 0.7, 'outcome': 'error', 'context': {'complexity': 8}, 'timestamp': '2024-01-01T10:03:00'},
    ]
    
    experience_data.extend(synthetic_data)
    
    # Crystallize the experience
    new_crystals = engine.crystallize_experience(experience_data)
    
    # Test applying wisdom
    test_context = {'operation': 'file_search', 'pattern': '*.py'}
    wisdom_results = engine.apply_crystallized_wisdom(test_context)
    
    # Generate report
    report = engine.generate_crystallization_report()
    
    # Save everything
    engine.save_crystallized_knowledge()
    
    report_path = engine.project_root / 'knowledge_crystallization_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"[CRYSTALLIZATION] Crystallization report saved to: {report_path}")
    print(f"[CRYSTALLIZATION] New crystals created: {len(new_crystals)}")
    print(f"[CRYSTALLIZATION] Wisdom formulas derived: {len(engine.wisdom_formulas)}")
    print(f"[CRYSTALLIZATION] Bytecode entries compiled: {len(engine.bytecode_library)}")
    
    # Show wisdom application results
    if wisdom_results['applied_wisdom']:
        print(f"[CRYSTALLIZATION] Applied {len(wisdom_results['applied_wisdom'])} wisdom entries to test context")
        
    return engine

if __name__ == "__main__":
    main()