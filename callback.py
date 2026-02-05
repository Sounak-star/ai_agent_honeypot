"""
Callback handler for sending final results to GUVI
"""

import requests
import logging
from typing import Optional
from config import GUVI_CALLBACK_URL

logger = logging.getLogger(__name__)


def send_final_callback(payload: dict, max_retries: int = 3) -> bool:
    """
    Send final scam detection results to GUVI callback endpoint
    
    Args:
        payload: Dictionary containing scam detection results
        max_retries: Maximum number of retry attempts
    
    Returns:
        Boolean indicating success
    """
    if not GUVI_CALLBACK_URL:
        logger.warning("⚠️ No GUVI_CALLBACK_URL configured, skipping callback")
        return False
    
    logger.info(f"📤 Sending callback to {GUVI_CALLBACK_URL}")
    logger.info(f"Payload: {payload}")
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                GUVI_CALLBACK_URL,
                json=payload,
                timeout=10,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'AI-Agentic-Honeypot/2.0'
                }
            )
            
            # Check response status
            if response.status_code == 200:
                logger.info(f"✅ Callback successful (attempt {attempt + 1}/{max_retries})")
                logger.info(f"Response: {response.text}")
                return True
            else:
                logger.warning(
                    f"⚠️ Callback failed with status {response.status_code} "
                    f"(attempt {attempt + 1}/{max_retries}): {response.text}"
                )
        
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ Callback timeout (attempt {attempt + 1}/{max_retries})")
        
        except requests.exceptions.ConnectionError:
            logger.warning(f"🔌 Connection error (attempt {attempt + 1}/{max_retries})")
        
        except Exception as e:
            logger.error(
                f"❌ Callback error (attempt {attempt + 1}/{max_retries}): {str(e)}"
            )
    
    logger.error(f"❌ All callback attempts failed after {max_retries} retries")
    return False


def test_callback():
    """Test the callback functionality"""
    test_payload = {
        "sessionId": "test-session-123",
        "scamDetected": True,
        "totalMessagesExchanged": 10,
        "extractedIntelligence": {
            "bankAccounts": ["1234567890123456"],
            "upiIds": ["scammer@paytm"],
            "phishingLinks": ["https://fake-bank.com"],
            "phoneNumbers": ["+919876543210"],
            "suspiciousKeywords": ["urgent", "blocked", "verify"]
        },
        "agentNotes": "Test scam detection",
        "finalScamScore": 15
    }
    
    result = send_final_callback(test_payload)
    print(f"Callback test result: {'Success' if result else 'Failed'}")


if __name__ == "__main__":
    # Run test
    logging.basicConfig(level=logging.INFO)
    test_callback()