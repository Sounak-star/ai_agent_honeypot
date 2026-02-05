"""
Scam detection engine with keyword-based scoring
"""

import logging

logger = logging.getLogger(__name__)

# Enhanced scam signal dictionary with weights
SCAM_SIGNALS = {
    # Urgency indicators (high weight)
    "urgent": 2,
    "urgently": 2,
    "immediately": 2,
    "right now": 2,
    "asap": 2,
    "hurry": 2,
    "quick": 1,
    "fast": 1,
    
    # Account/Security threats (very high weight)
    "blocked": 3,
    "suspended": 3,
    "locked": 3,
    "frozen": 3,
    "account suspended": 4,
    "account blocked": 4,
    "will be blocked": 3,
    "will be suspended": 3,
    
    # Verification/Action requests (medium-high weight)
    "verify": 2,
    "confirm": 2,
    "update": 2,
    "validate": 2,
    "authenticate": 2,
    "reactivate": 2,
    
    # Financial terms (medium weight)
    "bank": 1,
    "upi": 3,
    "account": 1,
    "payment": 1,
    "transaction": 1,
    "refund": 2,
    "pending": 1,
    "debit": 2,
    "credit": 1,
    
    # Action requests (high weight)
    "click": 2,
    "click here": 3,
    "tap": 2,
    "download": 2,
    "install": 2,
    "share": 2,
    "provide": 2,
    "send": 2,
    
    # Information requests (medium weight)
    "otp": 3,
    "password": 3,
    "pin": 3,
    "cvv": 4,
    "card number": 4,
    "account number": 3,
    "details": 1,
    
    # Authority claims (medium weight)
    "bank representative": 2,
    "customer care": 2,
    "support team": 2,
    "official": 1,
    
    # Threat indicators (medium weight)
    "lose": 2,
    "lost": 2,
    "expire": 2,
    "expired": 2,
    "limited time": 2,
    "deadline": 2,
}

# Detection threshold
THRESHOLD = 4


def detect_scam_score(text: str) -> int:
    """
    Calculate scam score based on keyword matches
    
    Args:
        text: Message text to analyze
    
    Returns:
        Integer scam score
    """
    if not text:
        return 0
    
    text_lower = text.lower()
    score = 0
    matched_keywords = []
    
    # Check for each scam signal
    for keyword, weight in SCAM_SIGNALS.items():
        if keyword in text_lower:
            score += weight
            matched_keywords.append(keyword)
    
    if matched_keywords:
        logger.info(f"Scam signals detected: {matched_keywords} (score: {score})")
    
    return score


def is_scam(text: str) -> bool:
    """
    Determine if text is likely a scam
    
    Args:
        text: Message text to analyze
    
    Returns:
        Boolean indicating if text exceeds scam threshold
    """
    score = detect_scam_score(text)
    return score >= THRESHOLD


def analyze_message(text: str) -> dict:
    """
    Provide detailed analysis of a message
    
    Args:
        text: Message text to analyze
    
    Returns:
        Dictionary with analysis results
    """
    score = detect_scam_score(text)
    is_scam_flag = is_scam(text)
    
    text_lower = text.lower()
    matched_signals = [
        {"keyword": k, "weight": w}
        for k, w in SCAM_SIGNALS.items()
        if k in text_lower
    ]
    
    return {
        "scamScore": score,
        "isScam": is_scam_flag,
        "threshold": THRESHOLD,
        "matchedSignals": matched_signals,
        "riskLevel": "high" if score >= 8 else "medium" if score >= 4 else "low"
    }


def test_detector():
    """Test function for the detector"""
    test_messages = [
        "Hello, how are you?",
        "Your account has been blocked. Click here to verify immediately!",
        "Urgent: Share your OTP to reactivate your suspended UPI account",
        "Your bank account will be frozen. Provide card details now.",
    ]
    
    print("\n=== Scam Detector Tests ===\n")
    for msg in test_messages:
        analysis = analyze_message(msg)
        print(f"Message: {msg}")
        print(f"Analysis: {analysis}")
        print(f"---\n")


if __name__ == "__main__":
    # Run tests
    logging.basicConfig(level=logging.INFO)
    test_detector()