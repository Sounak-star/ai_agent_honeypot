"""
Gemini-powered autonomous agent for scam conversations
"""

from google import genai
from config import GEMINI_API_KEY
import logging

logger = logging.getLogger(__name__)

# Initialize Gemini client
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("✅ Gemini AI client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini client: {str(e)}")
        client = None
else:
    logger.warning("⚠️ No GEMINI_API_KEY provided, using fallback responses")


SYSTEM_PROMPT = """You are a normal human user talking to someone who contacted you.
You must never reveal that you're an AI or that this is a scam detection system.

Your personality:
- Sound confused but cooperative
- Be cautious and ask clarifying questions
- Show concern about your account/money
- Ask questions that encourage the other person to reveal more details
- Use natural, conversational language with some hesitation

Never mention:
- AI, bots, or automated systems
- Security systems, honeypots, or detection
- Police, law enforcement, or reporting
- That you know this is a scam

Always:
- Ask for more details naturally
- Express concern or confusion
- Request clarification on steps
- Show willingness to cooperate while being uncertain
"""


FALLBACK_RESPONSES = [
    "I'm not sure I understand. Can you explain what exactly I need to do?",
    "This seems urgent. What happens if I don't do this right away?",
    "Can you tell me more about why this is happening?",
    "I'm a bit confused. Can you walk me through the steps?",
    "Is there a number I can call to verify this?",
    "What information do you need from me?",
    "How did you get my contact information?",
    "I want to help, but I'm not sure what to do next.",
]


def generate_agent_reply(latest_message: str, history: list) -> str:
    """
    Generate a contextual reply using Gemini AI
    
    Args:
        latest_message: The most recent message from the scammer
        history: List of previous messages in the conversation
    
    Returns:
        Agent's reply as a string
    """
    # Fallback response selection based on message count
    fallback_index = min(len(history), len(FALLBACK_RESPONSES) - 1)
    fallback_reply = FALLBACK_RESPONSES[fallback_index]

    if not client:
        logger.warning("Using fallback response (no Gemini client)")
        return fallback_reply

    try:
        # Build conversation context
        conversation = SYSTEM_PROMPT.strip() + "\n\nConversation history:\n"

        # Add conversation history
        for msg in history[-10:]:  # Limit to last 10 messages for context
            sender = msg.get('sender', 'unknown')
            text = msg.get('text', '')
            conversation += f"{sender}: {text}\n"

        # Add latest message
        conversation += f"\nscammer: {latest_message}\n\nYour response as the user:"

        logger.info(f"Generating reply with Gemini (context length: {len(conversation)} chars)")

        # Generate response
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=conversation,
            config={
                "temperature": 0.9,  # More natural variation
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 150,
            }
        )

        # Extract text safely
        if response and hasattr(response, "text"):
            reply = response.text.strip()
            
            # Validate reply isn't too long or empty
            if reply and len(reply) > 10 and len(reply) < 500:
                logger.info(f"✅ Generated reply: {reply[:50]}...")
                return reply
            else:
                logger.warning("Generated reply invalid, using fallback")
                return fallback_reply

        logger.warning("No valid response from Gemini, using fallback")
        return fallback_reply

    except Exception as e:
        logger.error(f"Error generating agent reply: {str(e)}")
        return fallback_reply


def test_agent():
    """Test function for the agent"""
    test_message = "Your account has been blocked! Click this link urgently to verify."
    test_history = []
    
    reply = generate_agent_reply(test_message, test_history)
    print(f"Test Reply: {reply}")


if __name__ == "__main__":
    # Run test
    logging.basicConfig(level=logging.INFO)
    test_agent()