#!/usr/bin/env python3
"""
Cognitive Operations - Ultra-fast mental state management
Acts like a compiled library for rapid cognitive continuity
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

class CognitiveCore:
    """Lightweight cognitive state manager - think of it as mental RAM"""
    
    def __init__(self, core_path: str = "cognitive_core.json"):
        self.path = Path(core_path)
        self.state = self.load()
        
    def load(self) -> Dict:
        """Hot-load cognitive state - <50ms"""
        if self.path.exists():
            with open(self.path, 'r') as f:
                return json.load(f)
        return self._default_state()
    
    def save(self) -> None:
        """Persist state atomically"""
        self.state['ts'] = datetime.now().isoformat()
        with open(self.path, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def q(self, path: str) -> Any:
        """Query state using dot notation - O(1) lookup
        Examples: q('mem.s2.goal'), q('flags.snake_case')"""
        keys = path.split('.')
        val = self.state
        for k in keys:
            val = val.get(k, None)
            if val is None:
                return None
        return val
    
    def u(self, path: str, value: Any) -> None:
        """Update state using dot notation - O(1) update"""
        keys = path.split('.')
        ref = self.state
        for k in keys[:-1]:
            if k not in ref:
                ref[k] = {}
            ref = ref[k]
        ref[keys[-1]] = value
    
    def learn(self, insight: str) -> None:
        """Append learning - cognitive growth"""
        if 'learn' not in self.state:
            self.state['learn'] = {'pend': []}
        self.state['learn']['last'] = insight
        if 'hist' not in self.state['learn']:
            self.state['learn']['hist'] = []
        self.state['learn']['hist'].append({
            'ts': datetime.now().isoformat(),
            'insight': insight
        })
    
    def flag(self, name: str) -> bool:
        """Check boolean flag - instant lookup"""
        return self.state.get('flags', {}).get(name, False)
    
    def idx(self, category: str, key: str = None) -> Any:
        """Access indexed knowledge"""
        idx_data = self.state.get('idx', {}).get(category, {})
        return idx_data.get(key) if key else idx_data
    
    def compress(self) -> str:
        """Generate ultra-compact representation for context"""
        # Pack essential state into minimal tokens
        s = self.state
        compact = f"CC[v{s['v']}|{s['git']}|"
        
        # Current episode
        if 'mem' in s and 's2' in s['mem']:
            compact += f"s2e1:{s['mem']['s2'].get('e1', '?')}|"
        
        # Active flags (only true ones)
        flags = [k[:3] for k, v in s.get('flags', {}).items() if v]
        if flags:
            compact += f"F:{','.join(flags)}|"
        
        # Recent learning
        if 'learn' in s and 'last' in s['learn']:
            compact += f"L:{s['learn']['last'][:20]}]"
        
        return compact
    
    def _default_state(self) -> Dict:
        """Initialize default cognitive state"""
        return {
            "v": "2.0.0",
            "ts": datetime.now().isoformat(),
            "git": "unknown",
            "ctx": {},
            "mem": {},
            "idx": {},
            "flags": {},
            "ops": {},
            "learn": {"pend": []}
        }

# CLI Interface for rapid mental operations
if __name__ == "__main__":
    cc = CognitiveCore()
    
    if len(sys.argv) < 2:
        print(f"Cognitive Core v{cc.state['v']}")
        print(f"Compact: {cc.compress()}")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == 'q' and len(sys.argv) > 2:
        # Query: python cognitive_ops.py q mem.s2.goal
        result = cc.q(sys.argv[2])
        print(json.dumps(result) if result else "null")
    
    elif cmd == 'u' and len(sys.argv) > 3:
        # Update: python cognitive_ops.py u mem.s2.e1 "mahna_mahna:complete"
        cc.u(sys.argv[2], sys.argv[3])
        cc.save()
        print(f"Updated {sys.argv[2]}")
    
    elif cmd == 'learn' and len(sys.argv) > 2:
        # Learn: python cognitive_ops.py learn "discovered pcb zones"
        cc.learn(' '.join(sys.argv[2:]))
        cc.save()
        print("Learning recorded")
    
    elif cmd == 'compress':
        # Get compact representation
        print(cc.compress())
    
    elif cmd == 'flag' and len(sys.argv) > 2:
        # Check flag: python cognitive_ops.py flag snake_case
        print("true" if cc.flag(sys.argv[2]) else "false")
    
    else:
        print("Usage: cognitive_ops.py [q|u|learn|compress|flag] [args...]")