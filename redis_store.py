"""
Redis storage handler with connection pooling and error handling
"""

import redis
import json
import logging
from typing import Optional, Dict
from config import REDIS_URL

logger = logging.getLogger(__name__)

# Initialize Redis client with connection pooling
redis_client = None

if REDIS_URL and REDIS_URL.startswith(("redis://", "rediss://", "unix://")):
    try:
        redis_client = redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        # Test connection
        redis_client.ping()
        logger.info("✅ Redis client initialized successfully")
    except redis.ConnectionError as e:
        logger.error(f"❌ Redis connection failed: {str(e)}")
        redis_client = None
    except Exception as e:
        logger.error(f"❌ Redis initialization error: {str(e)}")
        redis_client = None
else:
    logger.warning("⚠️ No valid REDIS_URL provided, using in-memory storage")


def get_session(session_id: str) -> Optional[Dict]:
    """
    Retrieve session data from Redis
    
    Args:
        session_id: Unique session identifier
    
    Returns:
        Session dictionary or None if not found
    """
    if not redis_client:
        return None
    
    try:
        data = redis_client.get(session_id)
        if data:
            session = json.loads(data)
            logger.info(f"📥 Retrieved session: {session_id}")
            return session
        return None
    
    except redis.ConnectionError:
        logger.error(f"❌ Redis connection error while getting session {session_id}")
        return None
    
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decode error for session {session_id}: {str(e)}")
        return None
    
    except Exception as e:
        logger.error(f"❌ Error getting session {session_id}: {str(e)}")
        return None


def save_session(session_id: str, data: Dict, ttl: int = 86400) -> bool:
    """
    Save session data to Redis with TTL
    
    Args:
        session_id: Unique session identifier
        data: Session data dictionary
        ttl: Time to live in seconds (default: 24 hours)
    
    Returns:
        Boolean indicating success
    """
    if not redis_client:
        return False
    
    try:
        json_data = json.dumps(data)
        redis_client.setex(session_id, ttl, json_data)
        logger.info(f"💾 Saved session: {session_id} (TTL: {ttl}s)")
        return True
    
    except redis.ConnectionError:
        logger.error(f"❌ Redis connection error while saving session {session_id}")
        return False
    
    except Exception as e:
        logger.error(f"❌ Error saving session {session_id}: {str(e)}")
        return False


def delete_session(session_id: str) -> bool:
    """
    Delete session from Redis
    
    Args:
        session_id: Unique session identifier
    
    Returns:
        Boolean indicating success
    """
    if not redis_client:
        return False
    
    try:
        result = redis_client.delete(session_id)
        if result:
            logger.info(f"🗑️ Deleted session: {session_id}")
            return True
        return False
    
    except Exception as e:
        logger.error(f"❌ Error deleting session {session_id}: {str(e)}")
        return False


def get_all_sessions() -> list:
    """
    Get all session IDs from Redis
    
    Returns:
        List of session IDs
    """
    if not redis_client:
        return []
    
    try:
        keys = redis_client.keys("*")
        logger.info(f"📋 Retrieved {len(keys)} session keys")
        return keys
    
    except Exception as e:
        logger.error(f"❌ Error getting all sessions: {str(e)}")
        return []


def check_connection() -> bool:
    """
    Check if Redis connection is alive
    
    Returns:
        Boolean indicating connection status
    """
    if not redis_client:
        return False
    
    try:
        redis_client.ping()
        return True
    except:
        return False


def test_redis():
    """Test Redis functionality"""
    print("\n=== Redis Storage Tests ===\n")
    
    # Test connection
    print(f"Connection status: {check_connection()}")
    
    if not check_connection():
        print("⚠️ Redis not available, skipping tests")
        return
    
    # Test save
    test_session = {
        "sessionId": "test-123",
        "messages": [{"sender": "user", "text": "test", "timestamp": 123456}],
        "scamDetected": False,
        "scamScore": 0
    }
    
    save_result = save_session("test-123", test_session)
    print(f"Save test: {'✅ Success' if save_result else '❌ Failed'}")
    
    # Test get
    retrieved = get_session("test-123")
    print(f"Get test: {'✅ Success' if retrieved else '❌ Failed'}")
    print(f"Retrieved data: {retrieved}")
    
    # Test delete
    delete_result = delete_session("test-123")
    print(f"Delete test: {'✅ Success' if delete_result else '❌ Failed'}")


if __name__ == "__main__":
    # Run tests
    logging.basicConfig(level=logging.INFO)
    test_redis()