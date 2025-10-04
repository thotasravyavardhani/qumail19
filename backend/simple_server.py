#!/usr/bin/env python3
"""
Simple QuMail FastAPI Backend for Frontend Integration Testing
This is a simplified version to focus on frontend-backend integration.
"""

import asyncio
import logging
import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uuid

# =============================================================================
# Pydantic Models for API Requests/Responses
# =============================================================================

class UserLogin(BaseModel):
    email: str
    password: str
    display_name: Optional[str] = None

class SendEmailRequest(BaseModel):
    to_address: str
    subject: str
    body: str
    security_level: str = "L2"
    attachments: Optional[List[Dict]] = None

class SendChatRequest(BaseModel):
    contact_id: str
    message: str
    security_level: str = "L2"

class CallInitiateRequest(BaseModel):
    contact_id: str
    call_type: str = "audio"  # audio or video

class QuantumStatus(BaseModel):
    status: str
    security_level: str
    kme_connected: bool
    available_levels: List[str]
    heartbeat_enabled: bool
    connection_failures: int
    success_rate: float
    uptime_seconds: int
    pqc_stats: Dict

class EmailResponse(BaseModel):
    email_id: str
    sender: str
    subject: str
    preview: str
    received_at: str
    security_level: str
    folder: str

# =============================================================================
# WebSocket Connection Manager
# =============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time chat and status updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_sessions[user_id] = {
            'connected_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat()
        }
        logging.info(f"WebSocket connected for user: {user_id}")
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        logging.info(f"WebSocket disconnected for user: {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
                self.user_sessions[user_id]['last_activity'] = datetime.utcnow().isoformat()
            except Exception as e:
                logging.error(f"Failed to send message to {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast quantum status updates to all connected users"""
        disconnected_users = []
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
                self.user_sessions[user_id]['last_activity'] = datetime.utcnow().isoformat()
            except Exception as e:
                logging.error(f"Failed to broadcast to {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)

# =============================================================================
# FastAPI Application Setup
# =============================================================================

app = FastAPI(
    title="QuMail Simple API",
    description="Simple QuMail Backend for Frontend Integration",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
connection_manager = ConnectionManager()
security = HTTPBearer()

# Simple demo user store
demo_users = {
    "alice@qumail.com": {"password_hash": hashlib.sha256("password123".encode()).hexdigest(), "display_name": "Alice Smith"}, 
    "bob@qumail.com": {"password_hash": hashlib.sha256("password123".encode()).hexdigest(), "display_name": "Bob Johnson"},
    "demo@qumail.com": {"password_hash": hashlib.sha256("password".encode()).hexdigest(), "display_name": "Demo User"},
    "test@qumail.com": {"password_hash": hashlib.sha256("test".encode()).hexdigest(), "display_name": "Test User"}
}

# In-memory storage for emails and messages
emails_store = []
chat_messages_store = {}
call_sessions_store = {}

# Mock quantum status
quantum_status = {
    'status': 'active',
    'security_level': 'L2',
    'kme_connected': True,
    'available_levels': ['L1', 'L2', 'L3', 'L4'],
    'heartbeat_enabled': True,
    'connection_failures': 0,
    'success_rate': 95.5,
    'uptime_seconds': 3600,
    'pqc_stats': {
        'files_encrypted': 12,
        'total_size_encrypted': 50 * 1024 * 1024,
        'fek_operations': 8,
        'kyber_encapsulations': 4
    }
}

# =============================================================================
# Authentication & Dependencies
# =============================================================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Simple token validation for demo purposes"""
    token = credentials.credentials
    if "@" in token and token in demo_users:
        return token
    raise HTTPException(status_code=401, detail="Invalid authentication token")

# =============================================================================
# Authentication Endpoints
# =============================================================================

@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    """User authentication"""
    try:
        email = user_data.email.lower()
        password = user_data.password
        submitted_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        if email not in demo_users or demo_users[email]["password_hash"] != submitted_hash:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        logging.info(f"Login successful for: {email}")
        
        return {
            "access_token": email,  # Simple token for demo
            "token_type": "bearer",
            "user": {
                "email": email,
                "display_name": demo_users[email]["display_name"],
                "sae_id": f"SAE_{uuid.uuid4().hex[:8].upper()}"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal authentication error")

@app.post("/api/auth/logout")
async def logout(current_user: str = Depends(get_current_user)):
    """Logout current user"""
    try:
        return {"message": "Logged out successfully"}
    except Exception as e:
        logging.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

# =============================================================================
# Quantum Status & Control Endpoints  
# =============================================================================

@app.get("/api/quantum/status", response_model=QuantumStatus)
async def get_quantum_status(current_user: str = Depends(get_current_user)):
    """Get real-time quantum/KME status"""
    try:
        return QuantumStatus(**quantum_status)
    except Exception as e:
        logging.error(f"Failed to get quantum status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve quantum status")

@app.post("/api/quantum/security-level")
async def set_security_level(level: str, current_user: str = Depends(get_current_user)):
    """Set quantum security level (L1/L2/L3/L4)"""
    try:
        if level not in ['L1', 'L2', 'L3', 'L4']:
            raise HTTPException(status_code=400, detail="Invalid security level")
        
        quantum_status['security_level'] = level
        
        # Broadcast status update to all connected WebSocket clients
        await connection_manager.broadcast_to_all({
            'type': 'quantum_status_update',
            'data': quantum_status
        })
        
        return {"message": f"Security level set to {level}", "level": level}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to set security level: {e}")
        raise HTTPException(status_code=500, detail="Failed to set security level")

# =============================================================================
# Email Endpoints
# =============================================================================

@app.post("/api/messages/send")
async def send_quantum_email(request: SendEmailRequest, current_user: str = Depends(get_current_user)):
    """Send quantum-encrypted email"""
    try:
        # Create new email
        email_id = str(uuid.uuid4())
        new_email = {
            'email_id': email_id,
            'sender': current_user,
            'to': request.to_address,
            'subject': request.subject,
            'body': request.body,
            'security_level': request.security_level,
            'folder': 'Sent',
            'timestamp': datetime.utcnow().isoformat(),
            'attachments': request.attachments or [],
            'preview': request.body[:100] + "..." if len(request.body) > 100 else request.body
        }
        
        emails_store.append(new_email)
        
        # Also create a received copy for the recipient if it's a demo user
        if request.to_address in demo_users:
            received_email = new_email.copy()
            received_email['email_id'] = str(uuid.uuid4())
            received_email['folder'] = 'Inbox'
            received_email['received_at'] = datetime.utcnow().isoformat()
            emails_store.append(received_email)
        
        logging.info(f"Email sent from {current_user} to {request.to_address}")
        
        return {
            "message": "Quantum email sent successfully",
            "email_id": email_id,
            "security_level": request.security_level,
            "to": request.to_address
        }
        
    except Exception as e:
        logging.error(f"Send email error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

@app.get("/api/messages/inbox")
async def get_inbox(folder: str = "Inbox", limit: int = 50, current_user: str = Depends(get_current_user)):
    """Get inbox messages"""
    try:
        # Filter emails by folder and user
        filtered_emails = [
            email for email in emails_store 
            if email.get('folder') == folder and (
                email.get('sender') == current_user or 
                email.get('to') == current_user
            )
        ]
        
        # Sort by timestamp, most recent first
        filtered_emails.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Limit results
        filtered_emails = filtered_emails[:limit]
        
        return {
            "emails": [
                EmailResponse(
                    email_id=email['email_id'],
                    sender=email['sender'],
                    subject=email['subject'],
                    preview=email.get('preview', email['body'][:100]),
                    received_at=email.get('received_at', email['timestamp']),
                    security_level=email['security_level'],
                    folder=email['folder']
                ) for email in filtered_emails
            ],
            "total": len(filtered_emails)
        }
        
    except Exception as e:
        logging.error(f"Get inbox error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve emails")

@app.get("/api/messages/{email_id}")
async def get_email_details(email_id: str, current_user: str = Depends(get_current_user)):
    """Get decrypted email details"""
    try:
        # Find email
        email = None
        for e in emails_store:
            if e['email_id'] == email_id and (e.get('sender') == current_user or e.get('to') == current_user):
                email = e
                break
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        return {
            "email_id": email_id,
            "sender": email['sender'],
            "to": email.get('to', ''),
            "subject": email['subject'],
            "body": email['body'],
            "security_level": email['security_level'],
            "timestamp": email['timestamp'],
            "decrypted_at": datetime.utcnow().isoformat(),
            "pqc_details": {} if email['security_level'] != 'L3' else {
                'algorithm': 'CRYSTALS-Kyber',
                'key_size': '768',
                'encrypted_size': len(email['body']) * 1.2
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get email details error: {e}")
        raise HTTPException(status_code=500, detail="Failed to decrypt email")

# =============================================================================
# WebSocket Endpoints (Real-Time Chat)
# =============================================================================

@app.websocket("/api/ws/chat/{user_id}")
async def websocket_chat_endpoint(websocket: WebSocket, user_id: str):
    """Real-time chat WebSocket"""
    await connection_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data['type'] == 'chat_message':
                # Process chat message
                chat_request = message_data['data']
                contact_id = chat_request['contact_id']
                message_content = chat_request['message']
                security_level = chat_request.get('security_level', 'L2')
                
                # Store message
                message_id = str(uuid.uuid4())
                chat_message = {
                    'message_id': message_id,
                    'sender_id': user_id,
                    'contact_id': contact_id,
                    'content': message_content,
                    'security_level': security_level,
                    'timestamp': datetime.utcnow().isoformat(),
                    'encrypted': security_level in ['L1', 'L2', 'L3']
                }
                
                # Store in chat messages
                chat_key = f"{min(user_id, contact_id)}_{max(user_id, contact_id)}"
                if chat_key not in chat_messages_store:
                    chat_messages_store[chat_key] = []
                chat_messages_store[chat_key].append(chat_message)
                
                # Send to recipient if connected
                await connection_manager.send_personal_message({
                    'type': 'new_chat_message',
                    'data': chat_message
                }, contact_id)
                
                # Confirm to sender
                await connection_manager.send_personal_message({
                    'type': 'message_sent',
                    'message_id': message_id,
                    'status': 'delivered'
                }, user_id)
                
                logging.info(f"Chat message from {user_id} to {contact_id}: {message_content[:50]}")
                
            elif message_data['type'] == 'request_quantum_status':
                # Send current quantum status
                await connection_manager.send_personal_message({
                    'type': 'quantum_status_update',
                    'data': quantum_status
                }, user_id)
                    
    except WebSocketDisconnect:
        connection_manager.disconnect(user_id)
    except Exception as e:
        logging.error(f"WebSocket error for user {user_id}: {e}")
        connection_manager.disconnect(user_id)

@app.get("/api/chat/history/{contact_id}")
async def get_chat_history(contact_id: str, current_user: str = Depends(get_current_user)):
    """Get chat history between current user and contact"""
    try:
        chat_key = f"{min(current_user, contact_id)}_{max(current_user, contact_id)}"
        messages = chat_messages_store.get(chat_key, [])
        
        return {
            "messages": messages,
            "total": len(messages)
        }
        
    except Exception as e:
        logging.error(f"Get chat history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

# =============================================================================
# Call Endpoints  
# =============================================================================

@app.post("/api/calls/initiate")
async def initiate_call(request: CallInitiateRequest, current_user: str = Depends(get_current_user)):
    """Initiate audio/video call"""
    try:
        call_id = f"call_{uuid.uuid4().hex[:8]}"
        
        call_session = {
            'call_id': call_id,
            'caller_id': current_user,
            'recipient_id': request.contact_id,
            'call_type': request.call_type,
            'status': 'INITIATED',
            'initiated_at': datetime.utcnow().isoformat(),
            'security_level': 'Hybrid-PQC'
        }
        
        call_sessions_store[call_id] = call_session
        
        # Notify recipient if connected
        await connection_manager.send_personal_message({
            'type': 'incoming_call',
            'data': call_session
        }, request.contact_id)
        
        logging.info(f"Call initiated: {call_id} from {current_user} to {request.contact_id}")
        
        return {
            "call_id": call_id,
            "status": "INITIATED",
            "message": "Call initiated successfully",
            "security_level": "Hybrid-PQC"
        }
        
    except Exception as e:
        logging.error(f"Call initiation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate call")

@app.post("/api/calls/{call_id}/end")
async def end_call(call_id: str, current_user: str = Depends(get_current_user)):
    """End call"""
    try:
        if call_id in call_sessions_store:
            call_session = call_sessions_store[call_id]
            call_session['status'] = 'ENDED'
            call_session['ended_at'] = datetime.utcnow().isoformat()
            
            # Notify both parties
            await connection_manager.send_personal_message({
                'type': 'call_ended',
                'call_id': call_id
            }, call_session['caller_id'])
            
            await connection_manager.send_personal_message({
                'type': 'call_ended',
                'call_id': call_id
            }, call_session['recipient_id'])
        
        return {"call_id": call_id, "status": "ended", "message": "Call ended successfully"}
        
    except Exception as e:
        logging.error(f"Call end error: {e}")
        raise HTTPException(status_code=500, detail="Failed to end call")

# =============================================================================
# Health Check & Info
# =============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "backend": True,
            "websocket_connections": len(connection_manager.active_connections)
        }
    }

@app.get("/api/info")
async def get_api_info():
    """API information"""
    return {
        "title": "QuMail Simple API",
        "version": "1.0.0",
        "description": "Simple Backend for Frontend Integration Testing",
        "features": [
            "User Authentication",
            "Email Send/Receive",
            "Real-time Chat via WebSocket",
            "Audio/Video Call Initiation",
            "Quantum Status Simulation"
        ]
    }

# =============================================================================
# Main Application Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Simple QuMail Backend Server")
    
    # Initialize some sample data
    sample_email = {
        'email_id': str(uuid.uuid4()),
        'sender': 'alice@qumail.com',
        'to': 'demo@qumail.com',
        'subject': 'Welcome to QuMail!',
        'body': 'This is a test email to verify the integration between frontend and backend.',
        'security_level': 'L2',
        'folder': 'Inbox',
        'timestamp': datetime.utcnow().isoformat(),
        'attachments': [],
        'preview': 'This is a test email to verify the integration...'
    }
    emails_store.append(sample_email)
    
    # Start the server
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )