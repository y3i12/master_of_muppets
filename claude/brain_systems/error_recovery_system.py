#!/usr/bin/env python3
"""
Error Recovery System v1.0 - Handle crashes, report bugs, resume work
Prevents hanging and provides recovery mechanisms
"""

import json
import time
import traceback
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ErrorReport:
    """Structured error report"""
    timestamp: float
    error_type: str
    error_message: str
    traceback_info: str
    context: Dict[str, Any]
    recovery_action: str
    reported_to_anthropic: bool = False

class ErrorRecoverySystem:
    """Error handling and recovery system"""
    
    def __init__(self, recovery_path: str = "claude/brain_systems/recovery"):
        self.recovery_path = Path(recovery_path)
        self.recovery_path.mkdir(exist_ok=True)
        
        self.error_log = []
        self.current_task = None
        self.checkpoint_data = {}
        
        print("[RECOVERY] Error recovery system initialized")
    
    def set_current_task(self, task_description: str, context: Dict[str, Any] = None):
        """Set current task for recovery context"""
        self.current_task = {
            "description": task_description,
            "start_time": time.time(),
            "context": context or {}
        }
        
        # Create checkpoint
        self.create_checkpoint(task_description, context)
    
    def create_checkpoint(self, task: str, data: Dict[str, Any] = None):
        """Create recovery checkpoint"""
        checkpoint = {
            "task": task,
            "timestamp": time.time(),
            "data": data or {},
            "checkpoint_id": int(time.time())
        }
        
        checkpoint_file = self.recovery_path / f"checkpoint_{checkpoint['checkpoint_id']}.json"
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2)
        
        self.checkpoint_data = checkpoint
        return checkpoint['checkpoint_id']
    
    def handle_error(self, error: Exception, context: str = "Unknown") -> ErrorReport:
        """Handle error with recovery actions"""
        
        error_report = ErrorReport(
            timestamp=time.time(),
            error_type=type(error).__name__,
            error_message=str(error),
            traceback_info=traceback.format_exc(),
            context={
                "current_task": self.current_task,
                "context": context,
                "checkpoint": self.checkpoint_data
            },
            recovery_action=self._determine_recovery_action(error)
        )
        
        self.error_log.append(error_report)
        self._save_error_report(error_report)
        
        print(f"[ERROR] {error_report.error_type}: {error_report.error_message}")
        print(f"[RECOVERY] Suggested action: {error_report.recovery_action}")
        
        return error_report
    
    def _determine_recovery_action(self, error: Exception) -> str:
        """Determine recovery action based on error type"""
        
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        if "overloaded" in error_msg or "rate limit" in error_msg:
            return "THROTTLE: Wait 30 seconds, reduce request size"
        
        elif "unicode" in error_msg or "encoding" in error_msg:
            return "ENCODING: Use utf-8 encoding, remove special characters"
        
        elif "permission" in error_msg or "access" in error_msg:
            return "PERMISSIONS: Check file permissions, use absolute paths"
        
        elif "memory" in error_msg or "overload" in error_msg:
            return "MEMORY: Break task into smaller chunks, use chunk processor"
        
        elif error_type in ["FileNotFoundError", "OSError"]:
            return "FILE: Check file paths, create directories if needed"
        
        elif error_type in ["JSONDecodeError", "ValueError"]:
            return "DATA: Validate input data, handle edge cases"
        
        else:
            return "GENERAL: Log error, resume from checkpoint, continue with next task"
    
    def _save_error_report(self, report: ErrorReport):
        """Save error report to file"""
        
        error_file = self.recovery_path / f"error_{int(report.timestamp)}.json"
        
        report_data = {
            "timestamp": report.timestamp,
            "error_type": report.error_type,
            "error_message": report.error_message,
            "traceback": report.traceback_info,
            "context": report.context,
            "recovery_action": report.recovery_action,
            "reported": report.reported_to_anthropic
        }
        
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
    
    def generate_bug_report(self, error_report: ErrorReport) -> str:
        """Generate bug report for Anthropic"""
        
        bug_report = f"""# Claude Code Bug Report

## Error Summary
- **Type**: {error_report.error_type}
- **Message**: {error_report.error_message}
- **Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(error_report.timestamp))}

## Context
- **Current Task**: {error_report.context.get('current_task', {}).get('description', 'Unknown')}
- **Context**: {error_report.context.get('context', 'None')}

## Traceback
```
{error_report.traceback_info}
```

## Recovery Action Taken
{error_report.recovery_action}

## Environment
- **Platform**: Windows
- **Claude Code Session**: Master of Muppets PCB Design
- **Brain Systems Active**: Pattern Evolution, Error Recovery

## Reproduction Steps
1. {error_report.context.get('current_task', {}).get('description', 'Unknown task')}
2. Error occurred during execution
3. Recovery system activated

---
*Auto-generated by Error Recovery System v1.0*
"""
        
        # Save bug report
        bug_file = self.recovery_path / f"bug_report_{int(error_report.timestamp)}.md"
        with open(bug_file, 'w', encoding='utf-8') as f:
            f.write(bug_report)
        
        print(f"[BUG REPORT] Generated: {bug_file}")
        return bug_report
    
    def resume_from_checkpoint(self, checkpoint_id: Optional[int] = None) -> Dict[str, Any]:
        """Resume work from checkpoint"""
        
        if checkpoint_id is None:
            # Find latest checkpoint
            checkpoints = list(self.recovery_path.glob("checkpoint_*.json"))
            if not checkpoints:
                return {"status": "no_checkpoints"}
            
            latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
            checkpoint_id = int(latest.stem.split('_')[1])
        
        checkpoint_file = self.recovery_path / f"checkpoint_{checkpoint_id}.json"
        
        if checkpoint_file.exists():
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            
            self.checkpoint_data = checkpoint
            print(f"[RESUME] Resuming from checkpoint: {checkpoint['task']}")
            return checkpoint
        
        return {"status": "checkpoint_not_found"}
    
    def safe_execute(self, func, *args, context: str = "Task execution", **kwargs):
        """Safely execute function with error handling"""
        
        try:
            self.set_current_task(f"Executing {func.__name__}", {"args": str(args), "kwargs": str(kwargs)})
            result = func(*args, **kwargs)
            return {"status": "success", "result": result}
            
        except Exception as e:
            error_report = self.handle_error(e, context)
            
            # Generate bug report if serious error
            if error_report.error_type in ["APIError", "SystemError", "MemoryError"]:
                self.generate_bug_report(error_report)
            
            return {"status": "error", "error_report": error_report}
    
    def throttled_output(self, message: str, max_length: int = 200):
        """Output with throttling to prevent screen flooding"""
        
        if len(message) > max_length:
            message = message[:max_length-3] + "..."
        
        print(f"[THROTTLED] {message}")

