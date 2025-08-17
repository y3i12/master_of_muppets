#!/usr/bin/env python3
"""
KiCad Hierarchical Parser - Full Nested Sheet Instance Support

A comprehensive parser for KiCad schematics that correctly handles deeply nested
hierarchical sheet instances, producing accurate flattened component lists.

Developed for the Master of Muppets project by y3i12
(https://github.com/y3i12/master_of_muppets)

This tool addresses the complex challenge of KiCad hierarchical designs where
sheets can be instantiated multiple times at different levels, requiring
recursive parsing to get accurate component counts.

Author: Claude Code (Anthropic) in collaboration with y3i12
License: MIT
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
import argparse
from collections import defaultdict

@dataclass
class Component:
    """Hardware component representation"""
    reference: str
    value: str
    footprint: str
    lib_id: str
    sheet_path: str
    instance_path: str
    position: Tuple[float, float] = (0.0, 0.0)
    rotation: float = 0.0
    properties: Dict[str, str] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

@dataclass 
class SheetInstance:
    """Sheet instance in hierarchy"""
    name: str
    file_path: str
    uuid: str
    instance_path: str
    parent_path: str
    multiplicity: int = 1  # How many times this instance appears at this level

@dataclass
class HierarchyNode:
    """Node in the hierarchy tree"""
    sheet_file: str
    instance_path: str
    parent: Optional['HierarchyNode']
    children: List['HierarchyNode']
    components: List[Component]
    total_multiplicity: int = 1  # Total instances accounting for parent multiplicity

class KiCadHierarchicalParser:
    """Advanced parser supporting full hierarchical sheet nesting"""
    
    def __init__(self):
        self.sheet_templates: Dict[str, Dict] = {}  # Cache of parsed sheet files
        self.hierarchy_tree: Optional[HierarchyNode] = None
        self.flattened_components: List[Component] = []
        
    def parse_project(self, project_dir: Path) -> Dict[str, Any]:
        """Parse entire KiCad project with full hierarchical support"""
        
        print(f"[*] KiCad Hierarchical Parser")
        print(f"[+] Project: {project_dir}")
        print(f"[*] Developed for Master of Muppets by y3i12")
        print(f"[+] https://github.com/y3i12/master_of_muppets")
        print("-" * 60)
        
        project_data = {
            'metadata': {
                'project_path': str(project_dir),
                'version': '2.0.0',
                'parser': 'kicad_hierarchical_parser.py',
                'author': 'Claude Code (Anthropic) + y3i12',
                'project_reference': 'Master of Muppets - y3i12'
            },
            'schematics': {},
            'hierarchy': {},
            'flattened_components': [],
            'summary': {
                'total_components': 0,
                'component_types': {},
                'hierarchy_depth': 0,
                'total_instances': {},
                'sheet_multiplicity': {}
            }
        }
        
        # Phase 1: Parse all schematic files into templates
        print("[1] Phase 1: Parsing schematic templates...")
        sch_files = list(project_dir.glob('*.kicad_sch'))
        
        for sch_file in sch_files:
            print(f"  [+] {sch_file.name}")
            template = self._parse_schematic_template(sch_file)
            if template:
                self.sheet_templates[sch_file.name] = template
                project_data['schematics'][sch_file.name] = template
        
        # Phase 2: Build hierarchy tree
        print("\n[2] Phase 2: Building hierarchy tree...")
        main_schematic = self._find_main_schematic()
        if main_schematic:
            self.hierarchy_tree = self._build_hierarchy_tree(main_schematic, "/")
            project_data['hierarchy'] = self._serialize_hierarchy(self.hierarchy_tree)
        
        # Phase 3: Flatten all component instances
        print("\n[3] Phase 3: Flattening component instances...")
        if self.hierarchy_tree:
            self._flatten_hierarchy(self.hierarchy_tree, project_data)
        
        # Phase 4: Generate summary statistics
        print("\n[4] Phase 4: Generating summary...")
        self._generate_summary(project_data)
        
        print(f"\n[OK] Parsing complete!")
        print(f"   [*] Total components: {project_data['summary']['total_components']}")
        print(f"   [*] Sheet templates: {len(self.sheet_templates)}")
        print(f"   [*] Max hierarchy depth: {project_data['summary']['hierarchy_depth']}")
        
        return project_data
    
    def _parse_schematic_template(self, file_path: Path) -> Dict[str, Any]:
        """Parse a single schematic file as a template"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            template = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'components': [],
                'sheets': []
            }
            
            # Extract components using regex (non-power symbols with lib_id)
            components = self._extract_components_regex(content, str(file_path))
            template['components'] = [asdict(comp) for comp in components]
            
            # Extract hierarchical sheet references
            sheets = self._extract_sheets_regex(content)
            template['sheets'] = [asdict(sheet) for sheet in sheets]
            
            return template
            
        except Exception as e:
            print(f"[!] Error parsing {file_path}: {e}")
            return {}
    
    def _extract_components_regex(self, content: str, sheet_path: str) -> List[Component]:
        """Extract components using simple regex approach"""
        components = []
        
        # Find all (symbol blocks that contain lib_id
        # Use a simple approach: find each (symbol then look for its properties
        symbol_start_pattern = r'\(symbol\s*\n'
        symbol_positions = [m.start() for m in re.finditer(symbol_start_pattern, content)]
        
        for i, start_pos in enumerate(symbol_positions):
            # Find the end of this symbol block (next symbol or end of file)
            if i + 1 < len(symbol_positions):
                end_pos = symbol_positions[i + 1]
            else:
                end_pos = len(content)
            
            symbol_block = content[start_pos:end_pos]
            
            # Extract lib_id
            lib_id_match = re.search(r'\(lib_id\s+"([^"]+)"\)', symbol_block)
            if not lib_id_match:
                continue
            
            lib_id = lib_id_match.group(1)
            
            # Skip power symbols - they're not physical components
            if lib_id.startswith('power:'):
                continue
            
            # Extract component properties using simple regex
            reference = ""
            value = ""
            footprint = ""
            
            ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', symbol_block)
            if ref_match:
                reference = ref_match.group(1)
            
            val_match = re.search(r'\(property\s+"Value"\s+"([^"]+)"', symbol_block)
            if val_match:
                value = val_match.group(1)
            
            fp_match = re.search(r'\(property\s+"Footprint"\s+"([^"]+)"', symbol_block)
            if fp_match:
                footprint = fp_match.group(1)
            
            # Skip power reference designators (#PWR)
            if reference.startswith('#PWR'):
                continue
            
            # Extract position
            position = (0.0, 0.0)
            rotation = 0.0
            at_match = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?\)', symbol_block)
            if at_match:
                try:
                    position = (float(at_match.group(1)), float(at_match.group(2)))
                    if at_match.group(3):
                        rotation = float(at_match.group(3))
                except ValueError:
                    pass
            
            # Only add if we have a valid reference
            if reference and lib_id:
                component = Component(
                    reference=reference,
                    value=value,
                    footprint=footprint,
                    lib_id=lib_id,
                    sheet_path=sheet_path,
                    instance_path="",
                    position=position,
                    rotation=rotation,
                    properties={}  # Simplified for now
                )
                components.append(component)
        
        return components
    
    def _extract_sheets_regex(self, content: str) -> List[SheetInstance]:
        """Extract hierarchical sheet references using simple regex"""
        sheets = []
        
        # Use the same approach that worked in our count_instances.py script
        # Find all "Sheetfile" property entries - this is much more reliable!
        sheetfile_pattern = r'\(property\s+"Sheetfile"\s+"([^"]+)"\)'
        sheetfile_matches = re.findall(sheetfile_pattern, content)
        
        # For each Sheetfile, we need to find the corresponding Sheetname
        # Look for complete sheet blocks using a different approach
        sheet_start_pattern = r'\(sheet\s*\n'
        sheet_positions = [m.start() for m in re.finditer(sheet_start_pattern, content)]
        
        sheet_counter = {}  # Track multiple instances of same sheet file
        
        for i, start_pos in enumerate(sheet_positions):
            # Find the end of this sheet block
            if i + 1 < len(sheet_positions):
                end_pos = sheet_positions[i + 1]
            else:
                # Find next top-level closing or end of file
                end_pos = len(content)
            
            sheet_block = content[start_pos:end_pos]
            
            # Extract UUID
            uuid_match = re.search(r'\(uuid\s+"([^"]+)"\)', sheet_block)
            uuid = uuid_match.group(1) if uuid_match else ""
            
            # Extract Sheetname and Sheetfile using simple regex
            sheetname_match = re.search(r'\(property\s+"Sheetname"\s+"([^"]+)"', sheet_block)
            sheetfile_match = re.search(r'\(property\s+"Sheetfile"\s+"([^"]+)"', sheet_block)
            
            if sheetname_match and sheetfile_match:
                sheetname = sheetname_match.group(1)
                sheetfile = sheetfile_match.group(1)
                
                # Track instances of same sheet file
                if sheetfile not in sheet_counter:
                    sheet_counter[sheetfile] = 0
                sheet_counter[sheetfile] += 1
                
                sheet = SheetInstance(
                    name=sheetname,
                    file_path=sheetfile,
                    uuid=uuid,
                    instance_path="",  # Will be set during hierarchy processing
                    parent_path="",
                    multiplicity=sheet_counter[sheetfile]
                )
                sheets.append(sheet)
        
        return sheets
    
    def _extract_property_value(self, text: str, property_name: str) -> Optional[str]:
        """Extract a specific property value from text"""
        pattern = rf'\(property\s+"{property_name}"\s+"([^"]+)"'
        match = re.search(pattern, text)
        return match.group(1) if match else None
    
    def _extract_all_properties(self, text: str) -> Dict[str, str]:
        """Extract all properties from a symbol block"""
        properties = {}
        property_pattern = r'\(property\s+"([^"]+)"\s+"([^"]+)"'
        for match in re.finditer(property_pattern, text):
            prop_name = match.group(1)
            prop_value = match.group(2)
            properties[prop_name] = prop_value
        return properties
    
    def _find_main_schematic(self) -> Optional[str]:
        """Find the main schematic file (root of hierarchy)"""
        # Look for schematic that contains sheet references but isn't referenced by others
        referenced_files = set()
        files_with_sheets = []
        
        for file_name, template in self.sheet_templates.items():
            sheets = template.get('sheets', [])
            if sheets:
                files_with_sheets.append(file_name)
                for sheet in sheets:
                    referenced_files.add(sheet['file_path'])
        
        # Main schematic has sheets but isn't referenced by others
        for file_name in files_with_sheets:
            if file_name not in referenced_files:
                print(f"  [M] Main schematic: {file_name}")
                return file_name
        
        # Fallback: use filename heuristics
        for file_name in self.sheet_templates.keys():
            if 'main' in file_name.lower() or 'master' in file_name.lower():
                print(f"  [M] Main schematic (heuristic): {file_name}")
                return file_name
        
        print(f"  [!] Could not identify main schematic")
        return None
    
    def _build_hierarchy_tree(self, sheet_file: str, instance_path: str, 
                            parent: Optional[HierarchyNode] = None, depth: int = 0) -> HierarchyNode:
        """Recursively build the hierarchy tree"""
        
        if depth > 10:  # Prevent infinite recursion
            print(f"  [!] Maximum hierarchy depth reached for {sheet_file}")
            return None
        
        template = self.sheet_templates.get(sheet_file, {})
        
        # Create node for this sheet
        node = HierarchyNode(
            sheet_file=sheet_file,
            instance_path=instance_path,
            parent=parent,
            children=[],
            components=[],
            total_multiplicity=1
        )
        
        # Add components from this sheet
        for comp_data in template.get('components', []):
            comp = Component(**comp_data)
            comp.instance_path = instance_path
            node.components.append(comp)
        
        print(f"  {'  ' * depth}[S] {sheet_file} @ {instance_path} ({len(node.components)} components)")
        
        # Process child sheets
        sheets = template.get('sheets', [])
        if sheets:
            # Group sheets by file to handle multiple instances
            sheet_files = defaultdict(list)
            for sheet in sheets:
                sheet_files[sheet['file_path']].append(sheet)
            
            for child_sheet_file, instances in sheet_files.items():
                print(f"  {'  ' * depth}  [+] {child_sheet_file}: {len(instances)} instances")
                
                for i, sheet_data in enumerate(instances, 1):
                    child_instance_path = f"{instance_path}{sheet_data['name']}#{i}/"
                    
                    # Recursively build child tree
                    child_node = self._build_hierarchy_tree(
                        child_sheet_file, child_instance_path, node, depth + 1
                    )
                    
                    if child_node:
                        node.children.append(child_node)
        
        return node
    
    def _flatten_hierarchy(self, node: HierarchyNode, project_data: Dict, 
                         parent_multiplicity: int = 1):
        """Flatten the hierarchy tree into a component list"""
        
        current_multiplicity = parent_multiplicity
        
        # Add components from this node
        for comp in node.components:
            for instance in range(current_multiplicity):
                # Create unique component instance
                comp_instance = Component(
                    reference=f"{comp.reference}_{node.instance_path.replace('/', '_')}_{instance+1}",
                    value=comp.value,
                    footprint=comp.footprint,
                    lib_id=comp.lib_id,
                    sheet_path=comp.sheet_path,
                    instance_path=f"{node.instance_path}[{instance+1}]",
                    position=comp.position,
                    rotation=comp.rotation,
                    properties=comp.properties.copy()
                )
                
                self.flattened_components.append(comp_instance)
                project_data['flattened_components'].append(asdict(comp_instance))
        
        # Recursively process children
        for child in node.children:
            self._flatten_hierarchy(child, project_data, current_multiplicity)
    
    def _serialize_hierarchy(self, node: HierarchyNode) -> Dict:
        """Convert hierarchy tree to serializable format"""
        return {
            'sheet_file': node.sheet_file,
            'instance_path': node.instance_path,
            'component_count': len(node.components),
            'total_multiplicity': node.total_multiplicity,
            'children': [self._serialize_hierarchy(child) for child in node.children]
        }
    
    def _generate_summary(self, project_data: Dict):
        """Generate comprehensive summary statistics"""
        summary = project_data['summary']
        
        # Count components by type
        component_types = defaultdict(int)
        sheet_instances = defaultdict(int)
        
        for comp in project_data['flattened_components']:
            lib_id = comp.get('lib_id', 'unknown')
            comp_type = lib_id.split(':')[0] if ':' in lib_id else lib_id
            component_types[comp_type] += 1
            
            # Count instances per sheet
            sheet_path = comp.get('sheet_path', 'unknown')
            sheet_name = Path(sheet_path).name if sheet_path else 'unknown'
            sheet_instances[sheet_name] += 1
        
        summary['total_components'] = len(project_data['flattened_components'])
        summary['component_types'] = dict(component_types)
        summary['total_instances'] = dict(sheet_instances)
        
        # Calculate hierarchy depth
        def calc_depth(node_data):
            if not node_data.get('children'):
                return 1
            return 1 + max(calc_depth(child) for child in node_data['children'])
        
        if project_data.get('hierarchy'):
            summary['hierarchy_depth'] = calc_depth(project_data['hierarchy'])

