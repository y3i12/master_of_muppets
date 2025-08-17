#!/usr/bin/env python3
"""
Session Daemon Manager - Auto-start meta-cognitive daemons
Ensures meta-learning daemons are running at session start
"""

import asyncio
import atexit
import threading
import time
from typing import Dict, Any, Optional
from pathlib import Path

from .meta_cognitive_architecture import (
    initialize_meta_cognitive_system, 
    get_meta_cognitive_insights,
    _global_meta_cognitive_system
)

class SessionDaemonManager:
    """Manages daemon lifecycle across user sessions"""
    
    def __init__(self):
        self.session_active = False
        self.startup_complete = False
        self.background_thread = None
        self.daemon_status = {}
        
    async def auto_start_daemons(self) -> Dict[str, Any]:
        """Auto-start daemons when session begins"""
        if self.startup_complete:
            return {
                'status': 'already_running',
                'message': 'Daemons already active from previous session'
            }
        
        print("[SESSION] Auto-starting meta-cognitive daemons...")
        
        try:
            # Initialize meta-cognitive system
            bootstrap_result = await initialize_meta_cognitive_system()
            
            # Mark session as active
            self.session_active = True
            self.startup_complete = True
            
            # Register cleanup on exit
            atexit.register(self._cleanup_on_exit)
            
            # Get initial status
            insights = await get_meta_cognitive_insights()
            
            self.daemon_status = {
                'bootstrap_result': bootstrap_result,
                'initial_insights': insights,
                'startup_time': time.time(),
                'auto_started': True
            }
            
            print(f"[SESSION] ✅ Daemons started: {bootstrap_result.get('daemons_active', 0)} active")
            
            return self.daemon_status
            
        except Exception as e:
            print(f"[SESSION] ❌ Daemon startup failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'auto_started': False
            }
    
    def _cleanup_on_exit(self):
        """Cleanup daemons on session exit"""
        if self.session_active:
            print("[SESSION] Session ending, saving daemon state...")
            # This will be called automatically on exit
            if _global_meta_cognitive_system:
                # Create new event loop for cleanup if needed
                try:
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(_global_meta_cognitive_system.shutdown())
                except RuntimeError:
                    # Create new loop if current one is closed
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(_global_meta_cognitive_system.shutdown())
                    loop.close()
    
    async def get_daemon_status(self) -> Dict[str, Any]:
        """Get current daemon status"""
        if not self.session_active:
            return {
                'status': 'inactive',
                'message': 'Daemons not started yet'
            }
        
        current_insights = await get_meta_cognitive_insights()
        
        return {
            'status': 'active',
            'session_active': self.session_active,
            'startup_complete': self.startup_complete,
            'current_insights': current_insights,
            'uptime_seconds': time.time() - self.daemon_status.get('startup_time', time.time())
        }
    
    async def force_restart_daemons(self) -> Dict[str, Any]:
        """Force restart all daemons"""
        print("[SESSION] Force restarting daemons...")
        
        # Shutdown existing
        if _global_meta_cognitive_system:
            await _global_meta_cognitive_system.shutdown()
        
        # Reset state
        self.session_active = False
        self.startup_complete = False
        
        # Restart
        return await self.auto_start_daemons()

# Global session manager instance
_session_manager = SessionDaemonManager()

async def ensure_daemons_running() -> Dict[str, Any]:
    """Ensure meta-cognitive daemons are running (call at session start)"""
    return await _session_manager.auto_start_daemons()

async def get_session_daemon_status() -> Dict[str, Any]:
    """Get daemon status for current session"""
    return await _session_manager.get_daemon_status()

async def restart_session_daemons() -> Dict[str, Any]:
    """Restart session daemons if needed"""
    return await _session_manager.force_restart_daemons()

# Auto-start integration - this runs when module is imported
def _auto_initialize():
    """Auto-initialize when module is imported"""
    try:
        # Start daemons in background thread to avoid blocking import
        def background_startup():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(_session_manager.auto_start_daemons())
                loop.close()
                print(f"[SESSION] Background startup complete: {result.get('status')}")
            except Exception as e:
                print(f"[SESSION] Background startup failed: {e}")
        
        # Start in daemon thread
        startup_thread = threading.Thread(target=background_startup, daemon=True)
        startup_thread.start()
        
    except Exception as e:
        print(f"[SESSION] Auto-initialization failed: {e}")

# Trigger auto-initialization when this module loads
_auto_initialize()

if __name__ == "__main__":
    # Test session daemon management
    async def test_session_daemons():
        print("Session Daemon Manager Test")
        print("=" * 40)
        
        # Ensure daemons are running
        status = await ensure_daemons_running()
        print(f"Daemon startup: {status}")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Check status
        current_status = await get_session_daemon_status()
        print(f"Current status: {current_status}")
        
        # Get insights
        insights = await get_meta_cognitive_insights()
        print(f"Meta-cognitive insights: {insights}")
    
    asyncio.run(test_session_daemons())