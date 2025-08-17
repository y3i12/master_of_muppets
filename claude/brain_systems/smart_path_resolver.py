#!/usr/bin/env python3
"""
Smart Path Resolver v1.0 - Intelligent file path resolution with learning
Auto-corrects path mistakes and learns from usage patterns
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from brain_path_mapper import BrainPathMapper

class SmartPathResolver:
    """Intelligent path resolver with pattern learning"""
    
    def __init__(self, project_root: str = None):
        self.mapper = BrainPathMapper(project_root)
        self.learning_file = self.mapper.project_root / 'claude' / 'brain_systems' / 'path_learning.json'
        self.load_learning_data()
        
    def load_learning_data(self):
        """Load existing learning data"""
        if self.learning_file.exists():
            with open(self.learning_file, 'r') as f:
                self.learning_data = json.load(f)
        else:
            self.learning_data = {
                'failed_attempts': [],
                'successful_resolutions': [],
                'common_mistakes': {},
                'auto_corrections': {}
            }
            
    def save_learning_data(self):
        """Save learning data"""
        os.makedirs(os.path.dirname(self.learning_file), exist_ok=True)
        with open(self.learning_file, 'w') as f:
            json.dump(self.learning_data, f, indent=2)
            
    def record_failed_attempt(self, attempted_path: str, context: str = ""):
        """Record a failed path attempt for learning"""
        failure = {
            'path': attempted_path,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        self.learning_data['failed_attempts'].append(failure)
        
        # Learn common mistakes
        mistake_key = self._extract_mistake_pattern(attempted_path)
        if mistake_key:
            if mistake_key not in self.learning_data['common_mistakes']:
                self.learning_data['common_mistakes'][mistake_key] = 0
            self.learning_data['common_mistakes'][mistake_key] += 1
            
        self.save_learning_data()
        print(f"[PATH_RESOLVER] Recorded failed attempt: {attempted_path}")
        
    def record_successful_resolution(self, original_path: str, resolved_path: str):
        """Record successful path resolution"""
        success = {
            'original': original_path,
            'resolved': resolved_path,
            'timestamp': datetime.now().isoformat()
        }
        self.learning_data['successful_resolutions'].append(success)
        
        # Create auto-correction rule
        correction_key = self._create_correction_key(original_path, resolved_path)
        if correction_key:
            self.learning_data['auto_corrections'][correction_key] = resolved_path
            
        self.save_learning_data()
        print(f"[PATH_RESOLVER] Learned correction: {original_path} -> {resolved_path}")
        
    def _extract_mistake_pattern(self, path: str) -> Optional[str]:
        """Extract common mistake patterns from failed paths"""
        # Common mistakes
        if path.startswith('claude/cognitive_cache.cc'):
            return 'cognitive_cache_wrong_location'
        elif 'cognitive_cache.cc' in path and 'brain_systems' not in path:
            return 'cognitive_cache_missing_brain_systems'
        elif path.startswith('claude/') and not path.startswith('claude/brain_systems/'):
            return 'missing_brain_systems_prefix'
        return None
        
    def _create_correction_key(self, original: str, resolved: str) -> Optional[str]:
        """Create correction key for auto-fixing"""
        if 'cognitive_cache.cc' in original:
            return 'cognitive_cache_location'
        elif 'cognitive_core.json' in original:
            return 'cognitive_core_location'
        elif 'cognitive_ops.py' in original:
            return 'cognitive_ops_location'
        return None
        
    def smart_resolve(self, path: str, context: str = "") -> Optional[str]:
        """Intelligently resolve a path with learning"""
        
        # 1. Try direct path
        if os.path.exists(path):
            return path
            
        # 2. Check auto-corrections first
        for correction_key, corrected_path in self.learning_data['auto_corrections'].items():
            if correction_key in path.lower():
                if os.path.exists(corrected_path):
                    self.record_successful_resolution(path, corrected_path)
                    return corrected_path
                    
        # 3. Try brain mapper auto-resolution
        brain_resolved = self.mapper.auto_resolve_path(Path(path).name)
        if brain_resolved and os.path.exists(brain_resolved):
            self.record_successful_resolution(path, brain_resolved)
            return brain_resolved
            
        # 4. Try common corrections
        corrected_path = self._apply_common_corrections(path)
        if corrected_path and os.path.exists(corrected_path):
            self.record_successful_resolution(path, corrected_path)
            return corrected_path
            
        # 5. Record failure and suggest alternatives
        self.record_failed_attempt(path, context)
        suggestions = self._suggest_alternatives(path)
        
        if suggestions:
            print(f"[PATH_RESOLVER] Path not found: {path}")
            print(f"[PATH_RESOLVER] Suggestions: {suggestions[:3]}")
            return suggestions[0] if suggestions else None
            
        return None
        
    def _apply_common_corrections(self, path: str) -> Optional[str]:
        """Apply learned common corrections"""
        
        # Common patterns
        corrections = [
            # cognitive_cache corrections
            ('claude/cognitive_cache.cc', 'claude/brain_systems/cognitive_cache.cc'),
            ('cognitive_cache.cc', 'claude/brain_systems/cognitive_cache.cc'),
            
            # cognitive_core corrections  
            ('claude/cognitive_core.json', 'claude/brain_systems/cognitive_core.json'),
            ('cognitive_core.json', 'claude/brain_systems/cognitive_core.json'),
            
            # cognitive_ops corrections
            ('claude/cognitive_ops.py', 'claude/brain_systems/cognitive_ops.py'),
            ('cognitive_ops.py', 'claude/brain_systems/cognitive_ops.py'),
            
            # Add brain_systems prefix if missing
            ('claude/', 'claude/brain_systems/'),
        ]
        
        for pattern, correction in corrections:
            if pattern in path:
                corrected = path.replace(pattern, correction)
                corrected_abs = self.mapper.project_root / corrected
                if corrected_abs.exists():
                    return str(corrected_abs)
                    
        return None
        
    def _suggest_alternatives(self, path: str) -> List[str]:
        """Suggest alternative paths based on filename"""
        filename = Path(path).name
        suggestions = []
        
        # Search for similar filenames
        claude_dir = self.mapper.project_root / 'claude'
        if claude_dir.exists():
            for root, dirs, files in os.walk(claude_dir):
                for file in files:
                    if filename.lower() in file.lower() or file.lower() in filename.lower():
                        full_path = Path(root) / file
                        suggestions.append(str(full_path))
                        
        return suggestions[:5]  # Top 5 suggestions
        
    def generate_learning_report(self) -> str:
        """Generate learning analytics report"""
        
        report = f"""# Smart Path Resolver Learning Report
