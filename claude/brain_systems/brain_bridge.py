#!/usr/bin/env python3
"""
Brain Systems Communication Bridge v1.0
Enables efficient communication between brain systems
Created during autonomous learning cycle
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Callable, List

class BrainBridge:
    """Communication bridge between brain systems"""
    
    def __init__(self):
        self.channels = {}
        self.message_queue = []
        self.subscribers = {}
        self.bridge_path = Path("claude/brain_systems/bridge_data")
        self.bridge_path.mkdir(exist_ok=True)
        
        print("[BRIDGE] Brain systems communication bridge initialized")
    
    def create_channel(self, channel_name: str):
        """Create communication channel"""
        self.channels[channel_name] = {
            "created": time.time(),
            "messages": [],
            "subscribers": [],
            "message_count": 0
        }
        
        print(f"[BRIDGE] Created channel: {channel_name}")
    
    def publish(self, channel: str, message: Dict[str, Any], sender: str = "unknown"):
        """Publish message to channel"""
        if channel not in self.channels:
            self.create_channel(channel)
        
        msg = {
            "id": self.channels[channel]["message_count"],
            "timestamp": time.time(),
            "sender": sender,
            "data": message
        }
        
        self.channels[channel]["messages"].append(msg)
        self.channels[channel]["message_count"] += 1
        
        # Notify subscribers
        for subscriber in self.channels[channel]["subscribers"]:
            try:
                subscriber(msg)
            except Exception as e:
                print(f"[BRIDGE WARNING] Subscriber error: {e}")
        
        # Persist to disk for cross-session communication
        self._persist_message(channel, msg)
        
        return msg["id"]
    
    def subscribe(self, channel: str, callback: Callable):
        """Subscribe to channel messages"""
        if channel not in self.channels:
            self.create_channel(channel)
        
        self.channels[channel]["subscribers"].append(callback)
        print(f"[BRIDGE] New subscriber to {channel}")
    
    def get_messages(self, channel: str, since: float = 0, limit: int = 100) -> List[Dict]:
        """Get messages from channel since timestamp"""
        if channel not in self.channels:
            return []
        
        filtered = [msg for msg in self.channels[channel]["messages"] 
                   if msg["timestamp"] > since]
        
        return filtered[-limit:] if limit else filtered
    
    def get_latest_message(self, channel: str) -> Dict[str, Any]:
        """Get latest message from channel"""
        if channel not in self.channels or not self.channels[channel]["messages"]:
            return None
        
        return self.channels[channel]["messages"][-1]
    
    def _persist_message(self, channel: str, message: Dict[str, Any]):
        """Persist message to disk"""
        try:
            channel_file = self.bridge_path / f"{channel}.json"
            
            # Load existing messages
            if channel_file.exists():
                with open(channel_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"channel": channel, "messages": []}
            
            # Add new message
            data["messages"].append(message)
            
            # Keep only last 1000 messages
            data["messages"] = data["messages"][-1000:]
            
            # Save back
            with open(channel_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"[BRIDGE WARNING] Could not persist message: {e}")
    
    def load_persisted_messages(self, channel: str):
        """Load persisted messages from disk"""
        try:
            channel_file = self.bridge_path / f"{channel}.json"
            
            if channel_file.exists():
                with open(channel_file, 'r') as f:
                    data = json.load(f)
                
                if channel not in self.channels:
                    self.create_channel(channel)
                
                self.channels[channel]["messages"] = data.get("messages", [])
                self.channels[channel]["message_count"] = len(self.channels[channel]["messages"])
                
                print(f"[BRIDGE] Loaded {len(self.channels[channel]['messages'])} persisted messages for {channel}")
                
        except Exception as e:
            print(f"[BRIDGE WARNING] Could not load persisted messages: {e}")
    
    def broadcast(self, message: Dict[str, Any], sender: str = "system"):
        """Broadcast message to all channels"""
        for channel in self.channels:
            self.publish(channel, message, sender)
    
    def get_channel_stats(self) -> Dict[str, Any]:
        """Get statistics about all channels"""
        stats = {}
        
        for channel_name, channel_data in self.channels.items():
            stats[channel_name] = {
                "message_count": len(channel_data["messages"]),
                "subscriber_count": len(channel_data["subscribers"]),
                "created": channel_data["created"],
                "last_message": channel_data["messages"][-1]["timestamp"] if channel_data["messages"] else None
            }
        
        return stats
    
    def cleanup_old_messages(self, max_age_hours: int = 24):
        """Clean up old messages to save memory"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned_count = 0
        
        for channel_data in self.channels.values():
            original_count = len(channel_data["messages"])
            channel_data["messages"] = [
                msg for msg in channel_data["messages"] 
                if msg["timestamp"] > cutoff_time
            ]
            cleaned_count += original_count - len(channel_data["messages"])
        
        print(f"[BRIDGE] Cleaned {cleaned_count} old messages")
        return cleaned_count

# Predefined channels for brain systems
CHANNELS = {
    "PCB_UPDATES": "pcb_design_updates",
    "LEARNING": "learning_insights", 
    "PATTERNS": "pattern_detection",
    "VELOCITY": "velocity_improvements",
    "ERRORS": "error_reports",
    "TOOLS": "tool_creation"
}

# Global bridge instance
brain_bridge = BrainBridge()

# Initialize common channels
for channel in CHANNELS.values():
    brain_bridge.create_channel(channel)
    brain_bridge.load_persisted_messages(channel)

# Convenience functions
def publish_learning_insight(insight: str, source: str = "unknown"):
    """Publish learning insight to learning channel"""
    return brain_bridge.publish(CHANNELS["LEARNING"], {
        "insight": insight,
        "source": source,
        "type": "learning"
    }, source)

def publish_pattern(pattern_type: str, pattern_data: Dict[str, Any], source: str = "pattern_engine"):
    """Publish detected pattern"""
    return brain_bridge.publish(CHANNELS["PATTERNS"], {
        "pattern_type": pattern_type,
        "data": pattern_data,
        "type": "pattern"
    }, source)

def publish_velocity_improvement(improvement: Dict[str, Any], source: str = "velocity_optimizer"):
    """Publish velocity improvement"""
    return brain_bridge.publish(CHANNELS["VELOCITY"], {
        "improvement": improvement,
        "type": "velocity"
    }, source)

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("[BRIDGE] Brain Systems Communication Bridge")
        print("Commands:")
        print("  stats           - Show channel statistics")
        print("  publish <ch> <msg> - Publish message to channel")
        print("  subscribe <ch>  - Subscribe to channel (prints messages)")
        print("  cleanup         - Clean old messages")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "stats":
        stats = brain_bridge.get_channel_stats()
        for channel, data in stats.items():
            print(f"[{channel}] Messages: {data['message_count']}, Subscribers: {data['subscriber_count']}")
    
    elif cmd == "publish" and len(sys.argv) > 3:
        channel = sys.argv[2]
        message = sys.argv[3]
        msg_id = brain_bridge.publish(channel, {"content": message}, "cli")
        print(f"[PUBLISHED] Message {msg_id} to {channel}")
    
    elif cmd == "cleanup":
        cleaned = brain_bridge.cleanup_old_messages()
        print(f"[CLEANED] {cleaned} old messages removed")
    
    else:
        print(f"[ERROR] Unknown command: {cmd}")