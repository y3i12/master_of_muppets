#!/usr/bin/env python3
"""
Schematic Component Counter v1.0 - Accurate counting of hierarchical components
Properly handles KiCad hierarchical sheets and sheet instances
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple
from collections import defaultdict

class SchematicComponentCounter:
    """Count components across hierarchical KiCad schematics"""
    
    def __init__(self, schematic_summary_path: str):
        self.schematic_path = Path(schematic_summary_path)
        self.schematic_data = None
        self.sheet_multipliers = {}
        self.component_instances = {}
        
        self._load_schematic_data()
        self._analyze_sheet_hierarchy()
    
    def _load_schematic_data(self):
        """Load schematic summary data"""
        if self.schematic_path.exists():
            with open(self.schematic_path, 'r') as f:
                self.schematic_data = json.load(f)
        else:
            raise FileNotFoundError(f"Schematic summary not found: {self.schematic_path}")
    
    def _analyze_sheet_hierarchy(self):
        """Analyze hierarchical sheets to determine instance multipliers"""
        
        print("[COUNTER] Analyzing sheet hierarchy...")
        
        # First pass: identify all sheet references and their instance counts
        sheet_references = defaultdict(int)
        
        for sch_name, sch_data in self.schematic_data.get('schematics', {}).items():
            sheets = sch_data.get('sheets', [])
            
            for sheet in sheets:
                sheet_file = sheet.get('file_path', '')
                if sheet_file:
                    sheet_references[sheet_file] += 1
                    print(f"[COUNTER] Found sheet reference: {sheet_file} (total instances: {sheet_references[sheet_file]})")
        
        # Calculate effective multipliers for each schematic
        for sch_name in self.schematic_data.get('schematics', {}):
            base_name = Path(sch_name).name
            
            # Count how many times this schematic is referenced as a sheet
            multiplier = sheet_references.get(base_name, 1)
            self.sheet_multipliers[sch_name] = multiplier
            
            print(f"[COUNTER] Sheet {sch_name}: multiplier = {multiplier}")
    
    def count_all_components(self) -> Dict[str, Any]:
        """Count all component instances across the entire schematic hierarchy"""
        
        total_count = 0
        component_breakdown = defaultdict(list)
        type_counts = defaultdict(int)
        
        for sch_name, sch_data in self.schematic_data.get('schematics', {}).items():
            components = sch_data.get('components', [])
            multiplier = self.sheet_multipliers.get(sch_name, 1)
            
            sch_physical_components = []
            
            for component in components:
                ref = component.get('reference', '')
                
                # Filter out power symbols and other non-physical components
                if (not ref.startswith('#') and 
                    ref and 
                    'PWR' not in ref and
                    ref not in ['GND', 'VCC', '+12V', '-12V']):
                    
                    sch_physical_components.append(ref)
                    
                    # Categorize component
                    component_type = self._categorize_component(ref)
                    type_counts[component_type] += multiplier
                    
                    # Record instances for this reference
                    for instance in range(multiplier):
                        if multiplier > 1:
                            instance_ref = f"{ref}_{instance+1}"
                        else:
                            instance_ref = ref
                        component_breakdown[component_type].append(instance_ref)
            
            sheet_total = len(sch_physical_components) * multiplier
            total_count += sheet_total
            
            print(f"[COUNTER] {sch_name}: {len(sch_physical_components)} components × {multiplier} instances = {sheet_total}")
        
        return {
            'total_physical_components': total_count,
            'component_breakdown': dict(component_breakdown),
            'type_counts': dict(type_counts),
            'sheet_multipliers': dict(self.sheet_multipliers),
            'analysis_summary': {
                'unique_schematics': len(self.schematic_data.get('schematics', {})),
                'total_instances': sum(self.sheet_multipliers.values()),
                'hierarchical_expansion': total_count > 50  # Indicate if hierarchy is being used
            }
        }
    
    def _categorize_component(self, reference: str) -> str:
        """Categorize component by reference designator"""
        
        if reference.startswith('U') or reference.startswith('OpAmp'):
            return 'IC/OpAmp'
        elif reference.startswith('DAC'):
            return 'DAC'
        elif reference.startswith('T'):
            return 'Microcontroller'
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
        else:
            return 'Other'
    
    def compare_with_pcb(self, pcb_component_count: int) -> Dict[str, Any]:
        """Compare schematic component count with PCB count"""
        
        sch_count = self.count_all_components()
        
        comparison = {
            'schematic_total': sch_count['total_physical_components'],
            'pcb_total': pcb_component_count,
            'difference': abs(sch_count['total_physical_components'] - pcb_component_count),
            'match_status': 'exact' if sch_count['total_physical_components'] == pcb_component_count else 'mismatch',
            'schematic_breakdown': sch_count['component_breakdown'],
            'type_counts': sch_count['type_counts']
        }
        
        if comparison['match_status'] == 'mismatch':
            if sch_count['total_physical_components'] > pcb_component_count:
                comparison['issue'] = 'schematic_has_more'
                comparison['suggestion'] = 'Some schematic components may not be placed in PCB yet'
            else:
                comparison['issue'] = 'pcb_has_more'
                comparison['suggestion'] = 'PCB may have manually added components not in schematic'
        
        return comparison
    
    def generate_component_report(self) -> str:
        """Generate a detailed component count report"""
        
        count_data = self.count_all_components()
        
        report = f"""# Schematic Component Analysis Report

