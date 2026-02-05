"""
In-memory session storage (fallback when Redis is unavailable)
"""

import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

# Global in-memory session store
sessions: Dict[str, dict] = {}


def cleanup_old_sessions(max_age_seconds: int = 86400):
    """
    Clean up sessions older than max_age_seconds
    
    Args:
        max_age_seconds: Maximum age in seconds (default: 24 hours)
    """
    if not sessions:
        return
    
    current_time = datetime.utcnow().timestamp()
    to_delete = []
    
    for session_id, session_data in sessions.items():
        # Check if session has lastUpdated timestamp
        if "lastUpdated" in session_data:
            try:
                last_updated = datetime.fromisoformat(session_data["lastUpdated"]).timestamp()
                if current_time - last_updated > max_age_seconds:
                    to_delete.append(session_id)
            except:
                pass
    
    # Delete old sessions
    for session_id in to_delete:
        del sessions[session_id]
        logger.info(f"🗑️ Cleaned up old session: {session_id}")
    
    if to_delete:
        logger.info(f"🧹 Cleaned up {len(to_delete)} old sessions")


def get_session_count() -> int:
    """
    Get the number of active sessions in memory
    
    Returns:
        Number of sessions
    """
    return len(sessions)


def get_session_stats() -> dict:
    """
    Get statistics about in-memory sessions
    
    Returns:
        Dictionary with session statistics
    """
    total_messages = sum(len(s.get("messages", [])) for s in sessions.values())
    scam_detected_count = sum(1 for s in sessions.values() if s.get("scamDetected", False))
    
    return {
        "total_sessions": len(sessions),
        "total_messages": total_messages,
        "scam_detected": scam_detected_count,
        "average_messages_per_session": total_messages / len(sessions) if sessions else 0
    }


if __name__ == "__main__":
    # Test in-memory storage
    logging.basicConfig(level=logging.INFO)
    
    print("\n=== Memory Storage Tests ===\n")
    
    # Add test sessions
    sessions["test-1"] = {
        "sessionId": "test-1",
        "messages": [{"sender": "user", "text": "test"}],
        "scamDetected": True,
        "lastUpdated": datetime.utcnow().isoformat()
    }
    
    sessions["test-2"] = {
        "sessionId": "test-2",
        "messages": [{"sender": "user", "text": "hello"}],
        "scamDetected": False,
        "lastUpdated": datetime.utcnow().isoformat()
    }
    
    stats = get_session_stats()
    print(f"Session stats: {stats}")
    
    # Test cleanup
    cleanup_old_sessions(0)  # Clean all for testing
    print(f"Sessions after cleanup: {get_session_count()}")