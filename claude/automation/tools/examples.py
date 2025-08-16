#!/usr/bin/env python3
"""
Example usage of KiCad Hierarchical Parser
Demonstrates various ways to use the parser for different analysis tasks
"""

import json
from pathlib import Path
from kicad_hierarchical_parser import KiCadHierarchicalParser, Component, HierarchyNode

def example_basic_parsing():
    """Basic example: Parse a KiCad project and get component count"""
    print("="*60)
    print("EXAMPLE 1: Basic Project Parsing")
    print("="*60)
    
    # Initialize parser
    parser = KiCadHierarchicalParser()
    
    # Parse project (replace with your project path)
    project_dir = Path("../CADfiles/MasterOfMuppets")
    if not project_dir.exists():
        print(f"Project directory {project_dir} not found - skipping example")
        return
    
    result = parser.parse_project(project_dir)
    
    # Display results
    summary = result['summary']
    print(f"\nRESULTS:")
    print(f"  Total components: {summary['total_components']}")
    print(f"  Hierarchy depth: {summary['hierarchy_depth']}")
    print(f"  Component types: {len(summary['component_types'])}")
    
    return result

def example_component_analysis(project_data):
    """Analyze components by type and location"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Component Analysis")
    print("="*60)
    
    if not project_data:
        print("No project data - run basic parsing first")
        return
    
    components = project_data['flattened_components']
    
    # Group components by type
    by_type = {}
    by_sheet = {}
    
    for comp in components:
        comp_type = comp['lib_id'].split(':')[0]
        sheet = Path(comp['sheet_path']).name
        
        if comp_type not in by_type:
            by_type[comp_type] = []
        by_type[comp_type].append(comp)
        
        if sheet not in by_sheet:
            by_sheet[sheet] = []
        by_sheet[sheet].append(comp)
    
    print("COMPONENTS BY TYPE:")
    for comp_type, comps in sorted(by_type.items()):
        print(f"  {comp_type}: {len(comps)} components")
        # Show first few references
        refs = [c['reference'][:20] for c in comps[:3]]
        if len(comps) > 3:
            refs.append(f"... +{len(comps)-3} more")
        print(f"    Examples: {', '.join(refs)}")
    
    print("\nCOMPONENTS BY SHEET:")
    for sheet, comps in sorted(by_sheet.items()):
        print(f"  {sheet}: {len(comps)} components")

def example_hierarchy_traversal(project_data):
    """Demonstrate hierarchy tree traversal"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Hierarchy Traversal")
    print("="*60)
    
    if not project_data or 'hierarchy' not in project_data:
        print("No hierarchy data available")
        return
    
    def print_hierarchy(node, depth=0):
        indent = "  " * depth
        print(f"{indent}[{depth}] {node['sheet_file']}")
        print(f"{indent}    Components: {node['component_count']}")
        print(f"{indent}    Instance: {node['instance_path']}")
        
        for child in node.get('children', []):
            print_hierarchy(child, depth + 1)
    
    print("HIERARCHY TREE:")
    print_hierarchy(project_data['hierarchy'])

def example_find_components():
    """Find specific components by criteria"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Component Search")
    print("="*60)
    
    # Create sample component data for demonstration
    sample_components = [
        Component("U1", "TL074", "SOIC-14", "Amplifier_Operational:TL074", "amp.kicad_sch", "/DAC#1/AMP#1/"),
        Component("C1", "100nF", "0805", "Device:C", "amp.kicad_sch", "/DAC#1/AMP#1/"),
        Component("R1", "10k", "0805", "Device:R", "amp.kicad_sch", "/DAC#1/AMP#1/"),
    ]
    
    # Search functions
    def find_by_type(components, component_type):
        return [c for c in components if component_type in c.lib_id]
    
    def find_by_sheet(components, sheet_pattern):
        return [c for c in components if sheet_pattern in c.sheet_path]
    
    def find_by_reference(components, ref_pattern):
        return [c for c in components if ref_pattern in c.reference]
    
    # Demonstrate searches
    print("SEARCH EXAMPLES:")
    
    amplifiers = find_by_type(sample_components, "Amplifier")
    print(f"  Amplifiers: {[c.reference for c in amplifiers]}")
    
    capacitors = find_by_type(sample_components, "Device:C")
    print(f"  Capacitors: {[c.reference for c in capacitors]}")
    
    amp_sheet = find_by_sheet(sample_components, "amp.kicad_sch")
    print(f"  In amp sheet: {[c.reference for c in amp_sheet]}")

def example_export_formats(project_data):
    """Show different export formats"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Export Formats")
    print("="*60)
    
    if not project_data:
        print("No project data available")
        return
    
    # Export as CSV-like format
    def export_csv_format(components):
        lines = ["Reference,Value,Footprint,LibID,Sheet,InstancePath"]
        for comp in components[:5]:  # Just first 5 for demo
            line = f"{comp['reference']},{comp['value']},{comp['footprint']},{comp['lib_id']},{Path(comp['sheet_path']).name},{comp['instance_path']}"
            lines.append(line)
        return "\n".join(lines)
    
    # Export as simple text report
    def export_text_report(project_data):
        summary = project_data['summary']
        lines = [
            f"KiCad Project Analysis Report",
            f"=" * 40,
            f"Total Components: {summary['total_components']}",
            f"Hierarchy Depth: {summary['hierarchy_depth']}",
            f"",
            f"Component Breakdown:",
        ]
        
        for comp_type, count in sorted(summary['component_types'].items()):
            lines.append(f"  {comp_type}: {count}")
        
        return "\n".join(lines)
    
    # Show exports
    print("CSV FORMAT (first 5 components):")
    if project_data.get('flattened_components'):
        csv_output = export_csv_format(project_data['flattened_components'])
        print(csv_output)
    
    print("\nTEXT REPORT FORMAT:")
    text_report = export_text_report(project_data)
    print(text_report)

def main():
    """Run all examples"""
    print("KiCad Hierarchical Parser - Usage Examples")
    print("Developed for Master of Muppets by y3i12")
    print("https://github.com/y3i12/master_of_muppets")
    
    # Run examples in sequence
    project_data = example_basic_parsing()
    example_component_analysis(project_data) 
    example_hierarchy_traversal(project_data)
    example_find_components()
    example_export_formats(project_data)
    
    print("\n" + "="*60)
    print("Examples complete! Check the output files:")
    print("  - hierarchical_analysis.json: Full project data")
    print("  - Use these patterns in your own scripts")
    print("="*60)

if __name__ == "__main__":
    main()