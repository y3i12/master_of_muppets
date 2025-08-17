#!/usr/bin/env python3
"""
Component Count Investigator v1.0 - Resolve component count discrepancies
Analyzes all sources to understand the true component count
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Any

# Import our tools
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / "brain_systems"))

class ComponentCountInvestigator:
    """Investigate component count discrepancies across all sources"""
    
    def __init__(self):
        self.results = {
            'sources': {},
            'analysis': {},
            'discrepancies': {},
            'resolution': {}
        }
    
    def analyze_pcb_file(self, pcb_file_path: str) -> Dict[str, Any]:
        """Analyze PCB file directly"""
        from kicad_pcb_parser import KiCadPCBParser
        
        parser = KiCadPCBParser(pcb_file_path)
        components = parser.components
        
        # Categorize components
        categories = {}
        for ref, comp in components.items():
            if ref.startswith('R'):
                cat = 'Resistor'
            elif ref.startswith('C'):
                cat = 'Capacitor'
            elif ref.startswith('J'):
                cat = 'Jack/Connector'
            elif ref.startswith(('U', 'OpAmp')):
                cat = 'IC/OpAmp'
            elif ref.startswith('T'):
                cat = 'Microcontroller'
            elif ref.startswith('DAC'):
                cat = 'DAC'
            else:
                cat = 'Other'
            
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(ref)
        
        return {
            'source': 'PCB File (kicad_pcb)',
            'total_count': len(components),
            'categories': categories,
            'component_refs': list(components.keys())
        }
    
    def analyze_schematic_summary(self, summary_path: str) -> Dict[str, Any]:
        """Analyze schematic summary"""
        from schematic_component_counter import SchematicComponentCounter
        
        if not Path(summary_path).exists():
            return {'source': 'Schematic Summary', 'error': 'File not found'}
        
        counter = SchematicComponentCounter(summary_path)
        analysis = counter.count_all_components()
        
        # Get individual schematic components (not instances)
        with open(summary_path, 'r') as f:
            schematic_data = json.load(f)
        
        all_unique_components = set()
        for sch_name, sch_data in schematic_data.get('schematics', {}).items():
            for component in sch_data.get('components', []):
                ref = component.get('reference', '')
                if (not ref.startswith('#') and 
                    ref and 
                    'PWR' not in ref and
                    ref not in ['GND', 'VCC', '+12V', '-12V']):
                    all_unique_components.add(ref)
        
        return {
            'source': 'Schematic Summary (hierarchical)',
            'total_count': analysis['total_physical_components'],
            'unique_components_count': len(all_unique_components),
            'sheet_multipliers': analysis['sheet_multipliers'],
            'hierarchical_breakdown': analysis['type_counts'],
            'unique_component_refs': list(all_unique_components)
        }
    
    def analyze_consolidated_data(self, consolidated_path: str) -> Dict[str, Any]:
        """Analyze consolidated PCB data"""
        
        if not Path(consolidated_path).exists():
            return {'source': 'Consolidated Data', 'error': 'File not found'}
        
        with open(consolidated_path, 'r') as f:
            data = json.load(f)
        
        component_analysis = data.get('component_analysis', {})
        
        return {
            'source': 'Consolidated PCB Analysis',
            'total_count': component_analysis.get('total_components', 0),
            'category_counts': component_analysis.get('component_counts', {}),
            'has_positions': 'component_positions' in component_analysis
        }
    
    def analyze_cognitive_core(self, core_path: str) -> Dict[str, Any]:
        """Analyze cognitive core cached data"""
        
        if not Path(core_path).exists():
            return {'source': 'Cognitive Core', 'error': 'File not found'}
        
        with open(core_path, 'r') as f:
            data = json.load(f)
        
        # Look for component references
        kicad_info = data.get('idx', {}).get('kicad', {})
        cached_count = None
        
        components_info = kicad_info.get('components', [])
        for item in components_info:
            if '_total' in str(item):
                cached_count = item
                break
        
        pcb_analysis = data.get('mem', {}).get('pcb_placement_analysis', {})
        
        return {
            'source': 'Cognitive Core Cache',
            'cached_reference': cached_count,
            'current_pcb_count': pcb_analysis.get('component_count', 0),
            'has_placement_issues': 'placement_issues' in pcb_analysis
        }
    
    def cross_reference_components(self, pcb_refs: List[str], 
                                 schematic_refs: List[str]) -> Dict[str, Any]:
        """Cross-reference component lists to find discrepancies"""
        
        pcb_set = set(pcb_refs)
        sch_set = set(schematic_refs)
        
        # Basic analysis
        common = pcb_set & sch_set
        pcb_only = pcb_set - sch_set
        sch_only = sch_set - pcb_set
        
        # Analyze patterns in differences
        pcb_patterns = self._analyze_ref_patterns(list(pcb_only))
        sch_patterns = self._analyze_ref_patterns(list(sch_only))
        
        return {
            'total_pcb': len(pcb_set),
            'total_schematic': len(sch_set),
            'common_count': len(common),
            'pcb_only_count': len(pcb_only),
            'schematic_only_count': len(sch_only),
            'pcb_only_patterns': pcb_patterns,
            'schematic_only_patterns': sch_patterns,
            'common_components': list(common)[:10],  # Sample
            'pcb_only_components': list(pcb_only)[:10],  # Sample
            'schematic_only_components': list(sch_only)[:10]  # Sample
        }
    
    def _analyze_ref_patterns(self, refs: List[str]) -> Dict[str, int]:
        """Analyze patterns in reference designators"""
        patterns = {}
        
        for ref in refs:
            # Extract prefix (letter part)
            prefix = ''.join(c for c in ref if c.isalpha())
            patterns[prefix] = patterns.get(prefix, 0) + 1
        
        return patterns
    
    def generate_investigation_report(self) -> str:
        """Generate comprehensive investigation report"""
        
        report = """# Component Count Investigation Report
