#!/usr/bin/env python3
"""
Schematic Brain v1.0 - Intelligent KiCad Analysis and Hardware Understanding
Builds on the KiCad parser with AI-enhanced pattern recognition and learning
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import subprocess
import re

# Import our existing KiCad parser
import sys
sys.path.append(str(Path(__file__).parent.parent / "automation" / "tools"))
try:
    from kicad_hierarchical_parser import KiCadHierarchicalParser
except ImportError:
    print("[WARN] KiCad parser not found - some features disabled")
    KiCadHierarchicalParser = None

@dataclass
class HardwareInsight:
    """An insight about the hardware design"""
    id: str
    type: str  # placement, routing, power, thermal, signal_integrity, etc.
    description: str
    components: List[str]
    severity: int  # 1-10, 10 being critical
    suggested_action: str
    confidence: float
    discovered_time: float = field(default_factory=time.time)

@dataclass
class ComponentRelationship:
    """Relationship between hardware components"""
    from_component: str
    to_component: str
    relationship_type: str  # electrical, thermal, proximity, functional
    strength: float  # 0.0 - 1.0
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DesignPattern:
    """Recognized hardware design pattern"""
    name: str
    components: List[str]
    pattern_type: str  # power_distribution, signal_conditioning, etc.
    description: str
    best_practices: List[str]
    common_issues: List[str]

class SchematicBrain:
    """AI-enhanced schematic analysis and understanding system"""
    
    def __init__(self, project_path: str = "CADfiles/MasterOfMuppets"):
        self.project_path = Path(project_path)
        self.insights: List[HardwareInsight] = []
        self.relationships: List[ComponentRelationship] = []
        self.patterns: List[DesignPattern] = []
        self.component_database: Dict[str, Dict] = {}
        self.layout_constraints: Dict[str, Any] = {}
        
        # Brain persistence
        self.brain_file = Path("claude/schematic_brain.json")
        self._load_brain()
        
        # Component knowledge base
        self._build_component_knowledge()
    
    def analyze_schematics(self, force_update: bool = False) -> Dict[str, Any]:
        """Perform comprehensive schematic analysis"""
        print("🔍 Analyzing schematics with AI enhancement...")
        
        results = {
            "insights": [],
            "patterns": [],
            "relationships": [],
            "recommendations": []
        }
        
        # Use KiCad parser for basic structure
        if KiCadHierarchicalParser:
            parser = KiCadHierarchicalParser(str(self.project_path))
            hierarchy = parser.parse_hierarchy()
            components = parser.get_all_components()
            
            # AI-enhanced analysis
            results["insights"] = self._analyze_component_insights(components)
            results["patterns"] = self._recognize_design_patterns(components, hierarchy)
            results["relationships"] = self._analyze_relationships(components)
            results["recommendations"] = self._generate_recommendations()
        
        # Learn from analysis
        self._learn_from_analysis(results)
        self._save_brain()
        
        return results
    
    def _analyze_component_insights(self, components: Dict) -> List[HardwareInsight]:
        """Generate insights about component placement and usage"""
        insights = []
        
        # Power distribution analysis
        power_components = self._find_power_components(components)
        if len(power_components) > 4:
            insights.append(HardwareInsight(
                id=self._generate_id("power_complexity"),
                type="power",
                description=f"Complex power distribution with {len(power_components)} power-related components",
                components=list(power_components.keys()),
                severity=6,
                suggested_action="Consider power distribution zones and decoupling strategy",
                confidence=0.8
            ))
        
        # Thermal analysis
        high_power_ics = self._find_high_power_components(components)
        if high_power_ics:
            insights.append(HardwareInsight(
                id=self._generate_id("thermal_concern"),
                type="thermal",
                description=f"High-power components detected: {', '.join(high_power_ics)}",
                components=high_power_ics,
                severity=7,
                suggested_action="Ensure adequate spacing and thermal management",
                confidence=0.9
            ))
        
        # Signal integrity analysis
        high_speed_components = self._find_high_speed_components(components)
        if high_speed_components:
            insights.append(HardwareInsight(
                id=self._generate_id("signal_integrity"),
                type="signal_integrity",
                description="High-speed digital components require careful routing",
                components=high_speed_components,
                severity=8,
                suggested_action="Use controlled impedance traces and minimize trace lengths",
                confidence=0.85
            ))
        
        # Connectivity analysis
        isolated_components = self._find_isolated_components(components)
        if isolated_components:
            insights.append(HardwareInsight(
                id=self._generate_id("connectivity"),
                type="placement",
                description=f"Components with few connections: {', '.join(isolated_components)}",
                components=isolated_components,
                severity=4,
                suggested_action="Consider placement near board edges or in dedicated areas",
                confidence=0.7
            ))
        
        self.insights.extend(insights)
        return insights
    
    def _recognize_design_patterns(self, components: Dict, hierarchy: Dict) -> List[DesignPattern]:
        """Recognize common hardware design patterns"""
        patterns = []
        
        # DAC + OpAmp pattern (specific to our project)
        dac_components = [name for name in components.keys() if 'dac' in name.lower() or 'ad5593' in name.lower()]
        amp_components = [name for name in components.keys() if 'amp' in name.lower() or 'tl074' in name.lower()]
        
        if dac_components and amp_components:
            patterns.append(DesignPattern(
                name="DAC Signal Conditioning",
                components=dac_components + amp_components,
                pattern_type="signal_conditioning",
                description="DAC outputs feeding operational amplifiers for signal conditioning",
                best_practices=[
                    "Keep DAC-to-OpAmp traces short",
                    "Use appropriate decoupling capacitors",
                    "Consider analog ground plane",
                    "Minimize digital noise coupling"
                ],
                common_issues=[
                    "Long traces introduce noise",
                    "Inadequate power supply decoupling",
                    "Digital switching noise coupling",
                    "Thermal gradients affecting precision"
                ]
            ))
        
        # Power regulation pattern
        reg_components = [name for name in components.keys() if any(term in name.lower() for term in ['reg', 'ldo', 'vreg', 'supply'])]
        if reg_components:
            patterns.append(DesignPattern(
                name="Power Regulation Network",
                components=reg_components,
                pattern_type="power_distribution",
                description="Voltage regulation and distribution network",
                best_practices=[
                    "Use adequate input/output capacitors",
                    "Keep thermal considerations in mind",
                    "Minimize dropout voltage",
                    "Use proper ground plane connections"
                ],
                common_issues=[
                    "Insufficient heat dissipation",
                    "Inadequate decoupling",
                    "Ground loop issues",
                    "Load regulation problems"
                ]
            ))
        
        # Microcontroller pattern
        mcu_components = [name for name in components.keys() if any(term in name.lower() for term in ['teensy', 'arduino', 'mcu', 'cpu'])]
        if mcu_components:
            patterns.append(DesignPattern(
                name="Microcontroller System",
                components=mcu_components,
                pattern_type="digital_processing",
                description="Central processing unit with support circuitry",
                best_practices=[
                    "Provide clean power with decoupling",
                    "Use proper crystal oscillator layout",
                    "Include programming/debug connectors",
                    "Consider EMI/EMC requirements"
                ],
                common_issues=[
                    "Clock signal integrity",
                    "Power supply noise",
                    "Reset circuit reliability",
                    "Programming access"
                ]
            ))
        
        self.patterns.extend(patterns)
        return patterns
    
    def _analyze_relationships(self, components: Dict) -> List[ComponentRelationship]:
        """Analyze relationships between components"""
        relationships = []
        
        # Electrical relationships (based on nets/connections)
        # This would be enhanced with actual netlist parsing
        
        # Functional relationships (based on component types and names)
        dac_components = [name for name in components.keys() if 'dac' in name.lower()]
        amp_components = [name for name in components.keys() if 'amp' in name.lower()]
        
        # DAC to Amp relationships
        for dac in dac_components:
            for amp in amp_components:
                if self._components_likely_connected(dac, amp):
                    relationships.append(ComponentRelationship(
                        from_component=dac,
                        to_component=amp,
                        relationship_type="electrical",
                        strength=0.9,
                        properties={"signal_type": "analog", "criticality": "high"}
                    ))
        
        # Thermal relationships (high-power components)
        high_power = self._find_high_power_components(components)
        for i, comp1 in enumerate(high_power):
            for comp2 in high_power[i+1:]:
                relationships.append(ComponentRelationship(
                    from_component=comp1,
                    to_component=comp2,
                    relationship_type="thermal",
                    strength=0.7,
                    properties={"concern": "heat_dissipation", "min_distance": "5mm"}
                ))
        
        self.relationships.extend(relationships)
        return relationships
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Based on insights
        critical_insights = [i for i in self.insights if i.severity >= 7]
        for insight in critical_insights:
            recommendations.append(f"HIGH PRIORITY: {insight.suggested_action} (for {insight.type})")
        
        # Based on patterns
        for pattern in self.patterns:
            if pattern.pattern_type == "signal_conditioning":
                recommendations.append("Signal conditioning detected - verify analog layout guidelines")
            elif pattern.pattern_type == "power_distribution":
                recommendations.append("Power distribution - ensure proper decoupling and thermal management")
        
        # Based on relationships
        thermal_relationships = [r for r in self.relationships if r.relationship_type == "thermal"]
        if len(thermal_relationships) > 3:
            recommendations.append("Multiple thermal concerns - consider component spacing and cooling")
        
        return recommendations
    
    def generate_placement_constraints(self) -> Dict[str, Any]:
        """Generate placement constraints for PCB layout"""
        constraints = {
            "keep_together": [],
            "keep_apart": [],
            "placement_zones": {},
            "routing_constraints": []
        }
        
        # Components that should be kept together
        for rel in self.relationships:
            if rel.relationship_type == "electrical" and rel.strength > 0.8:
                constraints["keep_together"].append([rel.from_component, rel.to_component])
        
        # Components that should be kept apart
        for rel in self.relationships:
            if rel.relationship_type == "thermal" and rel.strength > 0.6:
                min_dist = rel.properties.get("min_distance", "3mm")
                constraints["keep_apart"].append({
                    "components": [rel.from_component, rel.to_component],
                    "min_distance": min_dist
                })
        
        # Placement zones based on patterns
        for pattern in self.patterns:
            if pattern.pattern_type == "power_distribution":
                constraints["placement_zones"]["power_zone"] = {
                    "components": pattern.components,
                    "guidelines": "Central location with good thermal management"
                }
            elif pattern.pattern_type == "signal_conditioning":
                constraints["placement_zones"]["analog_zone"] = {
                    "components": pattern.components,
                    "guidelines": "Away from digital switching, short analog traces"
                }
        
        self.layout_constraints = constraints
        return constraints
    
    def get_brain_summary(self) -> Dict[str, Any]:
        """Get summary of learned hardware knowledge"""
        return {
            "insights_count": len(self.insights),
            "patterns_count": len(self.patterns),
            "relationships_count": len(self.relationships),
            "critical_insights": len([i for i in self.insights if i.severity >= 7]),
            "component_knowledge": len(self.component_database),
            "avg_insight_confidence": sum(i.confidence for i in self.insights) / max(1, len(self.insights)),
            "pattern_types": list(set(p.pattern_type for p in self.patterns)),
            "relationship_types": list(set(r.relationship_type for r in self.relationships))
        }
    
    def update_cognitive_systems(self):
        """Update other cognitive systems with hardware insights"""
        summary = self.get_brain_summary()
        
        # Update cognitive core
        from cognitive_ops import CognitiveCore
        cc = CognitiveCore()
        
        cc.u("idx.hw.insights", f"{summary['insights_count']}_total")
        cc.u("idx.hw.patterns", f"{summary['patterns_count']}_recognized")
        cc.u("idx.hw.critical", f"{summary['critical_insights']}_issues")
        cc.save()
        
        # Update neural core with insights
        from neural_core import NeuralCore
        neural = NeuralCore()
        
        for insight in self.insights[-5:]:  # Last 5 insights
            neural.learn_insight(
                f"Hardware: {insight.description}",
                {"type": insight.type, "severity": insight.severity},
                confidence=insight.confidence
            )
        
        print(f"🧠 Updated cognitive systems with {summary['insights_count']} hardware insights")
    
    def _build_component_knowledge(self):
        """Build knowledge base of component characteristics"""
        self.component_database = {
            # DACs
            "ad5593r": {
                "type": "ic",
                "function": "dac",
                "power_consumption": "medium",
                "thermal_profile": "low",
                "signal_type": "analog",
                "placement_priority": "high",
                "routing_constraints": ["short_analog_traces", "avoid_digital_noise"]
            },
            
            # Op-Amps
            "tl074": {
                "type": "ic", 
                "function": "opamp",
                "power_consumption": "low",
                "thermal_profile": "low",
                "signal_type": "analog",
                "placement_priority": "high",
                "routing_constraints": ["matched_traces", "low_noise_environment"]
            },
            
            # Microcontrollers
            "teensy": {
                "type": "module",
                "function": "mcu",
                "power_consumption": "medium",
                "thermal_profile": "medium",
                "signal_type": "digital",
                "placement_priority": "medium",
                "routing_constraints": ["clock_routing", "power_decoupling"]
            }
        }
    
    def _find_power_components(self, components: Dict) -> Dict[str, str]:
        """Find power-related components"""
        power_components = {}
        power_keywords = ['reg', 'ldo', 'supply', 'power', 'vcc', 'gnd', 'capacitor', 'inductor']
        
        for name, comp in components.items():
            if any(keyword in name.lower() for keyword in power_keywords):
                power_components[name] = comp
        
        return power_components
    
    def _find_high_power_components(self, components: Dict) -> List[str]:
        """Find components that generate significant heat"""
        high_power = []
        high_power_keywords = ['reg', 'ldo', 'driver', 'power', 'switching']
        high_power_parts = ['tl074', 'lm317', 'ams1117']
        
        for name in components.keys():
            if (any(keyword in name.lower() for keyword in high_power_keywords) or
                any(part in name.lower() for part in high_power_parts)):
                high_power.append(name)
        
        return high_power
    
    def _find_high_speed_components(self, components: Dict) -> List[str]:
        """Find high-speed digital components"""
        high_speed = []
        hs_keywords = ['teensy', 'mcu', 'cpu', 'crystal', 'oscillator', 'clock']
        
        for name in components.keys():
            if any(keyword in name.lower() for keyword in hs_keywords):
                high_speed.append(name)
        
        return high_speed
    
    def _find_isolated_components(self, components: Dict) -> List[str]:
        """Find components with few connections (heuristic)"""
        isolated = []
        isolated_keywords = ['test', 'tp', 'jumper', 'connector', 'jack']
        
        for name in components.keys():
            if any(keyword in name.lower() for keyword in isolated_keywords):
                isolated.append(name)
        
        return isolated
    
    def _components_likely_connected(self, comp1: str, comp2: str) -> bool:
        """Heuristic to determine if components are likely connected"""
        # Simple heuristic based on naming patterns
        if 'dac' in comp1.lower() and 'amp' in comp2.lower():
            return True
        if 'supply' in comp1.lower() or 'supply' in comp2.lower():
            return True
        return False
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID for insights/patterns"""
        timestamp = str(int(time.time()))
        return f"{prefix}_{timestamp}_{hash(prefix) % 1000:03d}"
    
    def _learn_from_analysis(self, results: Dict[str, Any]):
        """Learn patterns from analysis results"""
        # This would implement machine learning from repeated analyses
        # For now, just record the analysis
        pass
    
    def _load_brain(self):
        """Load persisted brain state"""
        if self.brain_file.exists():
            try:
                with open(self.brain_file, 'r') as f:
                    data = json.load(f)
                
                # Reconstruct objects (simplified for now)
                self.insights = [HardwareInsight(**item) for item in data.get('insights', [])]
                self.patterns = [DesignPattern(**item) for item in data.get('patterns', [])]
                # Relationships would need custom deserialization
                
                print(f"🧠 Loaded schematic brain: {len(self.insights)} insights, {len(self.patterns)} patterns")
            except Exception as e:
                print(f"⚠️ Error loading schematic brain: {e}")
    
    def _save_brain(self):
        """Save brain state to file"""
        self.brain_file.parent.mkdir(exist_ok=True)
        
        data = {
            "insights": [insight.__dict__ for insight in self.insights],
            "patterns": [pattern.__dict__ for pattern in self.patterns],
            "layout_constraints": self.layout_constraints,
            "last_analysis": time.time()
        }
        
        with open(self.brain_file, 'w') as f:
            json.dump(data, f, indent=2)

