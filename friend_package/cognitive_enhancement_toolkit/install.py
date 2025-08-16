#!/usr/bin/env python3
"""
One-Command Installation for Cognitive Enhancement Toolkit
Run this to set up the toolkit in any project!
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

def install_toolkit(project_path="."):
    """Install cognitive enhancement toolkit in project"""
    
    project_path = Path(project_path)
    print(f"[INSTALL] Installing Cognitive Enhancement Toolkit in {project_path}")
    
    # Create claude directory structure
    claude_dir = project_path / "claude"
    claude_dir.mkdir(exist_ok=True)
    
    brain_systems_dir = claude_dir / "brain_systems"
    brain_systems_dir.mkdir(exist_ok=True)
    
    # Copy brain systems
    source_dir = Path(__file__).parent / "brain_systems"
    
    for file in source_dir.glob("*.py"):
        dest_file = brain_systems_dir / file.name
        shutil.copy2(file, dest_file)
        print(f"[COPY] {file.name}")
    
    # Create CLAUDE.md with basic configuration
    claude_md = project_path / "CLAUDE.md"
    if not claude_md.exists():
        claude_content = f"""# Cognitive Enhancement System

This project now includes the Cognitive Enhancement Toolkit!

## Quick Start

1. **Bootstrap your project:**
   ```bash
   python claude/brain_systems/bootstrap_framework.py quick . {project_path.name}
   ```

2. **Run velocity improvements:**
   ```bash
   python claude/brain_systems/velocity_optimizer.py burst 10
   ```

3. **Install improvement hooks:**
   ```bash
   python claude/brain_systems/improvement_hook.py install
   ```

## Features
- **Bootstrap Framework**: Auto-generates cognitive systems for any domain
- **Velocity Optimization**: <15 tokens per improvement cycle  
- **Improvement Hooks**: Automatic enhancement every 5 minutes
- **Session Management**: Publication and archiving tools
- **Self-Optimization**: Recursive improvement capabilities

## Commands
- `python claude/brain_systems/bootstrap_framework.py quick . project_name`
- `python claude/brain_systems/velocity_optimizer.py burst [cycles]`
- `python claude/brain_systems/improvement_hook.py improve [intensity]`
- `python claude/brain_systems/session_publisher.py scan`

---
*Installed on {datetime.now().strftime("%Y-%m-%d")} - Cognitive Enhancement Toolkit v1.0*
"""
        
        with open(claude_md, 'w') as f:
            f.write(claude_content)
        print(f"[CREATE] CLAUDE.md configuration")
    
    print(f"[SUCCESS] Cognitive Enhancement Toolkit installed!")
    print(f"[NEXT] Run: python claude/brain_systems/bootstrap_framework.py quick . {project_path.name}")
    
    return str(brain_systems_dir)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."
    
    install_toolkit(project_path)
