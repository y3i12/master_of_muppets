#!/usr/bin/env python3
"""
Fresh Schematic Ingester v1.0 - Complete re-ingestion of all schematic data
Provides authoritative component counts and cross-references
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict

class FreshSchematicIngester:
    """Complete schematic data re-ingestion and analysis"""
    
    def __init__(self):
        self.schematic_data = {}
        self.total_analysis = {
            'unique_components': set(),
            'all_instances': [],
            'hierarchy_map': {},
            'component_categories': defaultdict(list)
        }
    
    def load_schematic_summary(self, summary_path: str) -> bool:
        """Load the schematic summary JSON"""
        try:
            with open(summary_path, 'r') as f:
                self.schematic_data = json.load(f)
            print(f"[INGESTER] Loaded schematic summary: {summary_path}")
            return True
        except Exception as e:
            print(f"[INGESTER] Error loading {summary_path}: {e}")
            return False
    
    def analyze_individual_schematics(self) -> Dict[str, Any]:
        """Analyze each individual schematic file"""
        
        individual_analysis = {}
        
        for sch_name, sch_data in self.schematic_data.get('schematics', {}).items():
            print(f"[INGESTER] Analyzing {sch_name}...")
            
            components = sch_data.get('components', [])
            sheets = sch_data.get('sheets', [])
            
            # Filter physical components (no power symbols)
            physical_components = []
            for comp in components:
                ref = comp.get('reference', '')
                if (not ref.startswith('#') and 
                    ref and 
                    'PWR' not in ref and
                    ref not in ['GND', 'VCC', '+12V', '-12V']):
                    physical_components.append(comp)
                    self.total_analysis['unique_components'].add(ref)
            
            # Categorize components
            categories = defaultdict(list)
            for comp in physical_components:
                ref = comp.get('reference', '')
                if ref.startswith('R'):
                    categories['Resistor'].append(ref)
                elif ref.startswith('C'):
                    categories['Capacitor'].append(ref)
                elif ref.startswith('J'):
                    categories['Jack/Connector'].append(ref)
                elif ref.startswith(('U', 'OpAmp')):
                    categories['IC/OpAmp'].append(ref)
                elif ref.startswith('T'):
                    categories['Microcontroller'].append(ref)
                elif ref.startswith('DAC'):
                    categories['DAC'].append(ref)
                else:
                    categories['Other'].append(ref)
            
            individual_analysis[sch_name] = {
                'total_components': len(physical_components),
                'component_refs': [c.get('reference') for c in physical_components],
                'categories': dict(categories),
                'sheet_count': len(sheets),
                'sheets': [s.get('name', '') for s in sheets]
            }
        
        return individual_analysis
    
    def calculate_hierarchical_instances(self, individual_analysis: Dict) -> Dict[str, Any]:
        """Calculate hierarchical instances based on sheet references"""
        
        # Count sheet references
        sheet_instance_counts = defaultdict(int)
        
        for sch_name, sch_data in self.schematic_data.get('schematics', {}).items():
            sheets = sch_data.get('sheets', [])
            for sheet in sheets:
                sheet_file = sheet.get('file_path', '')
                if sheet_file:
                    sheet_instance_counts[sheet_file] += 1
        
        # Calculate total instances for each schematic
        hierarchical_totals = {}
        grand_total = 0
        
        for sch_name, analysis in individual_analysis.items():
            base_name = Path(sch_name).name
            instances = sheet_instance_counts.get(base_name, 1)
            
            base_components = analysis['total_components']
            total_instances = base_components * instances
            
            hierarchical_totals[sch_name] = {
                'base_components': base_components,
                'instance_multiplier': instances,
                'total_instances': total_instances,
                'component_refs': analysis['component_refs']
            }
            
            grand_total += total_instances
            
            print(f"[INGESTER] {sch_name}: {base_components} × {instances} = {total_instances}")
        
        hierarchical_totals['GRAND_TOTAL'] = grand_total
        return hierarchical_totals
    
    def generate_expected_pcb_components(self, hierarchical_totals: Dict) -> Set[str]:
        """Generate expected PCB component references with hierarchical naming"""
        
        expected_components = set()
        
        for sch_name, totals in hierarchical_totals.items():
            if sch_name == 'GRAND_TOTAL':
                continue
            
            base_refs = totals['component_refs']
            instances = totals['instance_multiplier']
            
            if instances == 1:
                # Single instance - use original names
                expected_components.update(base_refs)
            else:
                # Multiple instances - use hierarchical naming
                for instance in range(instances):
                    for ref in base_refs:
                        hierarchical_ref = f"{ref}_{instance + 1}"
                        expected_components.add(hierarchical_ref)
        
        return expected_components
    
    def compare_with_pcb(self, pcb_file_path: str, expected_components: Set[str]) -> Dict[str, Any]:
        """Compare expected components with actual PCB"""
        
        # Parse PCB
        sys.path.append(str(Path(__file__).parent))
        from kicad_pcb_parser import KiCadPCBParser
        
        parser = KiCadPCBParser(pcb_file_path)
        pcb_components = set(parser.components.keys())
        
        # Analysis
        common = expected_components & pcb_components
        expected_only = expected_components - pcb_components
        pcb_only = pcb_components - expected_components
        
        return {
            'expected_total': len(expected_components),
            'pcb_total': len(pcb_components),
            'common_count': len(common),
            'missing_from_pcb': len(expected_only),
            'extra_in_pcb': len(pcb_only),
            'synchronization_rate': len(common) / len(expected_components) if expected_components else 0,
            'common_sample': list(common)[:10],
            'missing_sample': list(expected_only)[:10],
            'extra_sample': list(pcb_only)[:10]
        }
    
    def run_complete_ingestion(self, schematic_summary_path: str, pcb_file_path: str) -> Dict[str, Any]:
        """Run complete fresh ingestion and analysis"""
        
        print("[INGESTER] ===== FRESH SCHEMATIC INGESTION =====")
        
        # Step 1: Load schematic data
        if not self.load_schematic_summary(schematic_summary_path):
            return {'error': 'Failed to load schematic summary'}
        
        # Step 2: Analyze individual schematics
        individual_analysis = self.analyze_individual_schematics()
        
        # Step 3: Calculate hierarchical instances
        hierarchical_totals = self.calculate_hierarchical_instances(individual_analysis)
        
        # Step 4: Generate expected PCB components
        expected_components = self.generate_expected_pcb_components(hierarchical_totals)
        
        # Step 5: Compare with PCB
        pcb_comparison = self.compare_with_pcb(pcb_file_path, expected_components)
        
        # Summary
        results = {
            'individual_schematics': individual_analysis,
            'hierarchical_analysis': hierarchical_totals,
            'expected_components_count': len(expected_components),
            'pcb_comparison': pcb_comparison,
            'unique_schematic_components': len(self.total_analysis['unique_components']),
            'summary': {
                'unique_base_components': len(self.total_analysis['unique_components']),
                'hierarchical_total': hierarchical_totals.get('GRAND_TOTAL', 0),
                'pcb_actual': pcb_comparison['pcb_total'],
                'synchronization_rate': f"{pcb_comparison['synchronization_rate']:.1%}"
            }
        }
        
        return results
    
    def generate_ingestion_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive ingestion report"""
        
        summary = results.get('summary', {})
        pcb_comp = results.get('pcb_comparison', {})
        
        report = f"""# Fresh Schematic Ingestion Report

## Component Count Summary
- **Unique Base Components**: {summary.get('unique_base_components', 0)}
- **Hierarchical Total**: {summary.get('hierarchical_total', 0)} 
- **PCB Actual Count**: {summary.get('pcb_actual', 0)}
- **Synchronization Rate**: {summary.get('synchronization_rate', '0%')}

## PCB Cross-Reference Analysis
- **Expected Components**: {pcb_comp.get('expected_total', 0)}
- **Actual PCB Components**: {pcb_comp.get('pcb_total', 0)}
- **Common Components**: {pcb_comp.get('common_count', 0)}
- **Missing from PCB**: {pcb_comp.get('missing_from_pcb', 0)}
- **Extra in PCB**: {pcb_comp.get('extra_in_pcb', 0)}

## Individual Schematic Analysis
"""
        
        individual = results.get('individual_schematics', {})
        for sch_name, analysis in individual.items():
            report += f"### {sch_name}\n"
            report += f"- Components: {analysis.get('total_components', 0)}\n"
            categories = analysis.get('categories', {})
            for cat, refs in categories.items():
                report += f"- {cat}: {len(refs)}\n"
            report += "\n"
        
        # Hierarchical breakdown
        report += "## Hierarchical Instance Analysis\n"
        hierarchical = results.get('hierarchical_analysis', {})
        for sch_name, data in hierarchical.items():
            if sch_name != 'GRAND_TOTAL':
                report += f"- **{sch_name}**: {data.get('base_components', 0)} × {data.get('instance_multiplier', 1)} = {data.get('total_instances', 0)}\n"
        
        return report

def main():
    """Main ingestion process"""
    
    ingester = FreshSchematicIngester()
    
    # Define paths
    schematic_summary = "CADfiles/MasterOfMuppets/schematic_summary.json"
    pcb_file = "CADfiles/MasterOfMuppets/MasterOfMuppets.kicad_pcb"
    
    # Run complete ingestion
    results = ingester.run_complete_ingestion(schematic_summary, pcb_file)
    
    if 'error' in results:
        print(f"[INGESTER] Error: {results['error']}")
        return
    
    # Generate report
    report = ingester.generate_ingestion_report(results)
    
    with open("fresh_schematic_ingestion_report.md", 'w') as f:
        f.write(report)
    
    print("\n[INGESTER] ===== FRESH INGESTION COMPLETE =====")
    print(f"Unique Base Components: {results['summary']['unique_base_components']}")
    print(f"Hierarchical Total: {results['summary']['hierarchical_total']}")
    print(f"PCB Actual: {results['summary']['pcb_actual']}")
    print(f"Sync Rate: {results['summary']['synchronization_rate']}")
    print(f"Report saved to: fresh_schematic_ingestion_report.md")
    
    return results

if __name__ == "__main__":
    main()