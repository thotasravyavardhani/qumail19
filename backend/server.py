#!/usr/bin/env python3
"""
QuMail FastAPI Backend - Web Interface for Quantum Secure Communications
ISRO-Grade Implementation for Smart India Hackathon

Wraps the existing QuMailCore functionality with REST APIs and WebSockets
for real-time quantum cryptography demonstrations.
"""

import asyncio
import logging
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn

# FIXED: Import path resolution for Uvicorn
import sys
from pathlib import Path
# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

# FIXED: Updated imports to resolve modules found in the new path
from core.app_core import QuMailCore, UserProfile
from crypto.kme_simulator import KMESimulator
from utils.config import load_config
from utils.logger import setup_logging

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
    title="QuMail Quantum API",
    description="ISRO-Grade Quantum Secure Communications API",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
qumail_core: Optional[QuMailCore] = None
kme_simulator: Optional[KMESimulator] = None
connection_manager = ConnectionManager()
security = HTTPBearer()

# backend/server.py (Lines 163-167)

# Simple demo user store (using hashes for security)
# backend/server.py (Lines 163-167)
demo_users = {
    "alice@qumail.com": {"password_hash": "e0bfb0a815022aa651c709941397700632ac97e3ac0b216f98587cb2b77af3ad", "display_name": "Alice Smith"}, 
    "bob@qumail.com": {"password_hash": "80e9d0efe2d4f822c2ca5539dc8065b0cac985998e10929324221d8223d97db7", "display_name": "Bob Johnson"},
    "demo@qumail.com": {"password_hash": "d3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791", "display_name": "Demo User"}
}
# =============================================================================
# Authentication & Dependencies
# =============================================================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Simple token validation for demo purposes"""
    # In a real implementation, this would validate JWT tokens
    # For hackathon demo, we use email as token
    token = credentials.credentials
    if "@" in token and token in demo_users:
        return token
    raise HTTPException(status_code=401, detail="Invalid authentication token")

async def get_authenticated_core(current_user: str = Depends(get_current_user)):
    """Get QuMail core instance for authenticated user"""
    if not qumail_core or not qumail_core.current_user:
        raise HTTPException(status_code=401, detail="User not authenticated in core")
    return qumail_core

