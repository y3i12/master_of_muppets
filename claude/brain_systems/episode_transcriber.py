#!/usr/bin/env python3
"""
Episode Transcriber v1.0 - Ultra-efficient session transcription with minimal tokens
Automatically maintains episode transcripts with smart compression and formatting
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class EpisodeTranscriber:
    """Smart transcription system for episode management"""
    
    def __init__(self, season: str = "season_02_cognitive_enhancement"):
        self.season_path = Path(f"claude/sessions/{season}")
        self.current_episode = None
        self.transcript_buffer = []
        self.last_update = time.time()
        
    def quick_append(self, user_msg: str, assistant_msg: str, achievements: List[str] = None, findings: str = None) -> bool:
        """Ultra-fast transcript append (< 5 tokens)"""
        
        # Find current episode
        episodes = sorted(self.season_path.glob("episode_*.md"))
        if not episodes:
            return False
        
        current = episodes[-1]  # Most recent episode
        
        # Read existing content
        with open(current, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove closing marker
        if content.endswith("*Episode"):
            content = content.rsplit("\n---", 1)[0]
        
        # Format new exchange
        exchange = f"\n\n### OP:\n{user_msg}\n\n### Sir Claude:\n{assistant_msg}"
        
        # Add achievements if present
        if achievements:
            exchange += "\n\n**Achievements:**"
            for achievement in achievements:
                exchange += f"\n- {achievement}"
        
        # Add findings if present
        if findings:
            exchange += f"\n\n**Findings:**\n{findings}"
        
        # Append and close
        content += exchange + "\n\n---\n\n*Episode in progress...*"
        
        # Write back
        with open(current, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    def smart_update(self, exchange_type: str, key_points: Dict[str, Any]) -> str:
        """Smart update with automatic formatting"""
        
        templates = {
            "technical": "**Technical Achievement:** {description}\n- Impact: {impact}\n- Implementation: {implementation}",
            "insight": "**Key Insight:** {description}\n- Discovery: {discovery}\n- Application: {application}",
            "tool_created": "**Tool Created:** `{name}`\n- Purpose: {purpose}\n- Features: {features}",
            "optimization": "**Optimization Results:**\n- Performance: {performance}\n- Efficiency: {efficiency}\n- Improvements: {improvements}"
        }
        
        template = templates.get(exchange_type, "{description}")
        formatted = template.format(**key_points)
        
        return formatted
    
    def batch_update(self, exchanges: List[Dict[str, str]]) -> bool:
        """Batch update multiple exchanges efficiently"""
        
        episodes = sorted(self.season_path.glob("episode_*.md"))
        if not episodes:
            return False
        
        current = episodes[-1]
        
        with open(current, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove closing
        if "*Episode" in content:
            content = content.rsplit("\n---", 1)[0]
        
        # Add all exchanges
        for exchange in exchanges:
            content += f"\n\n### OP:\n{exchange.get('user', 'Continued...')}"
            content += f"\n\n### Sir Claude:\n{exchange.get('assistant', 'Working...')}"
            
            if 'achievements' in exchange:
                content += f"\n\n{exchange['achievements']}"
        
        content += "\n\n---\n\n*Episode in progress...*"
        
        with open(current, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    def auto_transcript(self, user_msg: str, assistant_response: str, auto_detect: bool = True) -> bool:
        """Automatically transcribe with smart detection"""
        
        if auto_detect:
            # Detect important content
            important_keywords = ['created', 'built', 'achieved', 'discovered', 'optimized', 'completed']
            is_important = any(keyword in assistant_response.lower() for keyword in important_keywords)
            
            if not is_important and len(assistant_response) < 100:
                # Skip trivial exchanges
                return False
        
        # Smart compression
        if len(user_msg) > 200:
            user_msg = user_msg[:197] + "..."
        
        if len(assistant_response) > 500:
            # Extract key points
            lines = assistant_response.split('\n')
            key_lines = [line for line in lines if any(
                marker in line for marker in ['**', '##', '- ', '✅', '🚀', 'Achievement', 'Created', 'Results']
            )]
            
            if key_lines:
                assistant_response = '\n'.join(key_lines[:10])  # Top 10 key points
            else:
                assistant_response = assistant_response[:497] + "..."
        
        return self.quick_append(user_msg, assistant_response)

# Ultra-compact CLI
if __name__ == "__main__":
    import sys
    
    transcriber = EpisodeTranscriber()
    
    if len(sys.argv) < 2:
        print("[TRANSCRIBE] Episode Transcriber - Smart session management")
        print("Commands:")
        print("  append <user> <assistant>  - Quick append to current episode")
        print("  smart <type> <json_data>   - Smart formatted update")
        print("  auto <user> <assistant>    - Auto-detect and transcribe")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "append" and len(sys.argv) > 3:
        user_msg = sys.argv[2]
        assistant_msg = sys.argv[3]
        success = transcriber.quick_append(user_msg, assistant_msg)
        print(f"[{'OK' if success else 'FAIL'}] Transcript updated")
    
    elif cmd == "smart" and len(sys.argv) > 3:
        exchange_type = sys.argv[2]
        key_points = json.loads(sys.argv[3])
        formatted = transcriber.smart_update(exchange_type, key_points)
        print(f"[FORMATTED] {formatted}")
    
    elif cmd == "auto" and len(sys.argv) > 3:
        user_msg = sys.argv[2]
        assistant_msg = sys.argv[3]
        success = transcriber.auto_transcript(user_msg, assistant_msg)
        print(f"[{'TRANSCRIBED' if success else 'SKIPPED'}] Auto-detection complete")
    
    else:
        print(f"[ERROR] Invalid command: {cmd}")