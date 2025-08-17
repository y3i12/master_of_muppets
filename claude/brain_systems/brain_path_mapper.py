#!/usr/bin/env python3
"""
Brain Path Mapper v1.0 - Self-organizing file location intelligence
Auto-discovers and maintains mapping of cognitive system files
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class BrainPathMapper:
    """Intelligent path mapping and discovery system"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.brain_map = {}
        self.search_patterns = {
            'cognitive_cache': ['cognitive_cache.cc', 'cache.cc'],
            'cognitive_core': ['cognitive_core.json', 'core.json'],
            'cognitive_ops': ['cognitive_ops.py', 'ops.py'],
            'brain_systems': ['brain_systems/', 'systems/'],
            'sessions': ['sessions/', 'episodes/'],
            'tools': ['tools/', 'utilities/'],
            'data_stores': ['data_stores/', 'data/', 'stores/'],
            'hardware_graph': ['hardware_graph/', 'hw_graph/'],
            'codebase_graph': ['codebase_graph/', 'code_graph/']
        }
        
    def discover_brain_files(self) -> Dict[str, str]:
        """Auto-discover all brain system files"""
        discovered = {}
        
        print("[BRAIN_MAPPER] Starting brain file discovery...")
        
        # Search claude/ directory tree
        claude_dir = self.project_root / 'claude'
        if not claude_dir.exists():
            print(f"[BRAIN_MAPPER] Warning: claude/ directory not found at {claude_dir}")
            return discovered
            
        # Recursive search for brain files
        for root, dirs, files in os.walk(claude_dir):
            root_path = Path(root)
            
            for file in files:
                file_path = root_path / file
                relative_path = file_path.relative_to(self.project_root)
                
                # Match against known patterns
                for brain_type, patterns in self.search_patterns.items():
                    for pattern in patterns:
                        if pattern in str(file_path).lower():
                            if brain_type not in discovered:
                                discovered[brain_type] = []
                            discovered[brain_type].append(str(relative_path))
                            
        # Convert lists to single paths for unique files
        for brain_type in discovered:
            if brain_type in ['cognitive_cache', 'cognitive_core', 'cognitive_ops']:
                # These should be single files
                if len(discovered[brain_type]) == 1:
                    discovered[brain_type] = discovered[brain_type][0]
                else:
                    # Pick the most likely candidate
                    discovered[brain_type] = self._pick_best_candidate(discovered[brain_type], brain_type)
                    
        return discovered
        
    def _pick_best_candidate(self, candidates: List[str], brain_type: str) -> str:
        """Pick the best candidate from multiple matches"""
        # Prefer files in brain_systems/ directory
        brain_systems_candidates = [c for c in candidates if 'brain_systems' in c]
        if brain_systems_candidates:
            return brain_systems_candidates[0]
        return candidates[0]
        
    def create_path_index(self) -> Dict[str, any]:
        """Create comprehensive path index"""
        index = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'brain_files': self.discover_brain_files(),
            'search_stats': {},
            'patterns_learned': []
        }
        
        # Add search statistics
        for brain_type, paths in index['brain_files'].items():
            if isinstance(paths, list):
                index['search_stats'][brain_type] = len(paths)
            else:
                index['search_stats'][brain_type] = 1
                
        return index
        
    def save_brain_index(self, index_path: str = None) -> str:
        """Save brain index to file"""
        if not index_path:
            index_path = self.project_root / 'claude' / 'brain_systems' / 'brain_path_index.json'
            
        index = self.create_path_index()
        
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
            
        print(f"[BRAIN_MAPPER] Brain index saved to: {index_path}")
        return str(index_path)
        
    def load_brain_index(self, index_path: str = None) -> Optional[Dict]:
        """Load existing brain index"""
        if not index_path:
            index_path = self.project_root / 'claude' / 'brain_systems' / 'brain_path_index.json'
            
        if not os.path.exists(index_path):
            return None
            
        with open(index_path, 'r') as f:
            return json.load(f)
            
    def get_file_path(self, brain_type: str) -> Optional[str]:
        """Get absolute path for a brain file type"""
        index = self.load_brain_index()
        if not index:
            # Create new index
            self.save_brain_index()
            index = self.load_brain_index()
            
        brain_files = index.get('brain_files', {})
        relative_path = brain_files.get(brain_type)
        
        if not relative_path:
            return None
            
        if isinstance(relative_path, list):
            relative_path = relative_path[0]
            
        return str(self.project_root / relative_path)
        
    def validate_paths(self) -> Dict[str, bool]:
        """Validate all mapped paths exist"""
        index = self.load_brain_index()
        if not index:
            return {}
            
        validation = {}
        brain_files = index.get('brain_files', {})
        
        for brain_type, path in brain_files.items():
            if isinstance(path, list):
                validation[brain_type] = [os.path.exists(self.project_root / p) for p in path]
            else:
                validation[brain_type] = os.path.exists(self.project_root / path)
                
        return validation
        
    def learn_from_access_pattern(self, requested_file: str, actual_path: str):
        """Learn from file access patterns to improve mapping"""
        index = self.load_brain_index()
        if not index:
            index = self.create_path_index()
            
        # Add to learned patterns
        pattern = {
            'requested': requested_file,
            'resolved': actual_path,
            'timestamp': datetime.now().isoformat()
        }
        
        if 'patterns_learned' not in index:
            index['patterns_learned'] = []
            
        index['patterns_learned'].append(pattern)
        
        # Save updated index
        index_path = self.project_root / 'claude' / 'brain_systems' / 'brain_path_index.json'
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
            
        print(f"[BRAIN_MAPPER] Learned pattern: {requested_file} -> {actual_path}")
        
    def auto_resolve_path(self, partial_name: str) -> Optional[str]:
        """Auto-resolve partial file names to full paths"""
        index = self.load_brain_index()
        if not index:
            return None
            
        brain_files = index.get('brain_files', {})
        
        # Direct match
        if partial_name in brain_files:
            path = brain_files[partial_name]
            if isinstance(path, list):
                path = path[0]
            return str(self.project_root / path)
            
        # Fuzzy match
        for brain_type, path in brain_files.items():
            if partial_name.lower() in brain_type.lower():
                if isinstance(path, list):
                    path = path[0]
                return str(self.project_root / path)
                
        return None
        
    def generate_brain_map_report(self) -> str:
        """Generate comprehensive brain mapping report"""
        index = self.load_brain_index()
        if not index:
            return "No brain index found"
            
        validation = self.validate_paths()
        
        report = f"""# Brain Path Mapping Report
Generated: {index.get('timestamp', 'Unknown')}
Project Root: {index.get('project_root', 'Unknown')}

## Discovered Brain Files
"""
        
        brain_files = index.get('brain_files', {})
        for brain_type, path in brain_files.items():
            status = "[OK]" if validation.get(brain_type, False) else "[MISSING]"
            if isinstance(path, list):
                report += f"- **{brain_type}**: {len(path)} files {status}\n"
                for p in path[:3]:  # Show first 3
                    report += f"  - {p}\n"
                if len(path) > 3:
                    report += f"  - ... and {len(path) - 3} more\n"
            else:
                report += f"- **{brain_type}**: {path} {status}\n"
                
        # Search statistics
        stats = index.get('search_stats', {})
        if stats:
            report += "\n## Search Statistics\n"
            for brain_type, count in stats.items():
                report += f"- {brain_type}: {count} matches\n"
                
        # Learned patterns
        patterns = index.get('patterns_learned', [])
        if patterns:
            report += f"\n## Learned Patterns ({len(patterns)})\n"
            for pattern in patterns[-5:]:  # Show last 5
                report += f"- {pattern['requested']} -> {pattern['resolved']}\n"
                
        return report

def main():
    """Run brain path mapping"""
    mapper = BrainPathMapper()
    
    print("[BRAIN_MAPPER] ===== BRAIN PATH DISCOVERY =====")
    
    # Create and save brain index
    index_path = mapper.save_brain_index()
    
    # Validate paths
    validation = mapper.validate_paths()
    
    # Generate report
    report = mapper.generate_brain_map_report()
    
    # Save report
    report_path = mapper.project_root / 'brain_path_mapping_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"[BRAIN_MAPPER] Report saved to: {report_path}")
    print(f"[BRAIN_MAPPER] Index saved to: {index_path}")
    
    # Test auto-resolution
    test_files = ['cognitive_cache', 'cognitive_core', 'cognitive_ops']
    print("\n[BRAIN_MAPPER] Testing auto-resolution:")
    for test_file in test_files:
        resolved = mapper.auto_resolve_path(test_file)
        print(f"- {test_file} -> {resolved}")
        
    return mapper

if __name__ == "__main__":
    main()