#!/usr/bin/env python3
"""
Cross-System Synthesizer v1.0 - Intelligent knowledge integration
Connects PCB, schematic, code, and hardware graph knowledge
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple

# Import our specialized tools
sys.path.append(str(Path(__file__).parent.parent / "tools"))
from kicad_pcb_parser import KiCadPCBParser

class CrossSystemSynthesizer:
    """Synthesize knowledge across all brain systems"""
    
    def __init__(self):
        self.schematic_data = None
        self.pcb_data = None
        self.hardware_graph = None
        self.cognitive_core = None
        
        self._load_cognitive_knowledge()
    
    def _load_cognitive_knowledge(self):
        """Load existing cognitive knowledge from brain systems"""
        
        # Load cognitive core
        cognitive_path = Path("claude/brain_systems/cognitive_core.json")
        if cognitive_path.exists():
            with open(cognitive_path, 'r') as f:
                self.cognitive_core = json.load(f)
        
        # Load schematic summary
        schematic_path = Path("CADfiles/MasterOfMuppets/schematic_summary.json")
        if schematic_path.exists():
            with open(schematic_path, 'r') as f:
                self.schematic_data = json.load(f)
        
        # Load hardware graph if available
        hw_graph_path = Path("claude/hardware_graph/master_of_muppets_graph.json")
        if hw_graph_path.exists():
            with open(hw_graph_path, 'r') as f:
                self.hardware_graph = json.load(f)
    
    def analyze_component_discrepancy(self, pcb_file_path: str) -> Dict[str, Any]:
        """Find discrepancies between schematic and PCB using proper hierarchical counting"""
        
        print("[SYNTHESIS] Cross-referencing schematic vs PCB components...")
        
        # Parse PCB
        pcb_parser = KiCadPCBParser(pcb_file_path)
        pcb_components = set(pcb_parser.components.keys())
        
        # Use accurate schematic component counter
        sys.path.append(str(Path(__file__).parent.parent / "tools"))
        from schematic_component_counter import SchematicComponentCounter
        
        # Get accurate schematic count
        schematic_summary_path = "CADfiles/MasterOfMuppets/schematic_summary.json"
        counter = SchematicComponentCounter(schematic_summary_path)
        sch_analysis = counter.count_all_components()
        
        # Build expected schematic component set with proper multipliers
        expected_schematic_components = set()
        for sch_name, sch_data in self.schematic_data.get('schematics', {}).items():
            multiplier = sch_analysis['sheet_multipliers'].get(sch_name, 1)
            
            for component in sch_data.get('components', []):
                ref = component.get('reference', '')
                # Filter out power symbols and other non-physical components
                if (not ref.startswith('#') and 
                    ref and 
                    'PWR' not in ref and
                    ref not in ['GND', 'VCC', '+12V', '-12V']):
                    
                    # Add instances based on sheet multipliers
                    if multiplier > 1:
                        for instance in range(multiplier):
                            expected_schematic_components.add(f"{ref}_{instance+1}")
                    else:
                        expected_schematic_components.add(ref)
        
        # Find discrepancies
        missing_in_pcb = expected_schematic_components - pcb_components
        extra_in_pcb = pcb_components - expected_schematic_components
        common_components = expected_schematic_components & pcb_components
        
        analysis = {
            'schematic_count': sch_analysis['total_physical_components'],
            'pcb_count': len(pcb_components),
            'common_count': len(common_components),
            'missing_in_pcb': list(missing_in_pcb),
            'extra_in_pcb': list(extra_in_pcb),
            'hierarchical_analysis': sch_analysis,
            'discrepancy_analysis': self._analyze_discrepancies(missing_in_pcb, extra_in_pcb)
        }
        
        return analysis
    
    def _analyze_discrepancies(self, missing: Set[str], extra: Set[str]) -> Dict[str, Any]:
        """Analyze the nature of component discrepancies"""
        
        analysis = {
            'missing_categories': {},
            'extra_categories': {},
            'possible_causes': [],
            'resolution_suggestions': []
        }
        
        # Categorize missing components
        for ref in missing:
            category = self._categorize_component_by_reference(ref)
            if category not in analysis['missing_categories']:
                analysis['missing_categories'][category] = []
            analysis['missing_categories'][category].append(ref)
        
        # Categorize extra components  
        for ref in extra:
            category = self._categorize_component_by_reference(ref)
            if category not in analysis['extra_categories']:
                analysis['extra_categories'][category] = []
            analysis['extra_categories'][category].append(ref)
        
        # Analyze possible causes
        if missing:
            analysis['possible_causes'].append("Components in schematic not yet placed in PCB")
            analysis['resolution_suggestions'].append("Update PCB from schematic in KiCad")
        
        if extra:
            analysis['possible_causes'].append("Components in PCB not in schematic (manual additions?)")
            analysis['resolution_suggestions'].append("Verify extra components are intentional")
        
        # Check for reference designator changes
        missing_refs = {ref[:-1] for ref in missing if ref[-1].isdigit()}
        extra_refs = {ref[:-1] for ref in extra if ref[-1].isdigit()}
        overlapping_types = missing_refs & extra_refs
        
        if overlapping_types:
            analysis['possible_causes'].append("Reference designator numbering changes")
            analysis['resolution_suggestions'].append("Check for renumbered components")
        
        return analysis
    
    def _categorize_component_by_reference(self, reference: str) -> str:
        """Categorize component by reference designator"""
        
        if reference.startswith('U'):
            return 'IC/Microcontroller'
        elif reference.startswith('R'):
            return 'Resistor'
        elif reference.startswith('C'):
            return 'Capacitor'
        elif reference.startswith('J'):
            return 'Connector/Jack'
        elif reference.startswith('L'):
            return 'Inductor'
        elif reference.startswith('D'):
            return 'Diode'
        elif reference.startswith('Q'):
            return 'Transistor'
        elif reference.startswith('T'):
            return 'Transformer/Teensy'
        elif reference.startswith('DAC'):
            return 'DAC'
        else:
            return 'Other'
    
    def synthesize_placement_intelligence(self, pcb_file_path: str) -> Dict[str, Any]:
        """Create intelligent placement suggestions using all available knowledge"""
        
        print("[SYNTHESIS] Integrating multi-system knowledge for placement...")
        
        synthesis = {
            'component_discrepancy': self.analyze_component_discrepancy(pcb_file_path),
            'hardware_constraints': self._extract_hardware_constraints(),
            'signal_flow_analysis': self._analyze_signal_flow(),
            'cognitive_insights': self._extract_cognitive_insights(),
            'integrated_suggestions': []
        }
        
        # Generate integrated suggestions
        synthesis['integrated_suggestions'] = self._generate_integrated_suggestions(synthesis)
        
        return synthesis
    
    def _extract_hardware_constraints(self) -> Dict[str, Any]:
        """Extract hardware constraints from cognitive core and hardware graph"""
        
        constraints = {
            'footprint_constraints': {},
            'performance_targets': {},
            'connectivity_requirements': {}
        }
        
        if self.cognitive_core:
            # Extract PCB footprint knowledge
            pcb_footprints = self.cognitive_core.get('mem', {}).get('pcb_footprints', {})
            if pcb_footprints:
                constraints['footprint_constraints'] = pcb_footprints
            
            # Extract hardware specs
            hw_idx = self.cognitive_core.get('idx', {}).get('hw', {})
            if hw_idx:
                constraints['performance_targets'] = {
                    'dac_specs': hw_idx.get('dac', []),
                    'opamp_specs': hw_idx.get('amp', []),
                    'i2c_specs': hw_idx.get('i2c', [])
                }
        
        if self.hardware_graph:
            # Extract connectivity from hardware graph
            constraints['connectivity_requirements'] = self.hardware_graph.get('connections', {})
        
        return constraints
    
    def _analyze_signal_flow(self) -> Dict[str, Any]:
        """Analyze signal flow from schematic for optimal placement"""
        
        signal_flow = {
            'critical_paths': [],
            'signal_groups': {},
            'interference_risks': []
        }
        
        if self.schematic_data:
            # Analyze schematic structure for signal flow
            for sch_name, sch_data in self.schematic_data.get('schematics', {}).items():
                if 'dac' in sch_name.lower():
                    signal_flow['signal_groups']['dac_cluster'] = [
                        comp['reference'] for comp in sch_data.get('components', [])
                        if not comp['reference'].startswith('#')
                    ]
                elif 'amp' in sch_name.lower():
                    signal_flow['signal_groups']['amp_cluster'] = [
                        comp['reference'] for comp in sch_data.get('components', [])
                        if not comp['reference'].startswith('#')
                    ]
                elif 'teensy' in sch_name.lower():
                    signal_flow['signal_groups']['digital_cluster'] = [
                        comp['reference'] for comp in sch_data.get('components', [])
                        if not comp['reference'].startswith('#')
                    ]
        
        # Define critical signal paths based on Master of Muppets architecture
        signal_flow['critical_paths'] = [
            {'name': 'I2C_Bus', 'components': ['T1', 'DAC1', 'DAC2'], 'max_length': 50.0},
            {'name': 'DAC1_Outputs', 'components': ['DAC1', 'U1', 'U2'], 'max_length': 15.0},
            {'name': 'DAC2_Outputs', 'components': ['DAC2', 'U3', 'U4'], 'max_length': 15.0},
            {'name': 'CV_Outputs', 'components': ['U1', 'U2', 'U3', 'U4', 'J2-J17'], 'max_length': 30.0}
        ]
        
        return signal_flow
    
    def _extract_cognitive_insights(self) -> List[str]:
        """Extract insights from cognitive learning sessions"""
        
        insights = []
        
        if self.cognitive_core:
            # Extract from cognitive memory
            mem = self.cognitive_core.get('mem', {})
            
            # Season 1 learnings
            s1_achievements = mem.get('s1', {}).get('achieve', [])
            for achievement in s1_achievements:
                if 'graph' in achievement:
                    insights.append("Hardware graphs available for component relationship analysis")
                elif 'tool' in achievement:
                    insights.append("Specialized tools available for accelerated analysis")
            
            # PCB footprint knowledge  
            if 'pcb_footprints' in mem:
                insights.append("Real footprint dimensions available for accurate placement")
                insights.append("Design constraints integrated (trace width, via size, spacing)")
        
        # Add Master of Muppets specific insights
        insights.extend([
            "16-channel CV architecture requires systematic OpAmp grouping",
            "I2C bus timing critical for dual-DAC operation", 
            "Jack mechanical constraints dominate board edge placement",
            "Analog/digital separation essential for signal integrity"
        ])
        
        return insights
    
    def _generate_integrated_suggestions(self, synthesis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate placement suggestions using integrated knowledge"""
        
        suggestions = []
        
        # Discrepancy-based suggestions
        discrepancy = synthesis['component_discrepancy']
        if discrepancy['missing_in_pcb']:
            suggestions.append({
                'type': 'missing_components',
                'priority': 10,
                'description': f"Resolve {len(discrepancy['missing_in_pcb'])} missing components",
                'action': 'Update PCB from schematic in KiCad',
                'components': discrepancy['missing_in_pcb'][:5]  # Show first 5
            })
        
        # Signal flow based suggestions
        signal_flow = synthesis['signal_flow_analysis']
        for path in signal_flow['critical_paths']:
            suggestions.append({
                'type': 'signal_integrity',
                'priority': 8,
                'description': f"Optimize {path['name']} routing length < {path['max_length']}mm",
                'action': f"Group components: {', '.join(path['components'][:3])}...",
                'components': path['components']
            })
        
        # Hardware constraint suggestions
        hw_constraints = synthesis['hardware_constraints']
        if 'footprint_constraints' in hw_constraints:
            constraints = hw_constraints['footprint_constraints']
            if 'jack_3.5mm' in constraints:
                suggestions.append({
                    'type': 'mechanical_constraint',
                    'priority': 9,
                    'description': "Apply jack spacing constraints (19.05mm minimum)",
                    'action': "Align jacks vertically with proper spacing",
                    'constraints': constraints['jack_3.5mm']
                })
        
        return sorted(suggestions, key=lambda x: x['priority'], reverse=True)
    
    def generate_synthesis_report(self, pcb_file_path: str) -> str:
        """Generate comprehensive cross-system analysis report"""
        
        synthesis = self.synthesize_placement_intelligence(pcb_file_path)
        
        report = f"""# Cross-System Intelligence Synthesis Report

## Component Synchronization Analysis
- **Schematic Components**: {synthesis['component_discrepancy']['schematic_count']}
- **PCB Components**: {synthesis['component_discrepancy']['pcb_count']}
- **Missing in PCB**: {len(synthesis['component_discrepancy']['missing_in_pcb'])}
- **Synchronized**: {synthesis['component_discrepancy']['common_count']}

"""
        
        # Component discrepancy details
        if synthesis['component_discrepancy']['missing_in_pcb']:
            report += "### Missing Components in PCB:\n"
            missing_cats = synthesis['component_discrepancy']['discrepancy_analysis']['missing_categories']
            for category, components in missing_cats.items():
                report += f"- **{category}**: {', '.join(components[:5])}"
                if len(components) > 5:
                    report += f" (+{len(components)-5} more)"
                report += "\n"
        
        # Integrated suggestions
        report += "\n## Integrated Placement Suggestions\n"
        for i, suggestion in enumerate(synthesis['integrated_suggestions'][:10], 1):
            report += f"{i}. **{suggestion['type'].title()}** (Priority {suggestion['priority']})\n"
            report += f"   - {suggestion['description']}\n"
            report += f"   - Action: {suggestion['action']}\n\n"
        
        # Signal flow insights
        signal_flow = synthesis['signal_flow_analysis']
        if signal_flow['critical_paths']:
            report += "## Critical Signal Paths\n"
            for path in signal_flow['critical_paths']:
                report += f"- **{path['name']}**: {len(path['components'])} components, <{path['max_length']}mm max\n"
        
        # Cognitive insights
        insights = synthesis['cognitive_insights']
        if insights:
            report += "\n## Cognitive System Insights\n"
            for insight in insights[:5]:
                report += f"- {insight}\n"
        
        return report
    
    def update_cognitive_core_with_pcb_analysis(self, pcb_analysis: Dict[str, Any]):
        """Update cognitive core with new PCB placement insights"""
        
        if not self.cognitive_core:
            return
        
        # Add PCB placement insights to cognitive memory
        if 'mem' not in self.cognitive_core:
            self.cognitive_core['mem'] = {}
        
        self.cognitive_core['mem']['pcb_placement_analysis'] = {
            'timestamp': 'latest',
            'component_count': pcb_analysis.get('pcb_count', 0),
            'placement_issues': pcb_analysis.get('discrepancy_analysis', {}),
            'optimization_opportunities': len(pcb_analysis.get('missing_in_pcb', []))
        }
        
        # Write back to cognitive core
        cognitive_path = Path("claude/brain_systems/cognitive_core.json")
        with open(cognitive_path, 'w') as f:
            json.dump(self.cognitive_core, f, indent=2)
        
        print("[SYNTHESIS] Updated cognitive core with PCB analysis insights")

# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cross_system_synthesizer.py <pcb_file>")
        sys.exit(1)
    
    pcb_file = sys.argv[1]
    synthesizer = CrossSystemSynthesizer()
    
    # Generate synthesis report
    report = synthesizer.generate_synthesis_report(pcb_file)
    print(report)
    
    # Update cognitive systems with insights
    analysis = synthesizer.analyze_component_discrepancy(pcb_file)
    synthesizer.update_cognitive_core_with_pcb_analysis(analysis)