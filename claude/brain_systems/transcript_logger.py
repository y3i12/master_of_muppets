#!/usr/bin/env python3
"""
Transcript Logger - Ultra-fast conversation capture
Minimal overhead logging system for cognitive enhancement
"""

import json
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class TranscriptMessage:
    timestamp: float
    role: str  # 'user' or 'assistant'
    content: str
    episode: str
    message_id: int

@dataclass 
class TranscriptSession:
    session_id: str
    start_time: float
    episode: str
    branch: str
    messages: List[TranscriptMessage]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'start_time': self.start_time,
            'episode': self.episode,
            'branch': self.branch,
            'messages': [asdict(msg) for msg in self.messages]
        }

class TranscriptLogger:
    """Ultra-fast transcript logging with minimal overhead"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent
        self.base_path = Path(base_path)
        self.transcript_dir = self.base_path / "claude" / "transcripts"
        self.transcript_dir.mkdir(exist_ok=True, parents=True)
        
        # Current session state
        self.current_session = None
        self.message_counter = 0
        self.session_start = time.time()
        
        # Initialize session
        self._start_new_session()
    
    def _start_new_session(self):
        """Start a new transcript session"""
        session_id = f"s2e4_{int(self.session_start)}"
        episode = "s2e4_kicad_fu_aisler_mastery"
        branch = "season_02"
        
        self.current_session = TranscriptSession(
            session_id=session_id,
            start_time=self.session_start,
            episode=episode,
            branch=branch,
            messages=[]
        )
    
    def log_message(self, role: str, content: str) -> None:
        """Log a message with ultra-fast performance"""
        if not self.current_session:
            self._start_new_session()
        
        self.message_counter += 1
        
        message = TranscriptMessage(
            timestamp=time.time(),
            role=role,
            content=content[:2000],  # Truncate for performance
            episode=self.current_session.episode,
            message_id=self.message_counter
        )
        
        self.current_session.messages.append(message)
        
        # Auto-save every 10 messages for safety
        if self.message_counter % 10 == 0:
            self._save_session()
    
    def _save_session(self) -> None:
        """Save current session to disk"""
        if not self.current_session:
            return
        
        filename = f"{self.current_session.session_id}.json"
        filepath = self.transcript_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.current_session.to_dict(), f, indent=2)
        except Exception as e:
            # Ultra-fast fallback - just print error, don't crash
            print(f"[TRANSCRIPT] Save error: {e}")
    
    def finalize_session(self) -> str:
        """Finalize and save the current session"""
        if self.current_session:
            self._save_session()
            session_id = self.current_session.session_id
            self.current_session = None
            return session_id
        return ""
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        if not self.current_session:
            return {}
        
        return {
            'session_id': self.current_session.session_id,
            'episode': self.current_session.episode,
            'message_count': len(self.current_session.messages),
            'duration_minutes': (time.time() - self.current_session.start_time) / 60,
            'messages_per_minute': len(self.current_session.messages) / max(1, (time.time() - self.current_session.start_time) / 60)
        }

# Global transcript logger instance
_global_logger = None

def get_transcript_logger() -> TranscriptLogger:
    """Get the global transcript logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = TranscriptLogger()
    return _global_logger

def log_user_message(content: str) -> None:
    """Quick function to log user messages"""
    logger = get_transcript_logger()
    logger.log_message('user', content)

def log_assistant_message(content: str) -> None:
    """Quick function to log assistant messages"""
    logger = get_transcript_logger()
    logger.log_message('assistant', content)

def finalize_transcript() -> str:
    """Finalize current transcript session"""
    logger = get_transcript_logger()
    return logger.finalize_session()

def get_transcript_stats() -> Dict[str, Any]:
    """Get current transcript statistics"""
    logger = get_transcript_logger()
    return logger.get_session_stats()

if __name__ == "__main__":
    # Quick test
    logger = TranscriptLogger()
    logger.log_message('user', 'Test user message')
    logger.log_message('assistant', 'Test assistant response')
    
    stats = logger.get_session_stats()
    print(f"Session: {stats['session_id']}")
    print(f"Messages: {stats['message_count']}")
    print(f"Duration: {stats['duration_minutes']:.1f} minutes")
    
    session_id = logger.finalize_session()
    print(f"Finalized session: {session_id}")