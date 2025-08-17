#!/usr/bin/env python3
"""
Auto Brain Updater v1.0 - Self-updating brain index system
Monitors file system changes and automatically updates brain mappings
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Set, List
from datetime import datetime
from brain_path_mapper import BrainPathMapper
from smart_path_resolver import SmartPathResolver

class AutoBrainUpdater:
    """Self-updating brain index system with change detection"""
    
    def __init__(self, project_root: str = None):
        self.mapper = BrainPathMapper(project_root)
        self.resolver = SmartPathResolver(project_root)
        self.update_log_file = self.mapper.project_root / 'claude' / 'brain_systems' / 'brain_updates.log'
        self.file_hashes = {}
        self.last_update = None
        
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file for change detection"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return ""
            
    def scan_brain_files(self) -> Dict[str, str]:
        """Scan all brain files and return their hashes"""
        hashes = {}
        claude_dir = self.mapper.project_root / 'claude'
        
        if not claude_dir.exists():
            return hashes
            
        # Scan for all brain-related files
        brain_extensions = ['.cc', '.json', '.py', '.md']
        
        for root, dirs, files in os.walk(claude_dir):
            for file in files:
                if any(file.endswith(ext) for ext in brain_extensions):
                    file_path = Path(root) / file
                    hashes[str(file_path)] = self.calculate_file_hash(str(file_path))
                    
        return hashes
        
    def detect_changes(self) -> Dict[str, str]:
        """Detect changes in brain files since last scan"""
        current_hashes = self.scan_brain_files()
        changes = {}
        
        # New files
        for file_path, current_hash in current_hashes.items():
            if file_path not in self.file_hashes:
                changes[file_path] = 'ADDED'
            elif self.file_hashes[file_path] != current_hash:
                changes[file_path] = 'MODIFIED'
                
        # Deleted files
        for file_path in self.file_hashes:
            if file_path not in current_hashes:
                changes[file_path] = 'DELETED'
                
        self.file_hashes = current_hashes
        return changes
        
    def update_brain_index(self, force: bool = False) -> bool:
        """Update brain index if changes detected"""
        changes = self.detect_changes()
        
        if not changes and not force:
            return False
            
        print(f"[BRAIN_UPDATER] Detected {len(changes)} changes, updating brain index...")
        
        # Update the brain index
        self.mapper.save_brain_index()
        
        # Log the update
        self.log_update(changes)
        
        self.last_update = datetime.now()
        return True
        
    def log_update(self, changes: Dict[str, str]):
        """Log brain index updates"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'changes': changes,
            'change_count': len(changes)
        }
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.update_log_file), exist_ok=True)
        
        # Append to log file
        with open(self.update_log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
        print(f"[BRAIN_UPDATER] Logged {len(changes)} changes to {self.update_log_file}")
        
    def auto_update_cycle(self, interval_seconds: int = 60):
        """Run continuous auto-update cycle"""
        print(f"[BRAIN_UPDATER] Starting auto-update cycle (interval: {interval_seconds}s)")
        
        # Initial scan
        self.file_hashes = self.scan_brain_files()
        
        while True:
            try:
                time.sleep(interval_seconds)
                if self.update_brain_index():
                    print(f"[BRAIN_UPDATER] Brain index updated at {datetime.now().strftime('%H:%M:%S')}")
                    
            except KeyboardInterrupt:
                print("[BRAIN_UPDATER] Auto-update cycle stopped")
                break
            except Exception as e:
                print(f"[BRAIN_UPDATER] Error in update cycle: {e}")
                time.sleep(5)  # Wait before retrying
                
    def validate_brain_integrity(self) -> Dict[str, any]:
        """Validate integrity of brain system"""
        integrity = {
            'timestamp': datetime.now().isoformat(),
            'status': 'HEALTHY',
            'issues': [],
            'stats': {}
        }
        
        # Check if core files exist
        core_files = ['cognitive_cache.cc', 'cognitive_core.json', 'cognitive_ops.py']
        missing_core = []
        
        for core_file in core_files:
            resolved_path = self.resolver.smart_resolve(core_file)
            if not resolved_path or not os.path.exists(resolved_path):
                missing_core.append(core_file)
                
        if missing_core:
            integrity['status'] = 'DEGRADED'
            integrity['issues'].append(f"Missing core files: {missing_core}")
            
        # Check brain index validity
        brain_index = self.mapper.load_brain_index()
        if not brain_index:
            integrity['status'] = 'CRITICAL'
            integrity['issues'].append("Brain index not found or invalid")
        else:
            validation = self.mapper.validate_paths()
            invalid_paths = [k for k, v in validation.items() if not v]
            if invalid_paths:
                integrity['status'] = 'DEGRADED'
                integrity['issues'].append(f"Invalid paths: {invalid_paths}")
                
        # Statistics
        integrity['stats'] = {
            'brain_files_count': len(self.file_hashes),
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'core_files_found': len(core_files) - len(missing_core)
        }
        
        return integrity
        
    def repair_brain_system(self) -> bool:
        """Attempt to repair brain system issues"""
        print("[BRAIN_UPDATER] Attempting brain system repair...")
        
        # Force update brain index
        self.update_brain_index(force=True)
        
        # Re-validate
        integrity = self.validate_brain_integrity()
        
        if integrity['status'] == 'HEALTHY':
            print("[BRAIN_UPDATER] Brain system repair successful")
            return True
        else:
            print(f"[BRAIN_UPDATER] Brain system still has issues: {integrity['issues']}")
            return False
            
    def generate_brain_health_report(self) -> str:
        """Generate comprehensive brain health report"""
        integrity = self.validate_brain_integrity()
        
        report = f"""# Brain System Health Report
Generated: {integrity['timestamp']}
Status: **{integrity['status']}**

## Statistics
- Brain Files: {integrity['stats']['brain_files_count']}
- Core Files Found: {integrity['stats']['core_files_found']}/3
- Last Update: {integrity['stats']['last_update'] or 'Never'}

## Issues ({len(integrity['issues'])})
"""
        
        if integrity['issues']:
            for issue in integrity['issues']:
                report += f"- {issue}\n"
        else:
            report += "No issues detected\n"
            
        # Recent updates
        report += "\n## Recent Updates\n"
        if self.update_log_file.exists():
            with open(self.update_log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-5:]:  # Last 5 updates
                    try:
                        log_entry = json.loads(line.strip())
                        timestamp = log_entry['timestamp'][:19]  # Remove microseconds
                        change_count = log_entry['change_count']
                        report += f"- {timestamp}: {change_count} changes\n"
                    except:
                        continue
        else:
            report += "No update history found\n"
            
        return report
        
    def setup_auto_maintenance(self):
        """Setup automatic brain maintenance"""
        print("[BRAIN_UPDATER] Setting up automatic brain maintenance...")
        
        # Initial integrity check
        integrity = self.validate_brain_integrity()
        print(f"[BRAIN_UPDATER] Initial brain status: {integrity['status']}")
        
        if integrity['status'] != 'HEALTHY':
            print("[BRAIN_UPDATER] Attempting repair...")
            self.repair_brain_system()
            
        # Initial brain index update
        self.update_brain_index(force=True)
        
        print("[BRAIN_UPDATER] Brain maintenance setup complete")

def main():
    """Run brain updater system"""
    updater = AutoBrainUpdater()
    
    print("[BRAIN_UPDATER] ===== AUTO BRAIN UPDATER =====")
    
    # Setup maintenance
    updater.setup_auto_maintenance()
    
    # Generate health report
    report = updater.generate_brain_health_report()
    
    report_path = updater.mapper.project_root / 'brain_health_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"[BRAIN_UPDATER] Health report saved to: {report_path}")
    
    # Test change detection
    print("[BRAIN_UPDATER] Testing change detection...")
    changes = updater.detect_changes()
    print(f"[BRAIN_UPDATER] Detected {len(changes)} initial changes")
    
    return updater

if __name__ == "__main__":
    main()