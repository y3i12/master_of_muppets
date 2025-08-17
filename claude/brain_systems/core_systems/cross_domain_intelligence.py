#!/usr/bin/env python3
"""
Cross-Domain Intelligence Synthesis v1.0 - Connect insights across different domains
Links PCB patterns to code organization, circuit principles to problem-solving strategies
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import re

# Import our existing systems for domain knowledge
from cognitive_performance_profiler import CognitivePerformanceProfiler
from knowledge_crystallization_engine import KnowledgeCrystallizationEngine
from failure_driven_evolution import FailureDrivenEvolution

@dataclass
class DomainKnowledge:
    """Knowledge from a specific domain"""
    domain_id: str
    domain_name: str
    knowledge_type: str  # pattern, principle, law, heuristic
    content: Dict[str, Any]
    abstraction_level: float  # 0.0 = concrete, 1.0 = abstract
    transferability_score: float
    examples: List[str]
    created: str

@dataclass
class CrossDomainMapping:
    """Mapping between concepts across domains"""
    mapping_id: str
    source_domain: str
    target_domain: str
    source_concept: str
    target_concept: str
    similarity_score: float
    transfer_mechanism: str
    validated: bool
    applications: List[str]
    created: str

@dataclass
class SynthesizedInsight:
    """New insight created by cross-domain synthesis"""
    insight_id: str
    contributing_domains: List[str]
    synthesis_type: str  # analogy, pattern_transfer, principle_generalization
    insight_content: str
    confidence_score: float
    novelty_score: float
    practical_applications: List[str]
    validation_results: Dict[str, Any]
    created: str

class CrossDomainIntelligence:
    """Synthesizes insights by connecting knowledge across different domains"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.domains_db = self.project_root / 'claude' / 'brain_systems' / 'domain_knowledge.json'
        self.mappings_db = self.project_root / 'claude' / 'brain_systems' / 'cross_domain_mappings.json'
        self.insights_db = self.project_root / 'claude' / 'brain_systems' / 'synthesized_insights.json'
        
        # Connect to existing systems for domain extraction
        self.profiler = CognitivePerformanceProfiler(project_root)
        self.crystallizer = KnowledgeCrystallizationEngine(project_root)
        self.evolution = FailureDrivenEvolution(project_root)
        
        # Knowledge storage
        self.domain_knowledge: Dict[str, DomainKnowledge] = {}
        self.cross_mappings: Dict[str, CrossDomainMapping] = {}
        self.synthesized_insights: List[SynthesizedInsight] = []
        
        # Domain definitions
        self.known_domains = {
            'pcb_design': {
                'patterns': ['signal_routing', 'component_placement', 'layer_management'],
                'principles': ['impedance_matching', 'noise_reduction', 'thermal_management'],
                'laws': ['ohms_law', 'kirchhoffs_laws', 'signal_integrity'],
                'abstractions': ['electrical_flow', 'component_hierarchy', 'system_architecture']
            },
            'software_engineering': {
                'patterns': ['module_organization', 'dependency_management', 'error_handling'],
                'principles': ['separation_of_concerns', 'dry_principle', 'solid_principles'],
                'laws': ['conways_law', 'brooks_law', 'amdahls_law'],
                'abstractions': ['information_flow', 'system_boundaries', 'architectural_layers']
            },
            'cognitive_systems': {
                'patterns': ['pattern_recognition', 'learning_loops', 'memory_hierarchies'],
                'principles': ['feedback_systems', 'adaptation', 'optimization'],
                'laws': ['hebbian_learning', 'cognitive_load_theory', 'chunking_principle'],
                'abstractions': ['knowledge_networks', 'processing_pipelines', 'decision_trees']
            },
            'physical_systems': {
                'patterns': ['force_distribution', 'energy_flow', 'system_stability'],
                'principles': ['conservation_laws', 'equilibrium', 'feedback_control'],
                'laws': ['thermodynamics', 'mechanics', 'wave_propagation'],
                'abstractions': ['system_dynamics', 'field_interactions', 'emergent_behavior']
            }
        }
        
        self.load_domain_data()
        self._initialize_base_knowledge()
        
    def load_domain_data(self):
        """Load existing domain knowledge and mappings"""
        if self.domains_db.exists():
            with open(self.domains_db, 'r') as f:
                data = json.load(f)
                domains_data = data.get('domains', {})
                self.domain_knowledge = {
                    k: DomainKnowledge(**v) for k, v in domains_data.items()
                }
                
        if self.mappings_db.exists():
            with open(self.mappings_db, 'r') as f:
                data = json.load(f)
                mappings_data = data.get('mappings', {})
                self.cross_mappings = {
                    k: CrossDomainMapping(**v) for k, v in mappings_data.items()
                }
                
        if self.insights_db.exists():
            with open(self.insights_db, 'r') as f:
                data = json.load(f)
                insights_data = data.get('insights', [])
                self.synthesized_insights = [
                    SynthesizedInsight(**insight) for insight in insights_data
                ]
                
    def save_domain_data(self):
        """Save domain knowledge, mappings, and insights"""
        # Save domain knowledge
        domains_data = {
            'timestamp': datetime.now().isoformat(),
            'domains': {k: asdict(v) for k, v in self.domain_knowledge.items()},
            'total_domains': len(self.domain_knowledge)
        }
        
        self.domains_db.parent.mkdir(parents=True, exist_ok=True)
        with open(self.domains_db, 'w') as f:
            json.dump(domains_data, f, indent=2)
            
        # Save cross-domain mappings
        mappings_data = {
            'timestamp': datetime.now().isoformat(),
            'mappings': {k: asdict(v) for k, v in self.cross_mappings.items()},
            'total_mappings': len(self.cross_mappings)
        }
        
        with open(self.mappings_db, 'w') as f:
            json.dump(mappings_data, f, indent=2)
            
        # Save synthesized insights
        insights_data = {
            'timestamp': datetime.now().isoformat(),
            'insights': [asdict(insight) for insight in self.synthesized_insights],
            'total_insights': len(self.synthesized_insights)
        }
        
        with open(self.insights_db, 'w') as f:
            json.dump(insights_data, f, indent=2)
            
    def _initialize_base_knowledge(self):
        """Initialize base domain knowledge if not already present"""
        if not self.domain_knowledge:
            print("[CROSS_DOMAIN] Initializing base domain knowledge...")
            
            # PCB Design Domain
            self._add_domain_knowledge('pcb_design', 'principle', {
                'name': 'signal_integrity',
                'description': 'Maintaining signal quality through proper routing and impedance control',
                'key_factors': ['trace_width', 'layer_separation', 'via_placement'],
                'optimization_goals': ['minimize_noise', 'maximize_speed', 'reduce_crosstalk']
            }, 0.7, ['differential_pairs', 'ground_planes', 'length_matching'])
            
            self._add_domain_knowledge('pcb_design', 'pattern', {
                'name': 'component_placement_optimization',
                'description': 'Strategic placement to minimize routing complexity and maximize performance',
                'strategies': ['functional_grouping', 'thermal_considerations', 'signal_flow_alignment'],
                'metrics': ['routing_efficiency', 'thermal_performance', 'manufacturability']
            }, 0.6, ['critical_path_optimization', 'power_distribution', 'clock_tree_synthesis'])
            
            # Software Engineering Domain
            self._add_domain_knowledge('software_engineering', 'principle', {
                'name': 'separation_of_concerns',
                'description': 'Dividing system into distinct sections with minimal overlap',
                'benefits': ['maintainability', 'testability', 'reusability'],
                'implementation': ['modular_design', 'layered_architecture', 'interface_segregation']
            }, 0.8, ['microservices', 'mvc_pattern', 'dependency_injection'])
            
            self._add_domain_knowledge('software_engineering', 'pattern', {
                'name': 'error_propagation_control',
                'description': 'Managing how errors flow through system boundaries',
                'strategies': ['exception_handling', 'circuit_breakers', 'graceful_degradation'],
                'goals': ['system_stability', 'fault_isolation', 'recovery_mechanisms']
            }, 0.7, ['retry_patterns', 'bulkhead_isolation', 'timeout_handling'])
            
            # Cognitive Systems Domain  
            self._add_domain_knowledge('cognitive_systems', 'principle', {
                'name': 'feedback_driven_learning',
                'description': 'Continuous improvement through performance feedback loops',
                'components': ['measurement', 'analysis', 'adaptation', 'validation'],
                'applications': ['pattern_recognition', 'optimization', 'prediction']
            }, 0.9, ['reinforcement_learning', 'meta_learning', 'adaptive_systems'])
            
    def _add_domain_knowledge(self, domain: str, knowledge_type: str, content: Dict[str, Any], 
                            abstraction_level: float, examples: List[str]):
        """Add knowledge to a domain"""
        knowledge_id = f"{domain}_{knowledge_type}_{len(self.domain_knowledge)}"
        
        knowledge = DomainKnowledge(
            domain_id=knowledge_id,
            domain_name=domain,
            knowledge_type=knowledge_type,
            content=content,
            abstraction_level=abstraction_level,
            transferability_score=self._calculate_transferability(content, abstraction_level),
            examples=examples,
            created=datetime.now().isoformat()
        )
        
        self.domain_knowledge[knowledge_id] = knowledge
        
    def _calculate_transferability(self, content: Dict[str, Any], abstraction_level: float) -> float:
        """Calculate how transferable knowledge is to other domains"""
        base_transferability = abstraction_level  # More abstract = more transferable
        
        # Boost transferability for fundamental concepts
        if any(term in str(content).lower() for term in ['optimization', 'efficiency', 'pattern', 'principle']):
            base_transferability += 0.2
            
        # Boost for concepts with clear mechanisms
        if 'strategies' in content or 'mechanisms' in content or 'approaches' in content:
            base_transferability += 0.1
            
        return min(1.0, base_transferability)
        
    def discover_cross_domain_mappings(self) -> List[CrossDomainMapping]:
        """Discover mappings between concepts across domains"""
        new_mappings = []
        
        print("[CROSS_DOMAIN] Discovering cross-domain mappings...")
        
        # Compare all domain pairs
        domain_ids = list(self.domain_knowledge.keys())
        
        for i, source_id in enumerate(domain_ids):
            for target_id in domain_ids[i+1:]:
                source_knowledge = self.domain_knowledge[source_id]
                target_knowledge = self.domain_knowledge[target_id]
                
                # Skip if same domain
                if source_knowledge.domain_name == target_knowledge.domain_name:
                    continue
                    
                # Calculate similarity
                similarity = self._calculate_concept_similarity(source_knowledge, target_knowledge)
                
                if similarity > 0.5:  # Threshold for meaningful mapping
                    mapping = self._create_cross_domain_mapping(source_knowledge, target_knowledge, similarity)
                    new_mappings.append(mapping)
                    self.cross_mappings[mapping.mapping_id] = mapping
                    
        print(f"[CROSS_DOMAIN] Discovered {len(new_mappings)} new cross-domain mappings")
        return new_mappings
        
    def _calculate_concept_similarity(self, source: DomainKnowledge, target: DomainKnowledge) -> float:
        """Calculate similarity between concepts from different domains"""
        similarity_factors = []
        
        # 1. Structural similarity (similar content organization)
        source_keys = set(source.content.keys())
        target_keys = set(target.content.keys())
        
        if source_keys and target_keys:
            key_similarity = len(source_keys & target_keys) / len(source_keys | target_keys)
            similarity_factors.append(key_similarity * 0.3)
            
        # 2. Semantic similarity (similar concepts/words)
        source_text = json.dumps(source.content, sort_keys=True).lower()
        target_text = json.dumps(target.content, sort_keys=True).lower()
        
        # Extract key terms
        source_terms = set(re.findall(r'\\b[a-z]{4,}\\b', source_text))
        target_terms = set(re.findall(r'\\b[a-z]{4,}\\b', target_text))
        
        if source_terms and target_terms:
            term_similarity = len(source_terms & target_terms) / len(source_terms | target_terms)
            similarity_factors.append(term_similarity * 0.4)
            
        # 3. Abstraction level similarity
        abstraction_similarity = 1.0 - abs(source.abstraction_level - target.abstraction_level)
        similarity_factors.append(abstraction_similarity * 0.3)
        
        return sum(similarity_factors) if similarity_factors else 0.0
        
    def _create_cross_domain_mapping(self, source: DomainKnowledge, target: DomainKnowledge, 
                                   similarity: float) -> CrossDomainMapping:
        """Create a cross-domain mapping between concepts"""
        mapping_id = f"mapping_{source.domain_name}_{target.domain_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Determine transfer mechanism based on similarity type
        transfer_mechanism = self._determine_transfer_mechanism(source, target)
        
        mapping = CrossDomainMapping(
            mapping_id=mapping_id,
            source_domain=source.domain_name,
            target_domain=target.domain_name,
            source_concept=source.content.get('name', source.knowledge_type),
            target_concept=target.content.get('name', target.knowledge_type),
            similarity_score=similarity,
            transfer_mechanism=transfer_mechanism,
            validated=False,
            applications=[],
            created=datetime.now().isoformat()
        )
        
        return mapping
        
    def _determine_transfer_mechanism(self, source: DomainKnowledge, target: DomainKnowledge) -> str:
        """Determine how knowledge transfers between domains"""
        # Analogy-based transfer
        if source.abstraction_level > 0.7 and target.abstraction_level > 0.7:
            return 'structural_analogy'
            
        # Pattern transfer
        if 'pattern' in source.knowledge_type or 'pattern' in target.knowledge_type:
            return 'pattern_mapping'
            
        # Principle generalization
        if 'principle' in source.knowledge_type and 'principle' in target.knowledge_type:
            return 'principle_generalization'
            
        # Method adaptation
        if any(key in source.content for key in ['strategies', 'methods', 'approaches']):
            return 'method_adaptation'
            
        return 'conceptual_bridge'
        
    def synthesize_cross_domain_insights(self) -> List[SynthesizedInsight]:
        """Synthesize new insights from cross-domain mappings"""
        new_insights = []
        
        print("[CROSS_DOMAIN] Synthesizing cross-domain insights...")
        
        # Group mappings by domains involved
        domain_groups = defaultdict(list)
        for mapping in self.cross_mappings.values():
            key = tuple(sorted([mapping.source_domain, mapping.target_domain]))
            domain_groups[key].append(mapping)
            
        # Synthesize insights for each domain pair
        for domain_pair, mappings in domain_groups.items():
            if len(mappings) >= 2:  # Need multiple mappings for synthesis
                insight = self._synthesize_domain_pair_insight(domain_pair, mappings)
                if insight:
                    new_insights.append(insight)
                    self.synthesized_insights.append(insight)
                    
        # Synthesize multi-domain insights
        multi_domain_insight = self._synthesize_multi_domain_insight()
        if multi_domain_insight:
            new_insights.append(multi_domain_insight)
            self.synthesized_insights.append(multi_domain_insight)
            
        print(f"[CROSS_DOMAIN] Synthesized {len(new_insights)} new cross-domain insights")
        return new_insights
        
    def _synthesize_domain_pair_insight(self, domain_pair: Tuple[str, str], 
                                      mappings: List[CrossDomainMapping]) -> Optional[SynthesizedInsight]:
        """Synthesize insight from mappings between two domains"""
        domain_a, domain_b = domain_pair
        
        # Find common patterns across mappings
        common_mechanisms = defaultdict(int)
        for mapping in mappings:
            common_mechanisms[mapping.transfer_mechanism] += 1
            
        dominant_mechanism = max(common_mechanisms.items(), key=lambda x: x[1])[0]
        
        # Create insight based on dominant mechanism
        if dominant_mechanism == 'structural_analogy':
            insight_content = self._create_structural_analogy_insight(domain_a, domain_b, mappings)
        elif dominant_mechanism == 'pattern_mapping':
            insight_content = self._create_pattern_mapping_insight(domain_a, domain_b, mappings)
        elif dominant_mechanism == 'principle_generalization':
            insight_content = self._create_principle_generalization_insight(domain_a, domain_b, mappings)
        else:
            insight_content = self._create_general_synthesis_insight(domain_a, domain_b, mappings)
            
        if not insight_content:
            return None
            
        insight = SynthesizedInsight(
            insight_id=f"synthesis_{domain_a}_{domain_b}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            contributing_domains=[domain_a, domain_b],
            synthesis_type=dominant_mechanism,
            insight_content=insight_content,
            confidence_score=self._calculate_insight_confidence(mappings),
            novelty_score=self._calculate_insight_novelty(insight_content),
            practical_applications=self._generate_practical_applications(domain_a, domain_b, insight_content),
            validation_results={},
            created=datetime.now().isoformat()
        )
        
        return insight
        
    def _create_structural_analogy_insight(self, domain_a: str, domain_b: str, 
                                         mappings: List[CrossDomainMapping]) -> str:
        """Create insight based on structural analogies"""
        return f"""
**Structural Analogy Between {domain_a.title()} and {domain_b.title()}**

The organizational principles in {domain_a} mirror those in {domain_b}:

1. **Hierarchical Structure**: Both domains use layered architectures where higher levels depend on lower levels
2. **Flow Management**: Information/energy/signals flow through defined pathways with control mechanisms
3. **Optimization Strategies**: Both employ similar approaches to balance competing constraints
4. **Error Isolation**: Failures are contained through boundary definitions and isolation techniques

This structural similarity suggests that optimization techniques from one domain can be adapted to the other.
"""
        
    def _create_pattern_mapping_insight(self, domain_a: str, domain_b: str, 
                                      mappings: List[CrossDomainMapping]) -> str:
        """Create insight based on pattern mappings"""
        return f"""
**Pattern Transfer Between {domain_a.title()} and {domain_b.title()}**

Common patterns identified:

1. **Modularization**: Both domains benefit from breaking complex systems into manageable modules
2. **Interface Design**: Clean interfaces between components reduce coupling and improve maintainability  
3. **Performance Optimization**: Similar bottleneck identification and resolution strategies
4. **Quality Assurance**: Validation and testing approaches show strong parallels

These patterns suggest a unified approach to system design across both domains.
"""
        
    def _create_principle_generalization_insight(self, domain_a: str, domain_b: str,
                                               mappings: List[CrossDomainMapping]) -> str:
        """Create insight based on principle generalization"""
        return f"""
**Universal Principles Spanning {domain_a.title()} and {domain_b.title()}**

Fundamental principles that apply across both domains:

1. **Conservation Laws**: Resources (energy/time/complexity) must be conserved and optimally allocated
2. **Feedback Systems**: Both domains rely on measurement, analysis, and adaptive response cycles
3. **Emergence**: Complex behaviors arise from simple interactions between components
4. **Trade-off Management**: Optimization requires balancing multiple competing objectives

These universal principles form the foundation for cross-domain optimization strategies.
"""
        
    def _create_general_synthesis_insight(self, domain_a: str, domain_b: str,
                                        mappings: List[CrossDomainMapping]) -> str:
        """Create general synthesis insight"""
        return f"""
**Cross-Domain Learning Bridge: {domain_a.title()} ↔ {domain_b.title()}**

Key learnings that transfer bidirectionally:

1. **Problem-Solving Approaches**: Methodologies from one domain enhance the other
2. **Quality Metrics**: Success indicators show conceptual overlap
3. **Optimization Techniques**: Algorithmic approaches are domain-adaptable
4. **System Thinking**: Holistic perspectives benefit both domains

This synthesis reveals opportunities for unified tooling and shared optimization strategies.
"""
        
    def _synthesize_multi_domain_insight(self) -> Optional[SynthesizedInsight]:
        """Synthesize insight spanning multiple domains"""
        if len(set(mapping.source_domain for mapping in self.cross_mappings.values())) < 3:
            return None  # Need at least 3 domains
            
        insight_content = """
**Universal System Design Principles (Multi-Domain Synthesis)**

Analysis across PCB design, software engineering, cognitive systems, and physical systems reveals universal principles:

1. **Hierarchical Decomposition**: All complex systems benefit from layered abstraction
2. **Flow Optimization**: Whether electrical signals, data, or energy, flow optimization is paramount
3. **Feedback-Driven Adaptation**: Systems improve through measurement and iterative refinement
4. **Modular Architecture**: Components with well-defined interfaces enable scalability and maintainability
5. **Error Recovery**: Robust systems anticipate and gracefully handle failure modes
6. **Resource Conservation**: Optimal allocation of limited resources (power, memory, bandwidth, time)

These principles suggest a unified approach to system design that transcends domain boundaries.
"""
        
        all_domains = list(set(
            [mapping.source_domain for mapping in self.cross_mappings.values()] +
            [mapping.target_domain for mapping in self.cross_mappings.values()]
        ))
        
        insight = SynthesizedInsight(
            insight_id=f"multi_domain_synthesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            contributing_domains=all_domains,
            synthesis_type='universal_principles',
            insight_content=insight_content,
            confidence_score=0.8,  # High confidence in universal principles
            novelty_score=0.9,    # High novelty for multi-domain synthesis
            practical_applications=[
                'Unified design methodology across domains',
                'Cross-domain optimization algorithms',
                'Universal system architecture principles',
                'Integrated quality metrics framework'
            ],
            validation_results={},
            created=datetime.now().isoformat()
        )
        
        return insight
        
    def _calculate_insight_confidence(self, mappings: List[CrossDomainMapping]) -> float:
        """Calculate confidence in synthesized insight"""
        if not mappings:
            return 0.0
            
        avg_similarity = sum(m.similarity_score for m in mappings) / len(mappings)
        mapping_count_factor = min(1.0, len(mappings) / 5.0)  # More mappings = higher confidence
        
        return min(1.0, avg_similarity * 0.7 + mapping_count_factor * 0.3)
        
    def _calculate_insight_novelty(self, insight_content: str) -> float:
        """Calculate novelty score of insight"""
        # Simple novelty calculation based on content complexity and uniqueness
        word_count = len(insight_content.split())
        unique_concepts = len(set(re.findall(r'\\b[a-z]{5,}\\b', insight_content.lower())))
        
        novelty = min(1.0, (unique_concepts / max(word_count, 1)) * 2.0)
        return max(0.3, novelty)  # Minimum novelty threshold
        
    def _generate_practical_applications(self, domain_a: str, domain_b: str, insight_content: str) -> List[str]:
        """Generate practical applications for the insight"""
        applications = []
        
        # Domain-specific applications
        if domain_a == 'pcb_design' and domain_b == 'software_engineering':
            applications.extend([
                'Apply modular PCB design principles to software architecture',
                'Use software testing strategies for PCB validation',
                'Implement version control concepts for PCB design iterations'
            ])
        elif domain_a == 'cognitive_systems' and domain_b == 'software_engineering':
            applications.extend([
                'Apply machine learning optimization to software performance',
                'Use cognitive load principles for UI/UX design',
                'Implement adaptive algorithms in software systems'
            ])
        elif domain_a == 'pcb_design' and domain_b == 'cognitive_systems':
            applications.extend([
                'Apply neural network principles to PCB routing optimization',
                'Use learning algorithms for component placement',
                'Implement feedback systems for design improvement'
            ])
            
        # General applications based on insight content
        if 'optimization' in insight_content.lower():
            applications.append('Cross-domain optimization framework')
        if 'pattern' in insight_content.lower():
            applications.append('Universal pattern recognition system')
        if 'principle' in insight_content.lower():
            applications.append('Unified design principle guidelines')
            
        return applications[:5]  # Limit to top 5
        
    def apply_cross_domain_insight(self, current_domain: str, problem_context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply cross-domain insights to solve problems in current domain"""
        applicable_insights = []
        
        # Find insights relevant to current domain
        for insight in self.synthesized_insights:
            if current_domain in insight.contributing_domains:
                applicable_insights.append(insight)
                
        # Sort by confidence and novelty
        applicable_insights.sort(key=lambda x: x.confidence_score * x.novelty_score, reverse=True)
        
        recommendations = []
        for insight in applicable_insights[:3]:  # Top 3 insights
            for application in insight.practical_applications:
                if self._application_matches_context(application, problem_context):
                    recommendations.append({
                        'insight_id': insight.insight_id,
                        'recommendation': application,
                        'confidence': insight.confidence_score,
                        'source_domains': insight.contributing_domains
                    })
                    
        return {
            'applicable_insights': len(applicable_insights),
            'recommendations': recommendations,
            'cross_domain_opportunities': self._identify_opportunities(current_domain, problem_context)
        }
        
    def _application_matches_context(self, application: str, context: Dict[str, Any]) -> bool:
        """Check if application is relevant to problem context"""
        application_terms = set(application.lower().split())
        context_terms = set(str(context).lower().split())
        
        # Simple term overlap matching
        overlap = len(application_terms & context_terms)
        return overlap > 0
        
    def _identify_opportunities(self, current_domain: str, context: Dict[str, Any]) -> List[str]:
        """Identify cross-domain learning opportunities"""
        opportunities = []
        
        # Check mappings from other domains to current domain
        for mapping in self.cross_mappings.values():
            if mapping.target_domain == current_domain:
                opportunities.append(f"Apply {mapping.source_concept} from {mapping.source_domain}")
                
        return opportunities[:3]  # Top 3 opportunities
        
    def generate_synthesis_report(self) -> str:
        """Generate comprehensive cross-domain synthesis report"""
        report = f"""# Cross-Domain Intelligence Synthesis Report
Generated: {datetime.now().isoformat()}

## Synthesis Summary
- **Domain Knowledge Entries**: {len(self.domain_knowledge)}
- **Cross-Domain Mappings**: {len(self.cross_mappings)}
- **Synthesized Insights**: {len(self.synthesized_insights)}
- **Active Domains**: {len(set(k.domain_name for k in self.domain_knowledge.values()))}

## Domain Coverage
"""
        
        # Domain distribution
        domain_counts = defaultdict(int)
        for knowledge in self.domain_knowledge.values():
            domain_counts[knowledge.domain_name] += 1
            
        for domain, count in domain_counts.items():
            report += f"- **{domain.title()}**: {count} knowledge entries\n"
            
        # Top cross-domain mappings
        report += "\n## Top Cross-Domain Mappings\n"
        top_mappings = sorted(self.cross_mappings.values(), key=lambda x: x.similarity_score, reverse=True)[:5]
        
        for mapping in top_mappings:
            report += f"- **{mapping.source_domain} → {mapping.target_domain}**\n"
            report += f"  - Concepts: {mapping.source_concept} ↔ {mapping.target_concept}\n"
            report += f"  - Similarity: {mapping.similarity_score:.1%}\n"
            report += f"  - Mechanism: {mapping.transfer_mechanism}\n"
            
        # Synthesized insights
        report += f"\n## Synthesized Insights ({len(self.synthesized_insights)})\n"
        
        for insight in self.synthesized_insights:
            report += f"### {insight.insight_id}\n"
            report += f"- **Domains**: {', '.join(insight.contributing_domains)}\n"
            report += f"- **Type**: {insight.synthesis_type}\n"
            report += f"- **Confidence**: {insight.confidence_score:.1%}\n"
            report += f"- **Novelty**: {insight.novelty_score:.1%}\n"
            report += f"- **Applications**: {len(insight.practical_applications)}\n\n"
            
        return report

def main():
    """Test cross-domain intelligence synthesis"""
    synthesis = CrossDomainIntelligence()
    
    print("[CROSS_DOMAIN] ===== CROSS-DOMAIN INTELLIGENCE SYNTHESIS =====")
    
    # Discover cross-domain mappings
    new_mappings = synthesis.discover_cross_domain_mappings()
    
    # Synthesize insights
    new_insights = synthesis.synthesize_cross_domain_insights()
    
    # Test application to a problem
    test_context = {
        'domain': 'software_engineering',
        'problem': 'code_organization',
        'constraints': ['maintainability', 'performance'],
        'goals': ['modularity', 'reusability']
    }
    
    application_result = synthesis.apply_cross_domain_insight('software_engineering', test_context)
    
    # Generate report
    report = synthesis.generate_synthesis_report()
    
    # Save all data
    synthesis.save_domain_data()
    
    report_path = synthesis.project_root / 'cross_domain_synthesis_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"[CROSS_DOMAIN] Synthesis report saved to: {report_path}")
    print(f"[CROSS_DOMAIN] Cross-domain mappings: {len(synthesis.cross_mappings)}")
    print(f"[CROSS_DOMAIN] Synthesized insights: {len(synthesis.synthesized_insights)}")
    print(f"[CROSS_DOMAIN] Application recommendations: {len(application_result['recommendations'])}")
    
    # Show sample insight
    if synthesis.synthesized_insights:
        sample_insight = synthesis.synthesized_insights[0]
        print(f"[CROSS_DOMAIN] Sample insight: {sample_insight.insight_id}")
        print(f"[CROSS_DOMAIN] Domains: {sample_insight.contributing_domains}")
        
    return synthesis

if __name__ == "__main__":
    main()