def main():
    parser = argparse.ArgumentParser(
        description='KiCad Hierarchical Parser - Full nested sheet support',
        epilog='Developed for Master of Muppets project by y3i12 (https://github.com/y3i12/master_of_muppets)'
    )
    parser.add_argument('project_dir', type=Path, help='Path to KiCad project directory')
    parser.add_argument('-o', '--output', type=Path, help='Output JSON file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--validate', action='store_true', help='Validate component count expectations')
    
    args = parser.parse_args()
    
    if not args.project_dir.exists():
        print(f"[!] Error: Project directory {args.project_dir} does not exist")
        sys.exit(1)
    
    output_file = args.output or args.project_dir / 'hierarchical_analysis.json'
    
    # Parse the project
    hierarchical_parser = KiCadHierarchicalParser()
    project_data = hierarchical_parser.parse_project(args.project_dir)
    
    # Display results
    if args.verbose or True:  # Always show summary
        print("\n" + "="*60)
        print("[=] ANALYSIS SUMMARY")
        print("="*60)
        print(f"Total components: {project_data['summary']['total_components']}")
        print(f"Hierarchy depth: {project_data['summary']['hierarchy_depth']}")
        print("\nComponent types:")
        for comp_type, count in sorted(project_data['summary']['component_types'].items()):
            print(f"  {comp_type}: {count}")
        print("\nSheet instances:")
        for sheet, count in sorted(project_data['summary']['total_instances'].items()):
            print(f"  {sheet}: {count}")
    
    # Validation for Master of Muppets
    if args.validate:
        expected = 163  # Based on our analysis
        actual = project_data['summary']['total_components']
        print(f"\n[V] Validation:")
        print(f"  Expected: {expected} components")
        print(f"  Actual: {actual} components")
        if actual == expected:
            print(f"  [OK] PASS - Component count matches!")
        else:
            print(f"  [X] FAIL - Component count mismatch!")
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[S] Results saved to {output_file}")
    print(f"[OK] Analysis complete!")

if __name__ == '__main__':
    main()