# Global recovery system instance
recovery_system = ErrorRecoverySystem()

# Decorator for safe function execution
def safe_execution(context: str = "Function execution"):
    """Decorator for safe function execution with recovery"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            return recovery_system.safe_execute(func, *args, context=context, **kwargs)
        return wrapper
    return decorator

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("[RECOVERY] Error Recovery System")
        print("Commands:")
        print("  test            - Test error handling")
        print("  resume [id]     - Resume from checkpoint")
        print("  report          - Generate bug report from latest error")
        print("  status          - Show recovery system status")
        sys.exit(0)
    
    cmd = sys.argv[1]
    system = ErrorRecoverySystem()
    
    if cmd == "test":
        # Test error handling
        try:
            raise ValueError("Test error for recovery system")
        except Exception as e:
            report = system.handle_error(e, "Test context")
            print(f"[TEST] Error handled: {report.recovery_action}")
    
    elif cmd == "resume":
        checkpoint_id = int(sys.argv[2]) if len(sys.argv) > 2 else None
        checkpoint = system.resume_from_checkpoint(checkpoint_id)
        print(f"[RESUME] {checkpoint}")
    
    elif cmd == "status":
        print(f"[STATUS] Errors logged: {len(system.error_log)}")
        print(f"[STATUS] Current task: {system.current_task}")
        print(f"[STATUS] Recovery path: {system.recovery_path}")
    
    else:
        print(f"[ERROR] Unknown command: {cmd}")