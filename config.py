"""
Configuration management with environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_KEY = os.getenv("API_KEY", "YOUR_SECRET_API_KEY")

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# GUVI Callback URL
GUVI_CALLBACK_URL = os.getenv(
    "GUVI_CALLBACK_URL",
    "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
)

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "")

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SCAM_DETECTION_THRESHOLD = int(os.getenv("SCAM_DETECTION_THRESHOLD", "4"))
MIN_MESSAGES_FOR_CALLBACK = int(os.getenv("MIN_MESSAGES_FOR_CALLBACK", "8"))

# Session Configuration
SESSION_TTL = int(os.getenv("SESSION_TTL", "86400"))  # 24 hours in seconds

# Agent Configuration
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.9"))
AGENT_MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "150"))


def validate_config() -> dict:
    """
    Validate configuration and return status
    
    Returns:
        Dictionary with validation results
    """
    issues = []
    warnings = []
    
    # Check critical configurations
    if API_KEY == "YOUR_SECRET_API_KEY":
        warnings.append("API_KEY is using default value - please set a secure key")
    
    if not GEMINI_API_KEY:
        warnings.append("GEMINI_API_KEY not set - agent will use fallback responses")
    
    if not REDIS_URL:
        warnings.append("REDIS_URL not set - using in-memory storage (not persistent)")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "config": {
            "api_key_set": bool(API_KEY and API_KEY != "YOUR_SECRET_API_KEY"),
            "gemini_key_set": bool(GEMINI_API_KEY),
            "redis_url_set": bool(REDIS_URL),
            "guvi_callback_url": GUVI_CALLBACK_URL,
            "log_level": LOG_LEVEL,
            "scam_threshold": SCAM_DETECTION_THRESHOLD,
            "min_messages_for_callback": MIN_MESSAGES_FOR_CALLBACK,
        }
    }


if __name__ == "__main__":
    # Display configuration status
    import json
    
    print("\n=== Configuration Status ===\n")
    status = validate_config()
    print(json.dumps(status, indent=2))
    
    if status["warnings"]:
        print("\n⚠️ Warnings:")
        for warning in status["warnings"]:
            print(f"  - {warning}")
    
    if status["issues"]:
        print("\n❌ Issues:")
        for issue in status["issues"]:
            print(f"  - {issue}")
    
    if not status["warnings"] and not status["issues"]:
        print("\n✅ Configuration is valid!")