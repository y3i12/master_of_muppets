#!/usr/bin/env python3
"""
PCB Data Organizer v1.0 - Assimilate and organize PCB analysis data
Consolidates multiple PCB analysis JSON files into organized brain systems
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class PCBDataOrganizer:
    """Organize and consolidate PCB analysis data"""
    
    def __init__(self):
        self.consolidated_data = {
            'metadata': {
                'version': '1.0.0',
                'consolidated_at': datetime.now().isoformat(),
                'source_files': []
            },
            'board_info': {},
            'component_analysis': {},
            'placement_analysis': {},
            'optimization_results': {},
            'constraints': [],
            'performance_metrics': {}
        }
    
    def load_and_analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Load and analyze a single JSON file"""
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        file_name = Path(file_path).name
        self.consolidated_data['metadata']['source_files'].append({
            'file': file_name,
            'size_kb': Path(file_path).stat().st_size / 1024,
            'loaded_at': datetime.now().isoformat()
        })
        
        return data
    
    def consolidate_placement_analysis(self, data: Dict[str, Any]) -> None:
        """Consolidate placement analysis data"""
        
        if 'board_info' in data:
            self.consolidated_data['board_info'].update(data['board_info'])
        
        if 'components' in data:
            # Count components by type
            component_counts = {}
            component_positions = {}
            
            for ref, comp_data in data['components'].items():
                # Categorize component
                if ref.startswith('T'):
                    comp_type = 'microcontroller'
                elif ref.startswith('DAC'):
                    comp_type = 'dac'
                elif ref.startswith(('U', 'OpAmp')):
                    comp_type = 'opamp'
                elif ref.startswith('J'):
                    comp_type = 'jack'
                elif ref.startswith('R'):
                    comp_type = 'resistor'
                elif ref.startswith('C'):
                    comp_type = 'capacitor'
                else:
                    comp_type = 'other'
                
                component_counts[comp_type] = component_counts.get(comp_type, 0) + 1
                
                # Store position data
                component_positions[ref] = {
                    'x': comp_data.get('x', 0),
                    'y': comp_data.get('y', 0),
                    'rotation': comp_data.get('rotation', 0),
                    'footprint': comp_data.get('footprint', ''),
                    'type': comp_type
                }
            
            self.consolidated_data['component_analysis'] = {
                'component_counts': component_counts,
                'total_components': sum(component_counts.values()),
                'component_positions': component_positions
            }
        
        if 'placement_violations' in data:
            self.consolidated_data['placement_analysis']['violations'] = data['placement_violations']
        
        if 'signal_integrity_analysis' in data:
            self.consolidated_data['placement_analysis']['signal_integrity'] = data['signal_integrity_analysis']
    
    def consolidate_optimization_report(self, data: Dict[str, Any]) -> None:
        """Consolidate optimization results"""
        
        if 'optimization_summary' in data:
            self.consolidated_data['optimization_results'] = data['optimization_summary']
        
        if 'constraints' in data:
            self.consolidated_data['constraints'] = data['constraints']
        
        if 'zones' in data:
            self.consolidated_data['placement_analysis']['zones'] = data['zones']
        
        if 'component_moves' in data:
            self.consolidated_data['optimization_results']['component_moves'] = data['component_moves']
    
    def consolidate_complete_analysis(self, data: Dict[str, Any]) -> None:
        """Consolidate complete analysis data"""
        
        # Update board info
        if 'board_info' in data:
            self.consolidated_data['board_info'].update(data['board_info'])
        
        # Merge component analysis
        if 'component_analysis' in data:
            if 'component_analysis' not in self.consolidated_data:
                self.consolidated_data['component_analysis'] = {}
            self.consolidated_data['component_analysis'].update(data['component_analysis'])
        
        # Add any thermal analysis
        if 'thermal_analysis' in data:
            self.consolidated_data['placement_analysis']['thermal'] = data['thermal_analysis']
        
        # Add routing analysis
        if 'routing_analysis' in data:
            self.consolidated_data['placement_analysis']['routing'] = data['routing_analysis']
        
        # Performance metrics
        if 'performance_metrics' in data:
            self.consolidated_data['performance_metrics'].update(data['performance_metrics'])
    
    def analyze_data_quality(self) -> Dict[str, Any]:
        """Analyze the quality and completeness of consolidated data"""
        
        quality_report = {
            'completeness_score': 0.0,
            'data_coverage': {},
            'issues': [],
            'recommendations': []
        }
        
        # Check data coverage
        sections = ['board_info', 'component_analysis', 'placement_analysis', 'optimization_results']
        coverage_count = 0
        
        for section in sections:
            has_data = bool(self.consolidated_data.get(section))
            quality_report['data_coverage'][section] = has_data
            if has_data:
                coverage_count += 1
        
        quality_report['completeness_score'] = coverage_count / len(sections)
        
        # Identify issues
        total_components = self.consolidated_data.get('component_analysis', {}).get('total_components', 0)
        if total_components == 0:
            quality_report['issues'].append("No component data found")
        elif total_components < 100:
            quality_report['issues'].append(f"Low component count: {total_components}")
        
        if not self.consolidated_data.get('constraints'):
            quality_report['issues'].append("No design constraints found")
        
        # Generate recommendations
        if quality_report['completeness_score'] < 0.8:
            quality_report['recommendations'].append("Consider running additional analysis passes")
        
        if 'signal_integrity' not in self.consolidated_data.get('placement_analysis', {}):
            quality_report['recommendations'].append("Run signal integrity analysis")
        
        return quality_report
    
    def generate_summary_report(self) -> str:
        """Generate a human-readable summary of consolidated data"""
        
        component_analysis = self.consolidated_data.get('component_analysis', {})
        board_info = self.consolidated_data.get('board_info', {})
        optimization = self.consolidated_data.get('optimization_results', {})
        
        report = f"""# Master of Muppets PCB Data Consolidation Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Board Information
- **Size**: {board_info.get('size', [0, 0])[0]}mm × {board_info.get('size', [0, 0])[1]}mm
- **Thickness**: {board_info.get('thickness', 'Unknown')}mm
- **Layer Count**: {board_info.get('layer_count', 'Unknown')}

## Component Analysis
- **Total Components**: {component_analysis.get('total_components', 0)}
"""
        
        # Component breakdown
        component_counts = component_analysis.get('component_counts', {})
        for comp_type, count in sorted(component_counts.items()):
            report += f"- **{comp_type.title()}s**: {count}\n"
        
        # Optimization results
        if optimization:
            report += f"\n## Optimization Results\n"
            report += f"- **Original Score**: {optimization.get('original_score', 0):.4f}\n"
            report += f"- **Optimized Score**: {optimization.get('optimized_score', 0):.4f}\n"
            report += f"- **Improvement**: {optimization.get('improvement_percent', 0):.2f}%\n"
        
        # Constraints
        constraints = self.consolidated_data.get('constraints', [])
        if constraints:
            report += f"\n## Design Constraints\n"
            report += f"- **Total Constraints**: {len(constraints)}\n"
            
            # Group by priority
            high_priority = [c for c in constraints if c.get('priority', 0) >= 8]
            report += f"- **High Priority Constraints**: {len(high_priority)}\n"
        
        # Data sources
        source_files = self.consolidated_data['metadata']['source_files']
        report += f"\n## Data Sources\n"
        for source in source_files:
            report += f"- **{source['file']}**: {source['size_kb']:.1f} KB\n"
        
        return report
    
    def save_consolidated_data(self, output_dir: str = "claude/brain_systems") -> str:
        """Save consolidated data to brain systems"""
        
        output_path = Path(output_dir) / "pcb_analysis_consolidated.json"
        
        with open(output_path, 'w') as f:
            json.dump(self.consolidated_data, f, indent=2)
        
        return str(output_path)
    
    def cleanup_source_files(self, file_paths: List[str]) -> None:
        """Clean up original source files after consolidation"""
        
        for file_path in file_paths:
            try:
                Path(file_path).unlink()
                print(f"[ORGANIZER] Removed: {Path(file_path).name}")
            except Exception as e:
                print(f"[ORGANIZER] Warning: Could not remove {file_path}: {e}")