Generated: Component Count Investigator v1.0

## Summary of Sources
"""
        
        total_counts = {}
        
        for source_name, data in self.results['sources'].items():
            if 'error' in data:
                report += f"- **{source_name}**: Error - {data['error']}\n"
            else:
                count = data.get('total_count', 0)
                total_counts[source_name] = count
                report += f"- **{source_name}**: {count} components\n"
        
        # Discrepancy analysis
        if len(total_counts) > 1:
            counts = list(total_counts.values())
            min_count, max_count = min(counts), max(counts)
            
            report += f"\n## Count Discrepancy Analysis\n"
            report += f"- **Range**: {min_count} to {max_count} components\n"
            report += f"- **Variance**: {max_count - min_count} components\n"
            
            if 'cross_reference' in self.results:
                cross_ref = self.results['cross_reference']
                report += f"- **Common Components**: {cross_ref['common_count']}\n"
                report += f"- **PCB Only**: {cross_ref['pcb_only_count']}\n"
                report += f"- **Schematic Only**: {cross_ref['schematic_only_count']}\n"
        
        # Resolution recommendations
        report += f"\n## Investigation Findings\n"
        
        if 'cross_reference' in self.results:
            cross_ref = self.results['cross_reference']
            
            # Analyze patterns
            pcb_patterns = cross_ref.get('pcb_only_patterns', {})
            sch_patterns = cross_ref.get('schematic_only_patterns', {})
            
            if pcb_patterns:
                report += f"\n### PCB-Only Component Patterns:\n"
                for pattern, count in sorted(pcb_patterns.items()):
                    report += f"- **{pattern}**: {count} components\n"
            
            if sch_patterns:
                report += f"\n### Schematic-Only Component Patterns:\n"
                for pattern, count in sorted(sch_patterns.items()):
                    report += f"- **{pattern}**: {count} components\n"
        
        return report
    
    def run_full_investigation(self) -> Dict[str, Any]:
        """Run complete component count investigation"""
        
        print("[INVESTIGATOR] Starting component count investigation...")
        
        # Analyze PCB file
        pcb_analysis = self.analyze_pcb_file("CADfiles/MasterOfMuppets/MasterOfMuppets.kicad_pcb")
        self.results['sources']['PCB_File'] = pcb_analysis
        print(f"[INVESTIGATOR] PCB file: {pcb_analysis.get('total_count', 0)} components")
        
        # Analyze schematic summary
        sch_analysis = self.analyze_schematic_summary("CADfiles/MasterOfMuppets/schematic_summary.json")
        self.results['sources']['Schematic_Summary'] = sch_analysis
        print(f"[INVESTIGATOR] Schematic (hierarchical): {sch_analysis.get('total_count', 0)} components")
        print(f"[INVESTIGATOR] Schematic (unique): {sch_analysis.get('unique_components_count', 0)} components")
        
        # Analyze consolidated data
        cons_analysis = self.analyze_consolidated_data("claude/brain_systems/pcb_analysis_consolidated.json")
        self.results['sources']['Consolidated_Data'] = cons_analysis
        print(f"[INVESTIGATOR] Consolidated data: {cons_analysis.get('total_count', 0)} components")
        
        # Analyze cognitive core
        core_analysis = self.analyze_cognitive_core("claude/brain_systems/cognitive_core.json")
        self.results['sources']['Cognitive_Core'] = core_analysis
        print(f"[INVESTIGATOR] Cognitive core cache: {core_analysis.get('cached_reference', 'Unknown')}")
        
        # Cross-reference if we have both PCB and schematic data
        if ('component_refs' in pcb_analysis and 
            'unique_component_refs' in sch_analysis):
            cross_ref = self.cross_reference_components(
                pcb_analysis['component_refs'],
                sch_analysis['unique_component_refs']
            )
            self.results['cross_reference'] = cross_ref
            print(f"[INVESTIGATOR] Cross-reference: {cross_ref['common_count']} common, {cross_ref['pcb_only_count']} PCB-only, {cross_ref['schematic_only_count']} schematic-only")
        
        return self.results

def main():
    investigator = ComponentCountInvestigator()
    results = investigator.run_full_investigation()
    
    # Generate report
    report = investigator.generate_investigation_report()
    
    with open("component_count_investigation.md", 'w') as f:
        f.write(report)
    
    print(f"\n[INVESTIGATOR] Investigation complete!")
    print(f"Report saved to: component_count_investigation.md")
    
    return results

if __name__ == "__main__":
    main()