# =============================================================================
# Startup/Shutdown Events
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize QuMail components on startup"""
    global qumail_core, kme_simulator
    
    # Setup logging
    setup_logging()
    logging.info("Starting QuMail FastAPI Backend")
    
    try:
        # Load configuration
        config = load_config()
        
        # Start KME Simulator for quantum key simulation
        kme_simulator = KMESimulator()
        # Note: KME simulator should be started separately or in background
        
        # Initialize QuMail Core
        qumail_core = QuMailCore(config)
        await qumail_core.initialize()
        
        logging.info("QuMail FastAPI Backend initialized successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize QuMail backend: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global qumail_core, kme_simulator
    
    logging.info("Shutting down QuMail FastAPI Backend")
    
    if qumail_core:
        await qumail_core.cleanup()
    
    if kme_simulator:
        # Stop KME simulator if needed
        pass

# =============================================================================
# Authentication Endpoints
# =============================================================================

@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    """Hybrid authentication - demo mode with real OAuth2 structure"""
    try:
        email = user_data.email.lower()
        password = user_data.password
        # Calculate hash of incoming password for security check
        submitted_hash = hashlib.sha256(password.encode('utf-8')).hexdigest() # CRITICAL: Hash the submitted password
        
        # Demo authentication check - Check against stored hash
        if email not in demo_users or demo_users[email]["password_hash"] != submitted_hash:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create user session in QuMail Core
        if qumail_core:
            user_identity = qumail_core.identity_manager.check_credentials(email, password)
            
            if user_identity:
                # Manually create the UserProfile object for the Core instance
                qumail_core.current_user = UserProfile(
                    user_id=user_identity.user_id,
                    email=user_identity.email,
                    display_name=user_identity.display_name,
                    password_hash=user_identity.password_hash,
                    sae_id=user_identity.sae_id,
                    provider="qumail_demo",
                    created_at=user_identity.created_at,
                    last_login=datetime.utcnow()
                )
                
                # OPTIONAL: Initialize email/chat handlers for the new user session (recommended)
                await qumail_core.email_handler.initialize(qumail_core.current_user)
                await qumail_core.chat_handler.initialize(qumail_core.current_user)
                
                logging.info(f"Web API Login SUCCESS for: {email}")
                
                return {
                    "access_token": email,  # Simple token for demo
                    "token_type": "bearer",
                    "user": {
                        "email": email,
                        "display_name": demo_users[email]["display_name"],
                        "sae_id": qumail_core.current_user.sae_id
                    }
                }
        
        raise HTTPException(status_code=500, detail="Authentication system error")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login error: {e}")
        # The crash is likely coming from here if the core setup failed later
        raise HTTPException(status_code=500, detail="Internal authentication error")

@app.post("/api/auth/logout")
async def logout(current_user: str = Depends(get_current_user)):
    """Logout current user"""
    try:
        if qumail_core and qumail_core.current_user:
            await qumail_core.logout_user()
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logging.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

# =============================================================================
# Quantum Status & Control Endpoints  
# =============================================================================

@app.get("/api/quantum/status", response_model=QuantumStatus)
async def get_quantum_status(core = Depends(get_authenticated_core)):
    """Get real-time quantum/KME status"""
    try:
        status_data = core.get_qkd_status()
        pqc_stats = core.get_pqc_statistics() if hasattr(core, 'get_pqc_statistics') else {}
        
        return QuantumStatus(
            status=status_data['status'],
            security_level=status_data['security_level'],
            kme_connected=status_data['kme_connected'],
            available_levels=status_data['available_levels'],
            heartbeat_enabled=status_data.get('heartbeat_enabled', False),
            connection_failures=status_data.get('connection_failures', 0),
            success_rate=status_data.get('success_rate', 0.0),
            uptime_seconds=status_data.get('uptime_seconds', 0),
            pqc_stats=pqc_stats
        )
        
    except Exception as e:
        logging.error(f"Failed to get quantum status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve quantum status")

@app.post("/api/quantum/security-level")
async def set_security_level(level: str, core = Depends(get_authenticated_core)):
    """Set quantum security level (L1/L2/L3/L4)"""
    try:
        if level not in ['L1', 'L2', 'L3', 'L4']:
            raise HTTPException(status_code=400, detail="Invalid security level")
        
        core.set_security_level(level)
        
        # Broadcast status update to all connected WebSocket clients
        status_data = core.get_qkd_status()
        await connection_manager.broadcast_to_all({
            'type': 'quantum_status_update',
            'data': status_data
        })
        
        return {"message": f"Security level set to {level}", "level": level}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to set security level: {e}")
        raise HTTPException(status_code=500, detail="Failed to set security level")

# =============================================================================
# Email Endpoints (Quantum Email Pillar)
# =============================================================================

@app.post("/api/messages/send")
async def send_quantum_email(request: SendEmailRequest, core = Depends(get_authenticated_core)):
    """Send quantum-encrypted email - Core Pillar 1"""
    try:
        # Process attachments if provided
        processed_attachments = []
        if request.attachments:
            for attachment in request.attachments:
                processed_attachments.append(attachment)
        
        success = await core.send_secure_email(
            to_address=request.to_address,
            subject=request.subject,
            body=request.body,
            attachments=processed_attachments,
            security_level=request.security_level
        )
        
        if success:
            return {
                "message": "Quantum email sent successfully",
                "security_level": request.security_level,
                "to": request.to_address
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send quantum email")
            
    except ValueError as e:
        # Handle policy violations (e.g., OTP size limits)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Send email error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

@app.get("/api/messages/inbox")
async def get_inbox(folder: str = "Inbox", limit: int = 50, core = Depends(get_authenticated_core)):
    """Get inbox messages"""
    try:
        emails = await core.get_email_list(folder, limit)
        
        return {
            "emails": [
                EmailResponse(
                    email_id=email.get('email_id', ''),
                    sender=email.get('sender', ''),
                    subject=email.get('subject', ''),
                    preview=email.get('preview', email.get('body', '')[:100]),
                    received_at=email.get('received_at', ''),
                    security_level=email.get('security_level', 'L4'),
                    folder=email.get('folder', folder)
                ) for email in emails
            ],
            "total": len(emails)
        }
        
    except Exception as e:
        logging.error(f"Get inbox error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve emails")

@app.get("/api/messages/{email_id}")
async def get_email_details(email_id: str, core = Depends(get_authenticated_core)):
    """Get decrypted email details - Core Pillar 1 (Phase 2)"""
    try:
        email_data = await core.receive_secure_email(email_id)
        
        if email_data:
            return {
                "email_id": email_id,
                "sender": email_data.get('sender'),
                "subject": email_data.get('subject'),
                "body": email_data.get('body'),
                "security_level": email_data.get('security_level'),
                "decrypted_at": email_data.get('decrypted_at'),
                "pqc_details": email_data.get('pqc_details')
            }
        else:
            raise HTTPException(status_code=404, detail="Email not found")
            
    except Exception as e:
        logging.error(f"Get email details error: {e}")
        raise HTTPException(status_code=500, detail="Failed to decrypt email")

# =============================================================================
# File Upload & PQC Encryption (Priority Feature)
# =============================================================================

@app.post("/api/files/encrypt")
async def encrypt_large_file(
    file: UploadFile = File(...),
    security_level: str = "L3",
    core = Depends(get_authenticated_core)
):
    """PQC File Encryption Demo - Priority Feature"""
    try:
        if security_level not in ['L2', 'L3']:
            raise HTTPException(status_code=400, detail="File encryption requires L2 or L3 security")
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Create mock attachment data for QuMail processing
        mock_attachment = {
            'name': file.filename,
            'size': file_size,
            'is_mock': True,
            'content': file_content
        }
        
        # Send as encrypted email to demonstrate PQC file handling
        success = await core.send_secure_email(
            to_address=core.current_user.email,  # Self-email for demo
            subject=f"PQC File Encryption: {file.filename}",
            body=f"Large file encrypted with {security_level} security. Size: {file_size / (1024*1024):.2f} MB",
            attachments=[mock_attachment],
            security_level=security_level
        )
        
        if success:
            # Get updated PQC statistics
            pqc_stats = core.get_pqc_statistics() if hasattr(core, 'get_pqc_statistics') else {}
            
            return {
                "message": "File encrypted successfully with PQC",
                "filename": file.filename,
                "size_mb": file_size / (1024*1024),
                "security_level": security_level,
                "pqc_stats": pqc_stats,
                "kyber_kem_used": security_level == "L3" and file_size > 10*1024*1024
            }
        else:
            raise HTTPException(status_code=500, detail="File encryption failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"File encryption error: {e}")
        raise HTTPException(status_code=500, detail=f"File encryption failed: {str(e)}")

# =============================================================================
# WebSocket Endpoints (Real-Time Chat & Status)
# =============================================================================

@app.websocket("/api/ws/chat/{user_id}")
async def websocket_chat_endpoint(websocket: WebSocket, user_id: str):
    """Real-time chat WebSocket - Core Pillar 2"""
    await connection_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data['type'] == 'chat_message':
                # Process quantum-encrypted chat message
                chat_request = SendChatRequest(**message_data['data'])
                
                # Use QuMail core to send encrypted message
                if qumail_core:
                    success = await qumail_core.send_secure_chat_message(
                        contact_id=chat_request.contact_id,
                        message=chat_request.message,
                        security_level=chat_request.security_level
                    )
                    
                    if success:
                        # Send encrypted message to recipient
                        encrypted_payload = {
                            'type': 'encrypted_chat_message',
                            'sender': user_id,
                            'contact_id': chat_request.contact_id,
                            'security_level': chat_request.security_level,
                            'timestamp': datetime.utcnow().isoformat(),
                            'encrypted': True,
                            'message': chat_request.message  # In real implementation, this would be encrypted
                        }
                        
                        # Send to specific recipient
                        await connection_manager.send_personal_message(
                            encrypted_payload, 
                            chat_request.contact_id
                        )
                        
                        # Confirm to sender
                        await connection_manager.send_personal_message({
                            'type': 'message_sent',
                            'message_id': f"msg_{int(datetime.utcnow().timestamp() * 1000)}",
                            'status': 'delivered'
                        }, user_id)
                        
            elif message_data['type'] == 'request_quantum_status':
                # Send current quantum status
                if qumail_core:
                    status_data = qumail_core.get_qkd_status()
                    await connection_manager.send_personal_message({
                        'type': 'quantum_status_update',
                        'data': status_data
                    }, user_id)
                    
    except WebSocketDisconnect:
        connection_manager.disconnect(user_id)
    except Exception as e:
        logging.error(f"WebSocket error for user {user_id}: {e}")
        connection_manager.disconnect(user_id)

# =============================================================================
# Call Endpoints (Quantum SRTP Handshake Demo)
# =============================================================================

@app.post("/api/calls/initiate")
async def initiate_quantum_call(request: CallInitiateRequest, core = Depends(get_authenticated_core)):
    """Initiate quantum SRTP call - Core Pillar 3"""
    try:
        # Simulate quantum SRTP key negotiation
        logging.info(f"Initiating {request.call_type} call to {request.contact_id}")
        
        # This would normally call QuMail's call handling logic
        # For hackathon demo, we simulate the key handshake process
        
        # Phase 1: Key Request
        call_session = {
            'call_id': f"call_{int(datetime.utcnow().timestamp() * 1000)}",
            'caller': core.current_user.user_id,
            'callee': request.contact_id,
            'call_type': request.call_type,
            'status': 'key_requested',
            'initiated_at': datetime.utcnow().isoformat()
        }
        
        # Notify both parties via WebSocket
        caller_message = {
            'type': 'call_status',
            'call_data': call_session,
            'message': 'Requesting quantum keys for SRTP...'
        }
        
        callee_message = {
            'type': 'incoming_call',
            'call_data': call_session,
            'message': f'Incoming {request.call_type} call with quantum security'
        }
        
        await connection_manager.send_personal_message(caller_message, core.current_user.user_id)
        await connection_manager.send_personal_message(callee_message, request.contact_id)
        
        # Simulate successful key handshake after brief delay
        await asyncio.sleep(1)
        
        # Phase 2: Keys Received, SRTP Active
        call_session['status'] = 'srtp_active'
        call_session['quantum_keys_received'] = datetime.utcnow().isoformat()
        
        active_message = {
            'type': 'call_status',
            'call_data': call_session,
            'message': 'Quantum SRTP session established 🔐'
        }
        
        await connection_manager.send_personal_message(active_message, core.current_user.user_id)
        await connection_manager.send_personal_message(active_message, request.contact_id)
        
        return {
            "call_id": call_session['call_id'],
            "status": "initiated",
            "quantum_keys": "requested",
            "message": "Quantum call handshake initiated"
        }
        
    except Exception as e:
        logging.error(f"Call initiation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate quantum call")

@app.post("/api/calls/{call_id}/end")
async def end_quantum_call(call_id: str, current_user: str = Depends(get_current_user)):
    """End quantum call and cleanup"""
    try:
        # Simulate secure key cleanup
        cleanup_message = {
            'type': 'call_ended',
            'call_id': call_id,
            'ended_at': datetime.utcnow().isoformat(),
            'message': 'Call ended - Quantum keys zeroized'
        }
        
        # Broadcast to relevant users (in real app, would track call participants)
        await connection_manager.broadcast_to_all(cleanup_message)
        
        return {
            "call_id": call_id,
            "status": "ended",
            "keys_zeroized": True,
            "message": "Quantum call ended successfully"
        }
        
    except Exception as e:
        logging.error(f"Call end error: {e}")
        raise HTTPException(status_code=500, detail="Failed to end call")

# =============================================================================
# Health Check & Info
# =============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "components": {
                "qumail_core": qumail_core is not None,
                "kme_simulator": kme_simulator is not None,
                "active_websockets": len(connection_manager.active_connections)
            }
        }
        
        if qumail_core:
            quantum_status = qumail_core.get_qkd_status()
            status["quantum"] = {
                "kme_connected": quantum_status.get('kme_connected', False),
                "security_level": quantum_status.get('security_level', 'Unknown')
            }
            
        return status
        
    except Exception as e:
        logging.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/api/info")
async def get_api_info():
    """API information for frontend"""
    return {
        "title": "QuMail Quantum API",
        "version": "1.0.0",
        "description": "ISRO-Grade Quantum Secure Communications",
        "features": [
            "Quantum Email (L1/L2/L3/L4 Security Levels)",
            "Real-time Chat with QKD",
            "PQC File Encryption",
            "Quantum SRTP Call Handshake",
            "Live KME Status Monitoring"
        ],
        "security_levels": {
            "L1": "Quantum OTP (One-Time Pad)",
            "L2": "Quantum-aided AES-GCM", 
            "L3": "Post-Quantum Cryptography + Files",
            "L4": "Standard TLS Only"
        }
    }

# =============================================================================
# Main Application Entry Point
# =============================================================================

if __name__ == "__main__":
    # Start the FastAPI server
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
