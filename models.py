"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class Message(BaseModel):
    """Individual message in a conversation"""
    sender: str = Field(..., description="Message sender (user/scammer)")
    text: str = Field(..., description="Message content")
    timestamp: int = Field(..., description="Unix timestamp")


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    sessionId: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Current message")
    conversationHistory: Optional[List[Message]] = Field(
        default=[],
        description="Previous messages in conversation"
    )
    metadata: Optional[Dict] = Field(
        default={},
        description="Additional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "session-123",
                "message": {
                    "sender": "scammer",
                    "text": "Your account is blocked! Click here urgently",
                    "timestamp": 1704067200
                },
                "conversationHistory": [],
                "metadata": {}
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    status: str = Field(..., description="Response status")
    reply: str = Field(..., description="Agent's reply to the message")
    scamDetected: bool = Field(
        default=False,
        description="Whether scam has been detected"
    )
    scamScore: int = Field(
        default=0,
        description="Cumulative scam score"
    )
    messageCount: int = Field(
        default=0,
        description="Total messages in session"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "reply": "I'm not sure I understand. Can you explain more?",
                "scamDetected": True,
                "scamScore": 12,
                "messageCount": 5
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")


class IntelligenceData(BaseModel):
    """Extracted intelligence data"""
    bankAccounts: List[str] = Field(default=[], description="Extracted bank accounts")
    upiIds: List[str] = Field(default=[], description="Extracted UPI IDs")
    phishingLinks: List[str] = Field(default=[], description="Extracted URLs")
    phoneNumbers: List[str] = Field(default=[], description="Extracted phone numbers")
    suspiciousKeywords: List[str] = Field(default=[], description="Detected keywords")
    emailAddresses: List[str] = Field(default=[], description="Extracted email addresses")


class SessionInfo(BaseModel):
    """Complete session information"""
    sessionId: str
    messages: List[Message]
    scamDetected: bool
    scamScore: int
    intel: IntelligenceData
    callbackSent: bool
    createdAt: str
    lastUpdated: str