def main():
    """Main consolidation process"""
    
    organizer = PCBDataOrganizer()
    
    # Define source files
    source_files = [
        "MasterOfMuppets_placement_analysis.json",
        "MasterOfMuppets_optimization_report.json", 
        "MasterOfMuppets_complete_analysis.json"
    ]
    
    print("[ORGANIZER] Starting PCB data consolidation...")
    
    # Load and process each file
    for file_path in source_files:
        if Path(file_path).exists():
            print(f"[ORGANIZER] Processing: {file_path}")
            data = organizer.load_and_analyze_file(file_path)
            
            if "placement_analysis" in file_path:
                organizer.consolidate_placement_analysis(data)
            elif "optimization_report" in file_path:
                organizer.consolidate_optimization_report(data)
            elif "complete_analysis" in file_path:
                organizer.consolidate_complete_analysis(data)
        else:
            print(f"[ORGANIZER] Warning: {file_path} not found")
    
    # Analyze data quality
    quality_report = organizer.analyze_data_quality()
    print(f"[ORGANIZER] Data completeness: {quality_report['completeness_score']:.1%}")
    
    # Save consolidated data
    output_path = organizer.save_consolidated_data()
    print(f"[ORGANIZER] Consolidated data saved to: {output_path}")
    
    # Generate summary report
    summary = organizer.generate_summary_report()
    with open("pcb_consolidation_summary.md", 'w') as f:
        f.write(summary)
    print("[ORGANIZER] Summary report saved to: pcb_consolidation_summary.md")
    
    # Clean up source files
    existing_files = [f for f in source_files if Path(f).exists()]
    if existing_files:
        print(f"[ORGANIZER] Cleaning up {len(existing_files)} source files...")
        organizer.cleanup_source_files(existing_files)
    
    print("[ORGANIZER] PCB data consolidation complete!")
    
    return {
        'consolidated_file': output_path,
        'summary_report': "pcb_consolidation_summary.md",
        'quality_score': quality_report['completeness_score'],
        'total_components': organizer.consolidated_data.get('component_analysis', {}).get('total_components', 0)
    }

if __name__ == "__main__":
    result = main()
    print(f"\n=== CONSOLIDATION RESULTS ===")
    print(f"Total Components: {result['total_components']}")
    print(f"Data Quality: {result['quality_score']:.1%}")
    print(f"Files Generated:")
    print(f"  - {result['consolidated_file']}")
    print(f"  - {result['summary_report']}")