# CLI interface
if __name__ == "__main__":
    import sys
    
    brain = SchematicBrain()
    
    if len(sys.argv) < 2:
        summary = brain.get_brain_summary()
        print("🔬 Schematic Brain Summary:")
        print(f"   Insights: {summary['insights_count']} ({summary['critical_insights']} critical)")
        print(f"   Patterns: {summary['patterns_count']}")
        print(f"   Relationships: {summary['relationships_count']}")
        print(f"   Avg Confidence: {summary['avg_insight_confidence']:.2f}")
        print("\nCommands:")
        print("  analyze          - Analyze schematics")
        print("  constraints      - Generate placement constraints")
        print("  update           - Update cognitive systems")
        print("  insights         - Show critical insights")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == 'analyze':
        results = brain.analyze_schematics(force_update=True)
        print(f"📊 Analysis complete:")
        print(f"   New insights: {len(results['insights'])}")
        print(f"   Patterns found: {len(results['patterns'])}")
        print(f"   Recommendations: {len(results['recommendations'])}")
        
        for rec in results['recommendations']:
            print(f"💡 {rec}")
    
    elif cmd == 'constraints':
        constraints = brain.generate_placement_constraints()
        print("📐 Placement Constraints Generated:")
        print(json.dumps(constraints, indent=2))
    
    elif cmd == 'update':
        brain.update_cognitive_systems()
    
    elif cmd == 'insights':
        critical = [i for i in brain.insights if i.severity >= 7]
        for insight in critical:
            print(f"⚠️ {insight.type.upper()}: {insight.description}")
            print(f"   Action: {insight.suggested_action}")
            print(f"   Confidence: {insight.confidence:.2f}")
            print()
    
    else:
        print(f"Unknown command: {cmd}")