Generated: {datetime.now().isoformat()}

## Failed Attempts ({len(self.learning_data['failed_attempts'])})
"""
        
        # Recent failures
        recent_failures = self.learning_data['failed_attempts'][-10:]
        for failure in recent_failures:
            report += f"- {failure['path']} ({failure['timestamp'][:10]})\n"
            
        # Common mistakes
        report += f"\n## Common Mistake Patterns\n"
        for mistake, count in self.learning_data['common_mistakes'].items():
            report += f"- {mistake}: {count} occurrences\n"
            
        # Auto-corrections
        report += f"\n## Auto-Correction Rules ({len(self.learning_data['auto_corrections'])})\n"
        for pattern, correction in self.learning_data['auto_corrections'].items():
            report += f"- {pattern} -> {correction}\n"
            
        # Success rate
        total_attempts = len(self.learning_data['failed_attempts']) + len(self.learning_data['successful_resolutions'])
        success_rate = len(self.learning_data['successful_resolutions']) / total_attempts if total_attempts > 0 else 0
        report += f"\n## Performance\n"
        report += f"- Success Rate: {success_rate:.1%}\n"
        report += f"- Total Resolutions: {len(self.learning_data['successful_resolutions'])}\n"
        report += f"- Total Failures: {len(self.learning_data['failed_attempts'])}\n"
        
        return report

def create_smart_resolver() -> SmartPathResolver:
    """Factory function to create smart resolver"""
    return SmartPathResolver()

# Convenience functions for common files
def get_cognitive_cache_path() -> Optional[str]:
    """Get cognitive cache path with smart resolution"""
    resolver = create_smart_resolver()
    return resolver.smart_resolve('cognitive_cache.cc', 'cognitive_cache_access')

def get_cognitive_core_path() -> Optional[str]:
    """Get cognitive core path with smart resolution"""
    resolver = create_smart_resolver()
    return resolver.smart_resolve('cognitive_core.json', 'cognitive_core_access')

def get_cognitive_ops_path() -> Optional[str]:
    """Get cognitive ops path with smart resolution"""
    resolver = create_smart_resolver()
    return resolver.smart_resolve('cognitive_ops.py', 'cognitive_ops_access')

def main():
    """Test smart path resolver"""
    resolver = SmartPathResolver()
    
    print("[PATH_RESOLVER] ===== SMART PATH RESOLVER TEST =====")
    
    # Test common paths
    test_paths = [
        'claude/cognitive_cache.cc',
        'cognitive_cache.cc', 
        'claude/cognitive_core.json',
        'cognitive_ops.py',
        'nonexistent_file.py'
    ]
    
    for test_path in test_paths:
        resolved = resolver.smart_resolve(test_path, 'test')
        print(f"[PATH_RESOLVER] {test_path} -> {resolved}")
        
    # Generate learning report
    report = resolver.generate_learning_report()
    
    report_path = resolver.mapper.project_root / 'smart_path_learning_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"[PATH_RESOLVER] Learning report saved to: {report_path}")
    
    return resolver

if __name__ == "__main__":
    main()