#!/usr/bin/env python3
"""
Failure-Driven Evolution System v1.0 - Learn exponentially from mistakes
Creates immune system for known failure modes and builds failure prediction models
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import re

# Import our other systems for integration
from cognitive_performance_profiler import CognitivePerformanceProfiler
from knowledge_crystallization_engine import KnowledgeCrystallizationEngine

@dataclass
class FailureSignature:
    """Unique signature of a failure mode"""
    signature_id: str
    error_pattern: str
    context_fingerprint: str
    frequency: int
    severity: float
    first_seen: str
    last_seen: str
    evolution_stage: str  # discovered, analyzed, immunized, predicted

@dataclass
class ImmunityResponse:
    """Immune response to prevent known failures"""
    response_id: str
    failure_signature: str
    prevention_strategy: str
    success_rate: float
    activation_count: int
    effectiveness_score: float
    created: str

@dataclass
class FailurePrediction:
    """Prediction of potential failure before it occurs"""
    prediction_id: str
    risk_score: float
    predicted_failure_type: str
    risk_factors: List[str]
    prevention_recommendations: List[str]
    confidence: float
    timestamp: str

class FailureDrivenEvolution:
    """Learns from failures to create immune responses and prediction models"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.failures_db = self.project_root / 'claude' / 'brain_systems' / 'failures_database.json'
        self.immunity_db = self.project_root / 'claude' / 'brain_systems' / 'immunity_responses.json'
        self.predictions_db = self.project_root / 'claude' / 'brain_systems' / 'failure_predictions.json'
        
        # Connect to other systems
        self.profiler = CognitivePerformanceProfiler(project_root)
        self.crystallizer = KnowledgeCrystallizationEngine(project_root)
        
        # Failure tracking
        self.failure_signatures: Dict[str, FailureSignature] = {}
        self.immunity_responses: Dict[str, ImmunityResponse] = {}
        self.failure_history = deque(maxlen=10000)
        self.prediction_models = {}
        
        # Evolution parameters
        self.immunity_threshold = 3  # Failures needed to create immunity
        self.prediction_confidence_threshold = 0.7
        self.severity_weights = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        
        self.load_failure_data()
        
    def load_failure_data(self):
        """Load existing failure evolution data"""
        if self.failures_db.exists():
            with open(self.failures_db, 'r') as f:
                data = json.load(f)
                signatures_data = data.get('signatures', {})
                self.failure_signatures = {
                    k: FailureSignature(**v) for k, v in signatures_data.items()
                }
                
        if self.immunity_db.exists():
            with open(self.immunity_db, 'r') as f:
                data = json.load(f)
                responses_data = data.get('responses', {})
                self.immunity_responses = {
                    k: ImmunityResponse(**v) for k, v in responses_data.items()
                }
                
    def save_failure_data(self):
        """Save failure evolution data"""
        # Save failure signatures
        signatures_data = {
            'timestamp': datetime.now().isoformat(),
            'signatures': {k: asdict(v) for k, v in self.failure_signatures.items()},
            'total_signatures': len(self.failure_signatures)
        }
        
        self.failures_db.parent.mkdir(parents=True, exist_ok=True)
        with open(self.failures_db, 'w') as f:
            json.dump(signatures_data, f, indent=2)
            
        # Save immunity responses
        immunity_data = {
            'timestamp': datetime.now().isoformat(),
            'responses': {k: asdict(v) for k, v in self.immunity_responses.items()},
            'total_responses': len(self.immunity_responses)
        }
        
        with open(self.immunity_db, 'w') as f:
            json.dump(immunity_data, f, indent=2)
            
    def analyze_failure(self, error_info: Dict[str, Any]) -> FailureSignature:
        """Analyze a failure and create/update its signature"""
        # Extract failure patterns
        error_pattern = self._extract_error_pattern(error_info)
        context_fingerprint = self._create_context_fingerprint(error_info)
        
        # Create signature ID
        signature_content = f"{error_pattern}:{context_fingerprint}"
        signature_id = hashlib.md5(signature_content.encode()).hexdigest()[:12]
        
        # Update or create signature
        if signature_id in self.failure_signatures:
            signature = self.failure_signatures[signature_id]
            signature.frequency += 1
            signature.last_seen = datetime.now().isoformat()
            
            # Evolve the signature stage
            if signature.frequency >= self.immunity_threshold and signature.evolution_stage == 'discovered':
                signature.evolution_stage = 'analyzed'
                self._create_immunity_response(signature)
                
        else:
            signature = FailureSignature(
                signature_id=signature_id,
                error_pattern=error_pattern,
                context_fingerprint=context_fingerprint,
                frequency=1,
                severity=self._calculate_failure_severity(error_info),
                first_seen=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat(),
                evolution_stage='discovered'
            )
            self.failure_signatures[signature_id] = signature
            
        # Record in history
        self.failure_history.append({
            'timestamp': datetime.now().isoformat(),
            'signature_id': signature_id,
            'error_info': error_info,
            'evolution_stage': signature.evolution_stage
        })
        
        print(f"[FAILURE_EVOLUTION] Analyzed failure: {signature_id} (freq: {signature.frequency}, stage: {signature.evolution_stage})")
        
        return signature
        
    def _extract_error_pattern(self, error_info: Dict[str, Any]) -> str:
        """Extract the core error pattern from error information"""
        error_msg = error_info.get('error_message', '')
        error_type = error_info.get('error_type', '')
        operation = error_info.get('operation', '')
        
        # Normalize error patterns
        if 'FileNotFoundError' in error_type or 'file not found' in error_msg.lower():
            return 'FILE_NOT_FOUND'
        elif 'PermissionError' in error_type or 'permission denied' in error_msg.lower():
            return 'PERMISSION_DENIED'
        elif 'UnicodeError' in error_type or 'encoding' in error_msg.lower():
            return 'ENCODING_ERROR'
        elif 'ModuleNotFoundError' in error_type or 'module' in error_msg.lower():
            return 'MISSING_DEPENDENCY'
        elif 'timeout' in error_msg.lower():
            return 'TIMEOUT_ERROR'
        elif 'connection' in error_msg.lower():
            return 'CONNECTION_ERROR'
        elif operation:
            return f'OPERATION_FAILURE:{operation}'
        else:
            # Extract key words from error message
            key_words = re.findall(r'\\b[A-Z][a-z]*Error\\b|\\b[a-z]+(?:Error|Exception)\\b', error_msg)
            if key_words:
                return f'PATTERN:{key_words[0]}'
            else:
                return 'UNKNOWN_ERROR'
                
    def _create_context_fingerprint(self, error_info: Dict[str, Any]) -> str:
        """Create a fingerprint of the error context"""
        context = error_info.get('context', {})
        
        # Extract key context elements
        fingerprint_elements = []
        
        # File-related context
        if 'file_path' in context:
            file_ext = Path(context['file_path']).suffix
            fingerprint_elements.append(f'ext:{file_ext}')
            
        # Operation context
        if 'operation' in context:
            fingerprint_elements.append(f'op:{context["operation"]}')
            
        # Tool context
        if 'tool' in context:
            fingerprint_elements.append(f'tool:{context["tool"]}')
            
        # Parameter context
        for key, value in context.items():
            if isinstance(value, str) and len(value) < 20:
                fingerprint_elements.append(f'{key}:{value}')
                
        # Create hash of fingerprint
        fingerprint_str = '|'.join(sorted(fingerprint_elements))
        return hashlib.md5(fingerprint_str.encode()).hexdigest()[:8]
        
    def _calculate_failure_severity(self, error_info: Dict[str, Any]) -> float:
        """Calculate the severity of a failure"""
        severity = 0.5  # Base severity
        
        # Increase severity based on error characteristics
        error_msg = error_info.get('error_message', '').lower()
        
        if any(term in error_msg for term in ['critical', 'fatal', 'corrupt']):
            severity += 0.4
        elif any(term in error_msg for term in ['warning', 'deprecated']):
            severity -= 0.2
            
        # Severity based on operation impact
        operation = error_info.get('operation', '')
        if operation in ['file_write', 'system_change', 'data_loss']:
            severity += 0.3
        elif operation in ['file_read', 'query', 'display']:
            severity += 0.1
            
        # Context-based severity
        context = error_info.get('context', {})
        if context.get('critical_path', False):
            severity += 0.2
            
        return min(1.0, severity)
        
    def _create_immunity_response(self, signature: FailureSignature):
        """Create an immune response for a recurring failure"""
        response_id = f"immunity_{signature.signature_id}"
        
        # Generate prevention strategy based on error pattern
        prevention_strategy = self._generate_prevention_strategy(signature)
        
        immunity = ImmunityResponse(
            response_id=response_id,
            failure_signature=signature.signature_id,
            prevention_strategy=prevention_strategy,
            success_rate=0.0,  # Will be updated based on effectiveness
            activation_count=0,
            effectiveness_score=0.0,
            created=datetime.now().isoformat()
        )
        
        self.immunity_responses[response_id] = immunity
        signature.evolution_stage = 'immunized'
        
        print(f"[FAILURE_EVOLUTION] Created immunity response: {response_id}")
        
    def _generate_prevention_strategy(self, signature: FailureSignature) -> str:
        """Generate prevention strategy for a failure pattern"""
        error_pattern = signature.error_pattern
        
        strategies = {
            'FILE_NOT_FOUND': """
BEFORE file_operation(path):
    VALIDATE file_exists(path)
    IF not exists: SUGGEST alternative_path() OR CREATE_FILE()
    LOG file_access_attempt(path)
""",
            'PERMISSION_DENIED': """
BEFORE file_operation(path):
    CHECK file_permissions(path)
    IF insufficient: REQUEST elevated_access() OR SUGGEST alternative()
    ENABLE permission_escalation_if_safe()
""",
            'ENCODING_ERROR': """
BEFORE text_operation(file):
    DETECT file_encoding(file)
    SET encoding='utf-8' OR detected_encoding
    ENABLE unicode_error_handling()
""",
            'MISSING_DEPENDENCY': """
BEFORE import_operation(module):
    CHECK module_availability(module)
    IF missing: SUGGEST installation() OR PROVIDE fallback()
    ENABLE graceful_degradation()
""",
            'TIMEOUT_ERROR': """
BEFORE long_operation():
    SET timeout_strategy(progressive_backoff)
    ENABLE operation_cancellation()
    PROVIDE progress_feedback()
""",
        }
        
        base_strategy = strategies.get(error_pattern, """
BEFORE operation():
    VALIDATE preconditions()
    ENABLE error_recovery()
    LOG operation_attempt()
""")
        
        return base_strategy
        
    def activate_immunity(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Activate immune responses for the given context"""
        activated_responses = []
        
        # Check all immunity responses
        for response_id, immunity in self.immunity_responses.items():
            if self._immunity_applies_to_context(immunity, context):
                # Activate the immunity
                immunity.activation_count += 1
                
                activated_responses.append({
                    'response_id': response_id,
                    'prevention_strategy': immunity.prevention_strategy,
                    'success_rate': immunity.success_rate,
                    'signature': immunity.failure_signature
                })
                
                print(f"[FAILURE_EVOLUTION] Activated immunity: {response_id}")
                
        if activated_responses:
            return {
                'immunity_activated': True,
                'responses': activated_responses,
                'prevention_recommendations': [r['prevention_strategy'] for r in activated_responses]
            }
            
        return None
        
    def _immunity_applies_to_context(self, immunity: ImmunityResponse, context: Dict[str, Any]) -> bool:
        """Check if immunity response applies to the current context"""
        # Get the failure signature
        signature = self.failure_signatures.get(immunity.failure_signature)
        if not signature:
            return False
            
        # Check if context matches the failure pattern
        context_fingerprint = self._create_context_fingerprint({'context': context})
        
        # Simple matching - can be enhanced
        return (signature.context_fingerprint in context_fingerprint or 
                context_fingerprint in signature.context_fingerprint)
                
    def predict_failure_risk(self, context: Dict[str, Any]) -> FailurePrediction:
        """Predict the risk of failure for a given context"""
        risk_factors = []
        risk_score = 0.0
        predicted_failure_types = []
        
        # Analyze context against known failure patterns
        for signature_id, signature in self.failure_signatures.items():
            context_similarity = self._calculate_context_similarity(signature, context)
            
            if context_similarity > 0.3:  # Significant similarity
                risk_contribution = context_similarity * signature.severity * (signature.frequency / 10.0)
                risk_score += risk_contribution
                
                risk_factors.append(f"{signature.error_pattern} (similarity: {context_similarity:.1%})")
                predicted_failure_types.append(signature.error_pattern)
                
        # Normalize risk score
        risk_score = min(1.0, risk_score)
        
        # Generate prevention recommendations
        recommendations = self._generate_risk_mitigation_recommendations(predicted_failure_types, context)
        
        prediction = FailurePrediction(
            prediction_id=f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            risk_score=risk_score,
            predicted_failure_type=predicted_failure_types[0] if predicted_failure_types else 'UNKNOWN',
            risk_factors=risk_factors,
            prevention_recommendations=recommendations,
            confidence=self._calculate_prediction_confidence(risk_score, len(risk_factors)),
            timestamp=datetime.now().isoformat()
        )
        
        return prediction
        
    def _calculate_context_similarity(self, signature: FailureSignature, context: Dict[str, Any]) -> float:
        """Calculate similarity between failure signature and current context"""
        # Create fingerprint for current context
        current_fingerprint = self._create_context_fingerprint({'context': context})
        
        # Simple similarity based on fingerprint overlap
        signature_parts = set(signature.context_fingerprint.split('|'))
        current_parts = set(current_fingerprint.split('|'))
        
        if not signature_parts and not current_parts:
            return 0.0
            
        intersection = signature_parts & current_parts
        union = signature_parts | current_parts
        
        jaccard_similarity = len(intersection) / len(union) if union else 0.0
        
        return jaccard_similarity
        
    def _generate_risk_mitigation_recommendations(self, failure_types: List[str], context: Dict[str, Any]) -> List[str]:
        """Generate recommendations to mitigate predicted failure risks"""
        recommendations = []
        
        for failure_type in set(failure_types):  # Unique failure types
            if failure_type == 'FILE_NOT_FOUND':
                recommendations.append("Validate file existence before operations")
            elif failure_type == 'PERMISSION_DENIED':
                recommendations.append("Check file permissions and user access rights")
            elif failure_type == 'ENCODING_ERROR':
                recommendations.append("Specify explicit encoding (UTF-8) for text operations")
            elif failure_type == 'MISSING_DEPENDENCY':
                recommendations.append("Verify all required modules are available")
            elif failure_type == 'TIMEOUT_ERROR':
                recommendations.append("Implement timeout handling and progress monitoring")
            else:
                recommendations.append(f"Apply defensive programming for {failure_type}")
                
        # Context-specific recommendations
        if context.get('file_path'):
            recommendations.append("Use absolute paths and validate file accessibility")
        if context.get('network_operation'):
            recommendations.append("Implement retry logic with exponential backoff")
            
        return recommendations[:5]  # Top 5 recommendations
        
    def _calculate_prediction_confidence(self, risk_score: float, risk_factors_count: int) -> float:
        """Calculate confidence in the failure prediction"""
        base_confidence = 0.5
        
        # Higher confidence with more risk factors
        factors_bonus = min(0.3, risk_factors_count * 0.1)
        
        # Higher confidence with higher risk score
        risk_bonus = risk_score * 0.2
        
        confidence = base_confidence + factors_bonus + risk_bonus
        return min(1.0, confidence)
        
    def evolve_immunity_effectiveness(self, immunity_id: str, was_successful: bool):
        """Update immunity effectiveness based on outcomes"""
        if immunity_id in self.immunity_responses:
            immunity = self.immunity_responses[immunity_id]
            
            # Update success rate
            total_activations = immunity.activation_count
            if total_activations > 0:
                current_successes = immunity.success_rate * (total_activations - 1)
                new_successes = current_successes + (1 if was_successful else 0)
                immunity.success_rate = new_successes / total_activations
                
            # Update effectiveness score
            immunity.effectiveness_score = immunity.success_rate * min(1.0, total_activations / 10.0)
            
            print(f"[FAILURE_EVOLUTION] Updated immunity effectiveness: {immunity_id} (success rate: {immunity.success_rate:.1%})")
            
    def generate_evolution_report(self) -> str:
        """Generate comprehensive failure evolution report"""
        report = f"""# Failure-Driven Evolution Report
Generated: {datetime.now().isoformat()}

## Evolution Summary
- **Failure Signatures**: {len(self.failure_signatures)}
- **Immunity Responses**: {len(self.immunity_responses)}
- **Evolution Stages**: {self._count_evolution_stages()}

## Failure Pattern Analysis
"""
        
        # Most frequent failures
        frequent_failures = sorted(
            self.failure_signatures.values(), 
            key=lambda x: x.frequency, 
            reverse=True
        )[:5]
        
        report += "### Most Frequent Failures\n"
        for signature in frequent_failures:
            report += f"- **{signature.error_pattern}** (ID: {signature.signature_id})\n"
            report += f"  - Frequency: {signature.frequency}\n"
            report += f"  - Severity: {signature.severity:.1%}\n"
            report += f"  - Stage: {signature.evolution_stage}\n"
            
        # Immunity effectiveness
        report += "\n## Immunity System Performance\n"
        effective_immunities = [
            r for r in self.immunity_responses.values() 
            if r.activation_count > 0
        ]
        
        if effective_immunities:
            avg_success_rate = sum(r.success_rate for r in effective_immunities) / len(effective_immunities)
            report += f"- **Average Success Rate**: {avg_success_rate:.1%}\n"
            
            top_immunities = sorted(effective_immunities, key=lambda x: x.effectiveness_score, reverse=True)[:3]
            report += "\n### Top Performing Immunities\n"
            for immunity in top_immunities:
                report += f"- **{immunity.response_id}**\n"
                report += f"  - Success Rate: {immunity.success_rate:.1%}\n"
                report += f"  - Activations: {immunity.activation_count}\n"
                report += f"  - Effectiveness: {immunity.effectiveness_score:.2f}\n"
        else:
            report += "- No immunity responses have been activated yet\n"
            
        # Evolution stages distribution
        stages = self._count_evolution_stages()
        report += "\n## Evolution Stages Distribution\n"
        for stage, count in stages.items():
            report += f"- **{stage.title()}**: {count}\n"
            
        return report
        
    def _count_evolution_stages(self) -> Dict[str, int]:
        """Count failure signatures by evolution stage"""
        stages = defaultdict(int)
        for signature in self.failure_signatures.values():
            stages[signature.evolution_stage] += 1
        return dict(stages)

def main():
    """Test failure-driven evolution system"""
    evolution = FailureDrivenEvolution()
    
    print("[FAILURE_EVOLUTION] ===== FAILURE-DRIVEN EVOLUTION SYSTEM =====")
    
    # Simulate some failures for testing
    test_failures = [
        {
            'error_message': 'FileNotFoundError: No such file or directory: cognitive_cache.cc',
            'error_type': 'FileNotFoundError',
            'operation': 'file_read',
            'context': {'file_path': 'cognitive_cache.cc', 'tool': 'read'}
        },
        {
            'error_message': 'FileNotFoundError: No such file or directory: cognitive_core.json',
            'error_type': 'FileNotFoundError', 
            'operation': 'file_read',
            'context': {'file_path': 'cognitive_core.json', 'tool': 'read'}
        },
        {
            'error_message': 'ModuleNotFoundError: No module named psutil',
            'error_type': 'ModuleNotFoundError',
            'operation': 'import',
            'context': {'module': 'psutil', 'tool': 'python'}
        },
        {
            'error_message': 'UnicodeEncodeError: charmap codec cant encode character',
            'error_type': 'UnicodeEncodeError',
            'operation': 'file_write',
            'context': {'encoding': 'cp1252', 'tool': 'write'}
        },
        # Repeat some to trigger immunity
        {
            'error_message': 'FileNotFoundError: No such file or directory: another_file.py',
            'error_type': 'FileNotFoundError',
            'operation': 'file_read', 
            'context': {'file_path': 'another_file.py', 'tool': 'read'}
        }
    ]
    
    # Process failures
    for failure in test_failures:
        signature = evolution.analyze_failure(failure)
        
    # Test immunity activation
    test_context = {'file_path': 'test_file.py', 'tool': 'read', 'operation': 'file_read'}
    immunity_result = evolution.activate_immunity(test_context)
    
    if immunity_result:
        print(f"[FAILURE_EVOLUTION] Immunity activated: {len(immunity_result['responses'])} responses")
        
    # Test failure prediction
    prediction = evolution.predict_failure_risk(test_context)
    print(f"[FAILURE_EVOLUTION] Failure risk prediction: {prediction.risk_score:.1%} (confidence: {prediction.confidence:.1%})")
    
    # Update immunity effectiveness (simulate)
    for immunity_id in evolution.immunity_responses:
        evolution.evolve_immunity_effectiveness(immunity_id, True)  # Simulate success
        
    # Generate report
    report = evolution.generate_evolution_report()
    
    # Save all data
    evolution.save_failure_data()
    
    report_path = evolution.project_root / 'failure_evolution_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"[FAILURE_EVOLUTION] Evolution report saved to: {report_path}")
    print(f"[FAILURE_EVOLUTION] Failure signatures: {len(evolution.failure_signatures)}")
    print(f"[FAILURE_EVOLUTION] Immunity responses: {len(evolution.immunity_responses)}")
    
    return evolution

if __name__ == "__main__":
    main()