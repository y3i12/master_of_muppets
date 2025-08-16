#!/usr/bin/env python3
"""
Transcript Sync v1.0 - Automated Session Documentation Management
Keeps session transcripts synchronized and maintains episode continuity
"""

import json
import time
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

@dataclass
class SessionEvent:
    """A notable event within a session"""
    timestamp: float
    event_type: str  # user_input, assistant_response, tool_use, breakthrough, etc.
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    importance: int = 5  # 1-10, 10 being critical breakthrough

@dataclass
class Episode:
    """A complete episode with metadata"""
    season: int
    episode_number: int
    title: str
    file_path: str
    started_time: float
    last_updated: float
    events: List[SessionEvent] = field(default_factory=list)
    status: str = "active"  # active, completed, archived
    key_insights: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)

class TranscriptSync:
    """Automated session documentation and episode management"""
    
    def __init__(self, sessions_root: str = "claude/sessions"):
        self.sessions_root = Path(sessions_root)
        self.current_episode: Optional[Episode] = None
        self.event_buffer: List[SessionEvent] = []
        self.auto_save_interval = 300  # 5 minutes
        self.last_save_time = time.time()
        
        # Session state
        self.session_start_time = time.time()
        self.git_branch = self._get_current_branch()
        self.current_season = self._extract_season_from_branch()
        
        # Load active episode
        self._load_current_episode()
    
    def start_episode(self, title: str, force_new: bool = False) -> Episode:
        """Start a new episode or continue existing one"""
        if self.current_episode and not force_new:
            print(f"📝 Continuing episode: {self.current_episode.title}")
            return self.current_episode
        
        # Determine episode number
        episode_num = self._get_next_episode_number()
        
        # Create episode
        episode = Episode(
            season=self.current_season,
            episode_number=episode_num,
            title=title,
            file_path=self._generate_episode_path(title, episode_num),
            started_time=time.time(),
            last_updated=time.time()
        )
        
        self.current_episode = episode
        self._create_episode_file(episode)
        
        print(f"🎬 Started Episode {episode_num}: {title}")
        return episode
    
    def log_user_input(self, content: str, context: Dict = None):
        """Log user input event"""
        event = SessionEvent(
            timestamp=time.time(),
            event_type="user_input",
            content=content,
            context=context or {},
            importance=self._assess_importance(content, "user")
        )
        
        self._add_event(event)
    
    def log_assistant_response(self, content: str, context: Dict = None):
        """Log assistant response event"""
        event = SessionEvent(
            timestamp=time.time(),
            event_type="assistant_response", 
            content=content,
            context=context or {},
            importance=self._assess_importance(content, "assistant")
        )
        
        self._add_event(event)
    
    def log_breakthrough(self, description: str, details: Dict = None):
        """Log a breakthrough moment"""
        event = SessionEvent(
            timestamp=time.time(),
            event_type="breakthrough",
            content=description,
            context=details or {},
            importance=9
        )
        
        self._add_event(event)
        
        if self.current_episode:
            self.current_episode.key_insights.append(description)
        
        print(f"💡 Breakthrough logged: {description}")
    
    def log_achievement(self, achievement: str, details: Dict = None):
        """Log a significant achievement"""
        event = SessionEvent(
            timestamp=time.time(),
            event_type="achievement",
            content=achievement,
            context=details or {},
            importance=8
        )
        
        self._add_event(event)
        
        if self.current_episode:
            self.current_episode.achievements.append(achievement)
        
        print(f"🏆 Achievement logged: {achievement}")
    
    def log_tool_use(self, tool_name: str, purpose: str, result: str = None):
        """Log tool usage"""
        event = SessionEvent(
            timestamp=time.time(),
            event_type="tool_use",
            content=f"Used {tool_name}: {purpose}",
            context={
                "tool": tool_name,
                "purpose": purpose,
                "result": result
            },
            importance=4
        )
        
        self._add_event(event)
    
    def update_episode(self, content: str):
        """Manually update current episode with content"""
        if not self.current_episode:
            print("⚠️ No active episode to update")
            return
        
        # Append to episode file
        episode_file = Path(self.current_episode.file_path)
        if episode_file.exists():
            with open(episode_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n{content}")
        
        self.current_episode.last_updated = time.time()
        self._auto_save_check()
        
        print(f"📝 Episode updated: {self.current_episode.title}")
    
    def complete_episode(self, summary: str = None):
        """Mark current episode as complete"""
        if not self.current_episode:
            print("⚠️ No active episode to complete")
            return
        
        # Generate episode summary
        self._generate_episode_summary(summary)
        
        # Mark as completed
        self.current_episode.status = "completed"
        self.current_episode.last_updated = time.time()
        
        # Save final state
        self._save_episode_metadata()
        
        print(f"✅ Episode completed: {self.current_episode.title}")
        
        # Clear current episode
        self.current_episode = None
    
    def generate_season_summary(self) -> Dict[str, Any]:
        """Generate summary of current season"""
        season_dir = self.sessions_root / f"season_{self.current_season:02d}_*"
        season_dirs = list(self.sessions_root.glob(f"season_{self.current_season:02d}_*"))
        
        if not season_dirs:
            return {"error": "No season directory found"}
        
        season_dir = season_dirs[0]
        episodes = list(season_dir.glob("episode_*.md"))
        
        summary = {
            "season": self.current_season,
            "total_episodes": len(episodes),
            "episodes": [],
            "key_themes": [],
            "major_achievements": [],
            "total_insights": 0
        }
        
        # Analyze each episode
        for episode_file in sorted(episodes):
            episode_info = self._analyze_episode_file(episode_file)
            summary["episodes"].append(episode_info)
            summary["key_themes"].extend(episode_info.get("themes", []))
            summary["major_achievements"].extend(episode_info.get("achievements", []))
        
        # Deduplicate and summarize
        summary["key_themes"] = list(set(summary["key_themes"]))
        summary["major_achievements"] = list(set(summary["major_achievements"]))
        
        return summary
    
    def sync_with_git(self) -> Dict[str, Any]:
        """Sync episode documentation with git state"""
        git_status = self._get_git_status()
        
        # Check for new commits that might need documentation
        recent_commits = self._get_recent_commits(limit=5)
        undocumented_commits = []
        
        for commit in recent_commits:
            if not self._commit_has_documentation(commit):
                undocumented_commits.append(commit)
        
        sync_info = {
            "current_branch": self.git_branch,
            "current_season": self.current_season,
            "active_episode": self.current_episode.title if self.current_episode else None,
            "git_status": git_status,
            "undocumented_commits": len(undocumented_commits),
            "needs_documentation": len(undocumented_commits) > 0
        }
        
        return sync_info
    
    def auto_generate_transcript(self, force: bool = False) -> str:
        """Auto-generate transcript from session events"""
        if not self.current_episode or not self.event_buffer:
            return ""
        
        # Filter important events
        important_events = [e for e in self.event_buffer if e.importance >= 6]
        
        if not important_events and not force:
            return ""
        
        # Generate transcript
        transcript = self._events_to_transcript(important_events)
        
        # Clear processed events
        self.event_buffer.clear()
        
        return transcript
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current synchronization status"""
        return {
            "current_episode": {
                "title": self.current_episode.title if self.current_episode else None,
                "events_count": len(self.event_buffer),
                "last_updated": self.current_episode.last_updated if self.current_episode else None
            },
            "session_info": {
                "duration_minutes": (time.time() - self.session_start_time) / 60,
                "season": self.current_season,
                "git_branch": self.git_branch
            },
            "auto_save": {
                "enabled": True,
                "interval_seconds": self.auto_save_interval,
                "last_save_ago": time.time() - self.last_save_time
            }
        }
    
    def _load_current_episode(self):
        """Load currently active episode if any"""
        # Look for active episodes in current season
        season_pattern = f"season_{self.current_season:02d}_*"
        season_dirs = list(self.sessions_root.glob(season_pattern))
        
        if not season_dirs:
            return
        
        season_dir = season_dirs[0]
        episodes = list(season_dir.glob("episode_*.md"))
        
        if episodes:
            # Load the most recent episode
            latest_episode = max(episodes, key=lambda x: x.stat().st_mtime)
            self._load_episode_from_file(latest_episode)
    
    def _get_next_episode_number(self) -> int:
        """Get the next episode number for current season"""
        season_pattern = f"season_{self.current_season:02d}_*"
        season_dirs = list(self.sessions_root.glob(season_pattern))
        
        if not season_dirs:
            return 1
        
        season_dir = season_dirs[0]
        episodes = list(season_dir.glob("episode_*.md"))
        
        if not episodes:
            return 1
        
        # Extract episode numbers
        episode_nums = []
        for ep in episodes:
            match = re.search(r'episode_(\d+)_', ep.name)
            if match:
                episode_nums.append(int(match.group(1)))
        
        return max(episode_nums, default=0) + 1
    
    def _generate_episode_path(self, title: str, episode_num: int) -> str:
        """Generate file path for new episode"""
        # Convert title to snake_case
        snake_title = re.sub(r'[^a-zA-Z0-9]+', '_', title).lower().strip('_')
        
        # Determine season theme (heuristic)
        season_theme = "unknown_theme"
        if self.current_season == 1:
            season_theme = "knowledge_and_tooling"
        elif self.current_season == 2:
            season_theme = "pcb_layout"
        
        # Create season directory if needed
        season_dir = self.sessions_root / f"season_{self.current_season:02d}_{season_theme}"
        season_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate episode file path
        episode_file = season_dir / f"episode_{episode_num:02d}_{snake_title}.md"
        
        return str(episode_file)
    
    def _create_episode_file(self, episode: Episode):
        """Create initial episode file"""
        episode_path = Path(episode.file_path)
        episode_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""# episode_{episode.episode_number:02d}_{episode.title.lower().replace(' ', '_')}

## Session Overview
Episode {episode.episode_number} of Season {episode.season}: {episode.title}
Started: {datetime.fromtimestamp(episode.started_time).isoformat()}

---

"""
        
        with open(episode_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _add_event(self, event: SessionEvent):
        """Add event to buffer and episode"""
        self.event_buffer.append(event)
        
        if self.current_episode:
            self.current_episode.events.append(event)
            self.current_episode.last_updated = time.time()
        
        # Auto-save check
        self._auto_save_check()
    
    def _auto_save_check(self):
        """Check if auto-save should trigger"""
        if time.time() - self.last_save_time > self.auto_save_interval:
            self._auto_save()
    
    def _auto_save(self):
        """Perform automatic save of current state"""
        if self.current_episode and self.event_buffer:
            # Generate partial transcript
            transcript = self.auto_generate_transcript()
            if transcript:
                self.update_episode(transcript)
        
        self.last_save_time = time.time()
        print("💾 Auto-saved session state")
    
    def _assess_importance(self, content: str, source: str) -> int:
        """Assess importance of content (1-10)"""
        importance = 5  # Default
        
        # Keywords that increase importance
        high_importance_keywords = [
            'breakthrough', 'discovered', 'solved', 'created', 'built',
            'achievement', 'success', 'working', 'complete', 'innovation'
        ]
        
        medium_importance_keywords = [
            'insight', 'learned', 'found', 'understand', 'pattern',
            'improvement', 'optimization', 'design', 'approach'
        ]
        
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in high_importance_keywords):
            importance += 3
        elif any(keyword in content_lower for keyword in medium_importance_keywords):
            importance += 2
        
        # Length-based adjustment
        if len(content) > 500:
            importance += 1
        
        # Question marks suggest engagement
        if '?' in content and source == "user":
            importance += 1
        
        return min(10, max(1, importance))
    
    def _events_to_transcript(self, events: List[SessionEvent]) -> str:
        """Convert events to readable transcript"""
        transcript = ""
        
        current_speaker = None
        for event in events:
            if event.event_type == "user_input":
                if current_speaker != "OP":
                    transcript += "\n### OP:\n"
                    current_speaker = "OP"
                transcript += f"{event.content}\n"
                
            elif event.event_type == "assistant_response":
                if current_speaker != "Sir Claude":
                    transcript += "\n### Sir Claude:\n"
                    current_speaker = "Sir Claude"
                transcript += f"{event.content}\n"
                
            elif event.event_type == "breakthrough":
                transcript += f"\n**Breakthrough**: {event.content}\n"
                
            elif event.event_type == "achievement":
                transcript += f"\n**Achievement**: {event.content}\n"
        
        return transcript
    
    def _get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True, text=True, cwd='.'
            )
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _extract_season_from_branch(self) -> int:
        """Extract season number from branch name"""
        if 'season_' in self.git_branch:
            match = re.search(r'season_(\d+)', self.git_branch)
            if match:
                return int(match.group(1))
        
        # Default fallback
        return 2  # Current season
    
    def _get_git_status(self) -> Dict[str, Any]:
        """Get git repository status"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, cwd='.'
            )
            
            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            return {
                "clean": len(lines) == 0,
                "modified_files": len([l for l in lines if l.startswith(' M')]),
                "new_files": len([l for l in lines if l.startswith('??')]),
                "staged_files": len([l for l in lines if l.startswith('A ')])
            }
        except:
            return {"error": "Could not get git status"}
    
    def _get_recent_commits(self, limit: int = 5) -> List[Dict[str, str]]:
        """Get recent git commits"""
        try:
            result = subprocess.run([
                'git', 'log', f'--max-count={limit}', 
                '--pretty=format:%H|%s|%an|%ad', '--date=iso'
            ], capture_output=True, text=True, cwd='.')
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    hash_val, subject, author, date = line.split('|', 3)
                    commits.append({
                        'hash': hash_val,
                        'subject': subject,
                        'author': author,
                        'date': date
                    })
            
            return commits
        except:
            return []
    
    def _commit_has_documentation(self, commit: Dict[str, str]) -> bool:
        """Check if commit has associated documentation"""
        # Simple heuristic - check if commit message mentions episodes
        subject = commit.get('subject', '').lower()
        return any(keyword in subject for keyword in ['episode', 'session', 'transcript'])
    
    def _analyze_episode_file(self, episode_file: Path) -> Dict[str, Any]:
        """Analyze episode file for themes and achievements"""
        try:
            with open(episode_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract themes (simple keyword matching)
            themes = []
            theme_keywords = {
                'cognitive': ['brain', 'memory', 'learning', 'cognitive'],
                'optimization': ['optimize', 'efficiency', 'performance', 'speed'],
                'tools': ['tool', 'parser', 'script', 'automation'],
                'hardware': ['pcb', 'schematic', 'component', 'circuit'],
                'software': ['code', 'function', 'class', 'algorithm']
            }
            
            content_lower = content.lower()
            for theme, keywords in theme_keywords.items():
                if any(keyword in content_lower for keyword in keywords):
                    themes.append(theme)
            
            # Extract achievements (look for achievement patterns)
            achievements = re.findall(r'\*\*Achievement[:\s]+([^*\n]+)', content, re.IGNORECASE)
            
            return {
                "file": episode_file.name,
                "themes": themes,
                "achievements": achievements,
                "word_count": len(content.split()),
                "last_modified": episode_file.stat().st_mtime
            }
        except:
            return {"error": f"Could not analyze {episode_file.name}"}
    
    def _load_episode_from_file(self, episode_file: Path):
        """Load episode metadata from existing file"""
        # Extract episode info from filename
        match = re.search(r'episode_(\d+)_([^.]+)', episode_file.name)
        if not match:
            return
        
        episode_num = int(match.group(1))
        title = match.group(2).replace('_', ' ').title()
        
        self.current_episode = Episode(
            season=self.current_season,
            episode_number=episode_num,
            title=title,
            file_path=str(episode_file),
            started_time=episode_file.stat().st_ctime,
            last_updated=episode_file.stat().st_mtime,
            status="active"
        )
        
        print(f"📂 Loaded episode: {title}")
    
    def _generate_episode_summary(self, manual_summary: str = None):
        """Generate summary for completed episode"""
        if not self.current_episode:
            return
        
        summary = f"\n\n## Episode Summary\n"
        
        if manual_summary:
            summary += f"{manual_summary}\n\n"
        
        if self.current_episode.key_insights:
            summary += "**Key Insights:**\n"
            for insight in self.current_episode.key_insights:
                summary += f"- {insight}\n"
            summary += "\n"
        
        if self.current_episode.achievements:
            summary += "**Achievements:**\n"
            for achievement in self.current_episode.achievements:
                summary += f"- {achievement}\n"
            summary += "\n"
        
        # Add session statistics
        duration_hours = (time.time() - self.current_episode.started_time) / 3600
        summary += f"**Session Stats:**\n"
        summary += f"- Duration: {duration_hours:.1f} hours\n"
        summary += f"- Events logged: {len(self.current_episode.events)}\n"
        summary += f"- Breakthroughs: {len([e for e in self.current_episode.events if e.event_type == 'breakthrough'])}\n"
        
        # Append to episode file
        with open(self.current_episode.file_path, 'a', encoding='utf-8') as f:
            f.write(summary)
    
    def _save_episode_metadata(self):
        """Save episode metadata to separate file"""
        if not self.current_episode:
            return
        
        metadata_file = Path(self.current_episode.file_path).with_suffix('.meta.json')
        
        metadata = {
            "season": self.current_episode.season,
            "episode": self.current_episode.episode_number,
            "title": self.current_episode.title,
            "started": self.current_episode.started_time,
            "completed": time.time(),
            "status": self.current_episode.status,
            "events_count": len(self.current_episode.events),
            "insights_count": len(self.current_episode.key_insights),
            "achievements_count": len(self.current_episode.achievements)
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

# CLI interface
if __name__ == "__main__":
    import sys
    
    sync = TranscriptSync()
    
    if len(sys.argv) < 2:
        status = sync.get_sync_status()
        print("📝 Transcript Sync Status:")
        print(f"   Current Episode: {status['current_episode']['title'] or 'None'}")
        print(f"   Events buffered: {status['current_episode']['events_count']}")
        print(f"   Session duration: {status['session_info']['duration_minutes']:.1f} minutes")
        print(f"   Season: {status['session_info']['season']}")
        print("\nCommands:")
        print("  start <title>        - Start new episode")
        print("  log <type> <text>    - Log event (user/response/breakthrough/achievement)")
        print("  update <content>     - Update current episode")
        print("  complete [summary]   - Complete current episode")
        print("  status              - Show sync status")
        print("  season              - Generate season summary")
        sys.exit(0)
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    if cmd == 'start' and args:
        sync.start_episode(' '.join(args))
    
    elif cmd == 'log' and len(args) >= 2:
        event_type = args[0]
        content = ' '.join(args[1:])
        
        if event_type == 'user':
            sync.log_user_input(content)
        elif event_type == 'response':
            sync.log_assistant_response(content)
        elif event_type == 'breakthrough':
            sync.log_breakthrough(content)
        elif event_type == 'achievement':
            sync.log_achievement(content)
    
    elif cmd == 'update' and args:
        sync.update_episode(' '.join(args))
    
    elif cmd == 'complete':
        summary = ' '.join(args) if args else None
        sync.complete_episode(summary)
    
    elif cmd == 'status':
        git_sync = sync.sync_with_git()
        print("🔄 Git Sync Status:")
        print(json.dumps(git_sync, indent=2))
    
    elif cmd == 'season':
        summary = sync.generate_season_summary()
        print("📊 Season Summary:")
        print(json.dumps(summary, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")