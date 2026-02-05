"""
AI Agentic Honeypot - Main API Server
A sophisticated scam detection system using Gemini AI
"""

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from config import API_KEY
from models import ChatRequest, ChatResponse, HealthResponse
from detector import is_scam, detect_scam_score
from extractor import extract_intelligence
from agent import generate_agent_reply
from callback import send_final_callback
from redis_store import get_session, save_session
from memory import sessions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Agentic Honeypot",
    description="Intelligent scam detection and intelligence gathering system",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Agentic Honeypot",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "AI Agentic Honeypot",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest, x_api_key: str = Header(None)):
    """
    Main chat endpoint for processing messages and detecting scams
    
    Args:
        body: ChatRequest containing message and session information
        x_api_key: API key for authentication
    
    Returns:
        ChatResponse with agent reply and detection status
    """
    # Authentication
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt from session {body.sessionId}")
        raise HTTPException(status_code=401, detail="Invalid API Key")

    try:
        body_dict = body.model_dump()

        # Extract message safely
        message = body_dict.get("message", {})
        text = message.get("text", "").strip()

        if not text:
            raise HTTPException(status_code=400, detail="Message text is required")

        session_id = body_dict.get("sessionId")
        logger.info(f"Processing message for session {session_id}: {text[:50]}...")

        # Get or create session
        session = get_session(session_id) or sessions.get(session_id)

        if not session:
            logger.info(f"Creating new session: {session_id}")
            session = {
                "sessionId": session_id,
                "messages": [],
                "scamDetected": False,
                "scamScore": 0,
                "intel": {
                    "bankAccounts": [],
                    "upiIds": [],
                    "phishingLinks": [],
                    "phoneNumbers": [],
                    "suspiciousKeywords": [],
                    "emailAddresses": []
                },
                "callbackSent": False,
                "createdAt": datetime.utcnow().isoformat(),
                "lastUpdated": datetime.utcnow().isoformat()
            }

        # Store message
        session["messages"].append(message)
        session["lastUpdated"] = datetime.utcnow().isoformat()

        # Scam detection
        score = detect_scam_score(text)
        session["scamScore"] += score
        
        logger.info(f"Session {session_id}: score={score}, total={session['scamScore']}")

        if is_scam(text) and not session["scamDetected"]:
            session["scamDetected"] = True
            logger.warning(f"🚨 SCAM DETECTED in session {session_id}")

        # Intelligence extraction
        intel = extract_intelligence(text)
        for key in intel:
            if key in session["intel"]:
                session["intel"][key] = list(set(session["intel"][key] + intel[key]))

        # Generate agent response
        reply = generate_agent_reply(
            text,
            body_dict.get("conversationHistory", [])
        )

        # Final callback logic
        message_count = len(session["messages"])
        if (
            session["scamDetected"]
            and message_count >= 8
            and not session["callbackSent"]
        ):
            payload = {
                "sessionId": session_id,
                "scamDetected": True,
                "totalMessagesExchanged": message_count,
                "extractedIntelligence": session["intel"],
                "agentNotes": "Multi-turn urgency-based financial scam detected",
                "finalScamScore": session["scamScore"],
                "timestamp": datetime.utcnow().isoformat()
            }
            send_final_callback(payload)
            session["callbackSent"] = True
            logger.info(f"✅ Final callback sent for session {session_id}")

        # Save session
        save_session(session_id, session)
        sessions[session_id] = session

        return {
            "status": "success",
            "reply": reply,
            "scamDetected": session["scamDetected"],
            "scamScore": session["scamScore"],
            "messageCount": message_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/session/{session_id}")
def get_session_info(session_id: str, x_api_key: str = Header(None)):
    """
    Retrieve session information
    
    Args:
        session_id: Session identifier
        x_api_key: API key for authentication
    
    Returns:
        Session data or 404 if not found
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    session = get_session(session_id) or sessions.get(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "status": "success",
        "session": session
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)