## Summary
- **Total Physical Components**: {count_data['total_physical_components']}
- **Unique Schematics**: {count_data['analysis_summary']['unique_schematics']}
- **Total Sheet Instances**: {count_data['analysis_summary']['total_instances']}
- **Hierarchical Design**: {"Yes" if count_data['analysis_summary']['hierarchical_expansion'] else "No"}

## Component Breakdown by Type
"""
        
        for comp_type, count in sorted(count_data['type_counts'].items()):
            report += f"- **{comp_type}**: {count} components\n"
        
        report += "\n## Sheet Instance Multipliers\n"
        for sheet, multiplier in sorted(count_data['sheet_multipliers'].items()):
            report += f"- {sheet}: ×{multiplier}\n"
        
        if count_data['analysis_summary']['hierarchical_expansion']:
            report += "\n## Hierarchical Analysis\n"
            report += "This design uses hierarchical sheets, where component counts are multiplied by sheet instances.\n"
            report += "Example: If amp_module.kicad_sch has 20 components and is instantiated 4 times,\n"
            report += "the total contribution is 20 × 4 = 80 components.\n"
        
        return report

# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python schematic_component_counter.py <schematic_summary_json>")
        sys.exit(1)
    
    summary_file = sys.argv[1]
    counter = SchematicComponentCounter(summary_file)
    
    # Generate component count analysis
    count_data = counter.count_all_components()
    print(f"\n=== SCHEMATIC COMPONENT COUNT ANALYSIS ===")
    print(f"Total Physical Components: {count_data['total_physical_components']}")
    
    print(f"\nComponent Breakdown:")
    for comp_type, count in sorted(count_data['type_counts'].items()):
        print(f"  {comp_type}: {count}")
    
    # If PCB count provided, compare
    if len(sys.argv) > 2:
        pcb_count = int(sys.argv[2])
        comparison = counter.compare_with_pcb(pcb_count)
        
        print(f"\n=== COMPARISON WITH PCB ===")
        print(f"Schematic: {comparison['schematic_total']}")
        print(f"PCB: {comparison['pcb_total']}")
        print(f"Difference: {comparison['difference']}")
        print(f"Status: {comparison['match_status']}")
        
        if comparison['match_status'] == 'mismatch':
            print(f"Issue: {comparison['issue']}")
            print(f"Suggestion: {comparison['suggestion']}")
    
    # Generate detailed report
    report = counter.generate_component_report()
    print(f"\n{report}")