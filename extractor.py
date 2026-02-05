"""
Intelligence extraction from text messages
Extracts bank accounts, UPI IDs, phone numbers, URLs, and emails
"""

import re
import logging

logger = logging.getLogger(__name__)


def extract_intelligence(text: str) -> dict:
    """
    Extract various types of intelligence from text
    
    Args:
        text: Message text to analyze
    
    Returns:
        Dictionary containing extracted intelligence
    """
    if not text:
        return {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": [],
            "emailAddresses": []
        }
    
    # Extract bank account numbers (12-16 digits)
    bank_accounts = list(set(re.findall(r'\b\d{12,16}\b', text)))
    
    # Extract UPI IDs
    upi_ids = list(set(re.findall(r'[a-zA-Z0-9._-]+@[a-zA-Z0-9]+', text)))
    # Filter to common UPI handles
    upi_ids = [uid for uid in upi_ids if any(handle in uid.lower() for handle in 
               ['@upi', '@paytm', '@ybl', '@oksbi', '@okaxis', '@okicici', '@okhdfcbank'])]
    
    # Extract URLs
    urls = list(set(re.findall(r'https?://\S+', text)))
    
    # Extract phone numbers (Indian format)
    phone_patterns = [
        r'\+91[-\s]?\d{10}',  # +91 with optional separator
        r'\b91\d{10}\b',       # 91 followed by 10 digits
        r'\b[6-9]\d{9}\b'      # 10 digit starting with 6-9
    ]
    phone_numbers = []
    for pattern in phone_patterns:
        phone_numbers.extend(re.findall(pattern, text))
    phone_numbers = list(set(phone_numbers))
    
    # Extract email addresses
    email_addresses = list(set(re.findall(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        text
    )))
    
    # Extract suspicious keywords
    suspicious_keywords_list = [
        "urgent", "urgently", "verify", "blocked", "suspended",
        "click", "otp", "password", "pin", "cvv", "account number",
        "card number", "immediately", "expire", "frozen", "locked"
    ]
    
    text_lower = text.lower()
    found_keywords = list(set([
        kw for kw in suspicious_keywords_list if kw in text_lower
    ]))
    
    intelligence = {
        "bankAccounts": bank_accounts,
        "upiIds": upi_ids,
        "phishingLinks": urls,
        "phoneNumbers": phone_numbers,
        "suspiciousKeywords": found_keywords,
        "emailAddresses": email_addresses
    }
    
    # Log extracted intelligence
    if any(intelligence.values()):
        logger.info(f"🔍 Intelligence extracted: {intelligence}")
    
    return intelligence


def extract_and_categorize(text: str) -> dict:
    """
    Extract intelligence and categorize by risk level
    
    Args:
        text: Message text to analyze
    
    Returns:
        Dictionary with categorized intelligence
    """
    intel = extract_intelligence(text)
    
    # Calculate risk score based on extracted data
    risk_score = 0
    if intel["bankAccounts"]:
        risk_score += 5 * len(intel["bankAccounts"])
    if intel["upiIds"]:
        risk_score += 4 * len(intel["upiIds"])
    if intel["phishingLinks"]:
        risk_score += 3 * len(intel["phishingLinks"])
    if intel["phoneNumbers"]:
        risk_score += 2 * len(intel["phoneNumbers"])
    
    return {
        **intel,
        "riskScore": risk_score,
        "riskLevel": "critical" if risk_score >= 10 else "high" if risk_score >= 5 else "medium" if risk_score > 0 else "low"
    }


def test_extractor():
    """Test function for the extractor"""
    test_texts = [
        "Call me at +91 9876543210",
        "Transfer to account 1234567890123456 or UPI id test@paytm",
        "Click https://fake-bank.com and share your OTP immediately",
        "Contact support@scam.com for urgent account verification",
        "Your bank account 9876543210987654 is blocked! Pay to 123@ybl"
    ]
    
    print("\n=== Intelligence Extractor Tests ===\n")
    for text in test_texts:
        result = extract_and_categorize(text)
        print(f"Text: {text}")
        print(f"Extracted: {result}")
        print(f"---\n")


if __name__ == "__main__":
    # Run tests
    logging.basicConfig(level=logging.INFO)
    test_extractor()