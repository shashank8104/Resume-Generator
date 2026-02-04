"""Session management for API requests"""

import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class SessionManager:
    """Manage user sessions and request history"""
    
    def __init__(self, session_timeout: int = 3600):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = session_timeout  # seconds
        self.session_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        logger.info("Session manager initialized")
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "request_count": 0,
            "is_active": True
        }
        
        logger.info(f"Created session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session has expired
        if self._is_session_expired(session):
            self.destroy_session(session_id)
            return None
        
        return session
    
    def update_session_activity(self, session_id: str):
        """Update session last activity timestamp"""
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.now()
            self.sessions[session_id]["request_count"] += 1
    
    def destroy_session(self, session_id: str) -> bool:
        """Destroy a session"""
        if session_id in self.sessions:
            self.sessions[session_id]["is_active"] = False
            del self.sessions[session_id]
            logger.info(f"Destroyed session: {session_id}")
            return True
        
        return False
    
    def add_request_to_history(
        self, 
        session_id: str, 
        endpoint: str, 
        method: str,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        execution_time: Optional[float] = None
    ):
        """Add request to session history"""
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "request_data": request_data,
            "response_data": response_data,
            "execution_time": execution_time,
            "status": "success" if response_data and response_data.get("success") else "error"
        }
        
        self.session_history[session_id].append(history_entry)
        
        # Limit history size per session
        max_history_size = 100
        if len(self.session_history[session_id]) > max_history_size:
            self.session_history[session_id] = self.session_history[session_id][-max_history_size:]
    
    def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get session request history"""
        history = self.session_history.get(session_id, [])
        return history[-limit:] if limit else history
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        active_sessions = []
        
        for session_id, session in self.sessions.items():
            if session["is_active"] and not self._is_session_expired(session):
                active_sessions.append(session)
            elif self._is_session_expired(session):
                # Clean up expired session
                self.destroy_session(session_id)
        
        return active_sessions
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.destroy_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        active_sessions = self.get_active_sessions()
        
        stats = {
            "total_active_sessions": len(active_sessions),
            "total_session_history": len(self.session_history),
            "session_timeout": self.session_timeout,
            "average_requests_per_session": 0,
            "most_active_session": None
        }
        
        if active_sessions:
            total_requests = sum(session["request_count"] for session in active_sessions)
            stats["average_requests_per_session"] = total_requests / len(active_sessions)
            
            # Find most active session
            most_active = max(active_sessions, key=lambda s: s["request_count"])
            stats["most_active_session"] = {
                "session_id": most_active["session_id"],
                "request_count": most_active["request_count"],
                "created_at": most_active["created_at"].isoformat()
            }
        
        return stats
    
    def _is_session_expired(self, session: Dict[str, Any]) -> bool:
        """Check if a session has expired"""
        last_activity = session["last_activity"]
        expiry_time = last_activity + timedelta(seconds=self.session_timeout)
        return datetime.now() > expiry_time