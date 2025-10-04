#!/usr/bin/env python3
"""
QuMail API Client for Frontend-Backend Integration
This module handles all communication between the PyQt6 frontend and FastAPI backend.
"""

import asyncio
import aiohttp
import json
import logging
import websockets
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

class QuMailAPIClient:
    """
    Main API client for QuMail frontend-backend communication
    Handles REST API calls and WebSocket connections
    """
    
    def __init__(self, backend_url: str = "http://127.0.0.1:8001"):
        self.backend_url = backend_url
        self.auth_token = None
        self.user_data = None
        self.websocket = None
        self.websocket_url = backend_url.replace('http', 'ws')
        
        # Callbacks for real-time events
        self.message_callbacks = []
        self.status_callbacks = []
        self.call_callbacks = []
        
        logging.info(f"QuMail API Client initialized for {backend_url}")
    
    # ==================== Authentication Methods ====================
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with backend"""
        try:
            async with aiohttp.ClientSession() as session:
                login_data = {
                    "email": email,
                    "password": password
                }
                
                async with session.post(
                    f"{self.backend_url}/api/auth/login",
                    json=login_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.auth_token = result['access_token']
                        self.user_data = result['user']
                        
                        logging.info(f"Login successful for {email}")
                        return {'success': True, 'data': result}
                    else:
                        error_text = await response.text()
                        logging.error(f"Login failed: {error_text}")
                        return {'success': False, 'error': error_text}
                        
        except Exception as e:
            logging.error(f"Login error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def logout(self) -> Dict[str, Any]:
        """Logout current user"""
        try:
            if not self.auth_token:
                return {'success': True, 'message': 'Not logged in'}
            
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                
                async with session.post(
                    f"{self.backend_url}/api/auth/logout",
                    headers=headers
                ) as response:
                    result = await response.json()
                    
                    # Clear local auth data
                    self.auth_token = None
                    self.user_data = None
                    
                    # Close WebSocket if connected
                    if self.websocket:
                        await self.websocket.close()
                        self.websocket = None
                    
                    logging.info("Logout successful")
                    return {'success': True, 'data': result}
                    
        except Exception as e:
            logging.error(f"Logout error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests"""
        if not self.auth_token:
            raise Exception("Not authenticated")
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    # ==================== Email Methods ====================
    
    async def send_email(self, to_address: str, subject: str, body: str, 
                        security_level: str = "L2", attachments: List = None) -> Dict[str, Any]:
        """Send email via backend API"""
        try:
            if not self.auth_token:
                return {'success': False, 'error': 'Not authenticated'}
            
            async with aiohttp.ClientSession() as session:
                email_data = {
                    "to_address": to_address,
                    "subject": subject,
                    "body": body,
                    "security_level": security_level,
                    "attachments": attachments or []
                }
                
                async with session.post(
                    f"{self.backend_url}/api/messages/send",
                    json=email_data,
                    headers=self.get_auth_headers()
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logging.info(f"Email sent to {to_address}")
                        return {'success': True, 'data': result}
                    else:
                        error_text = await response.text()
                        logging.error(f"Send email failed: {error_text}")
                        return {'success': False, 'error': error_text}
                        
        except Exception as e:
            logging.error(f"Send email error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_inbox(self, folder: str = "Inbox", limit: int = 50) -> Dict[str, Any]:
        """Get inbox emails from backend"""
        try:
            if not self.auth_token:
                return {'success': False, 'error': 'Not authenticated'}
            
            async with aiohttp.ClientSession() as session:
                params = {"folder": folder, "limit": limit}
                
                async with session.get(
                    f"{self.backend_url}/api/messages/inbox",
                    params=params,
                    headers=self.get_auth_headers()
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logging.info(f"Retrieved {len(result.get('emails', []))} emails from {folder}")
                        return {'success': True, 'data': result}
                    else:
                        error_text = await response.text()
                        logging.error(f"Get inbox failed: {error_text}")
                        return {'success': False, 'error': error_text}
                        
        except Exception as e:
            logging.error(f"Get inbox error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_email_details(self, email_id: str) -> Dict[str, Any]:
        """Get detailed email content from backend"""
        try:
            if not self.auth_token:
                return {'success': False, 'error': 'Not authenticated'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.backend_url}/api/messages/{email_id}",
                    headers=self.get_auth_headers()
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logging.info(f"Retrieved email details for {email_id}")
                        return {'success': True, 'data': result}
                    else:
                        error_text = await response.text()
                        logging.error(f"Get email details failed: {error_text}")
                        return {'success': False, 'error': error_text}
                        
        except Exception as e:
            logging.error(f"Get email details error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==================== Chat Methods ====================
    
    async def connect_chat_websocket(self):
        """Connect to chat WebSocket for real-time messaging"""
        try:
            if not self.auth_token:
                logging.error("Cannot connect to WebSocket without authentication")
                return False
            
            user_id = self.auth_token  # Using email as user ID for simplicity
            ws_url = f"{self.websocket_url}/api/ws/chat/{user_id}"
            
            self.websocket = await websockets.connect(ws_url)
            logging.info(f"WebSocket connected for user {user_id}")
            
            # Start listening for messages
            asyncio.create_task(self._websocket_listener())
            
            return True
            
        except Exception as e:
            logging.error(f"WebSocket connection error: {e}")
            return False
    
    async def _websocket_listener(self):
        """Listen for incoming WebSocket messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                message_type = data.get('type')
                
                if message_type == 'new_chat_message':
                    # New chat message received
                    for callback in self.message_callbacks:
                        callback(data['data'])
                        
                elif message_type == 'quantum_status_update':
                    # Quantum status update
                    for callback in self.status_callbacks:
                        callback(data['data'])
                        
                elif message_type == 'incoming_call':
                    # Incoming call
                    for callback in self.call_callbacks:
                        callback(data['data'])
                        
                elif message_type == 'call_ended':
                    # Call ended
                    for callback in self.call_callbacks:
                        callback({'type': 'call_ended', 'call_id': data.get('call_id')})
                        
                logging.debug(f"WebSocket message received: {message_type}")
                
        except websockets.exceptions.ConnectionClosed:
            logging.info("WebSocket connection closed")
        except Exception as e:
            logging.error(f"WebSocket listener error: {e}")
    
    async def send_chat_message(self, contact_id: str, message: str, security_level: str = "L2") -> bool:
        """Send chat message via WebSocket"""
        try:
            if not self.websocket:
                logging.error("WebSocket not connected")
                return False
            
            message_data = {
                'type': 'chat_message',
                'data': {
                    'contact_id': contact_id,
                    'message': message,
                    'security_level': security_level
                }
            }
            
            await self.websocket.send(json.dumps(message_data))
            logging.info(f"Chat message sent to {contact_id}")
            return True
            
        except Exception as e:
            logging.error(f"Send chat message error: {e}")
            return False
    
    async def get_chat_history(self, contact_id: str) -> Dict[str, Any]:
        """Get chat history with contact"""
        try:
            if not self.auth_token:
                return {'success': False, 'error': 'Not authenticated'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.backend_url}/api/chat/history/{contact_id}",
                    headers=self.get_auth_headers()
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logging.info(f"Retrieved chat history with {contact_id}")
                        return {'success': True, 'data': result}
                    else:
                        error_text = await response.text()
                        logging.error(f"Get chat history failed: {error_text}")
                        return {'success': False, 'error': error_text}
                        
        except Exception as e:
            logging.error(f"Get chat history error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==================== Call Methods ====================
    
    async def initiate_call(self, contact_id: str, call_type: str = "audio") -> Dict[str, Any]:
        """Initiate audio/video call"""
        try:
            if not self.auth_token:
                return {'success': False, 'error': 'Not authenticated'}
            
            async with aiohttp.ClientSession() as session:
                call_data = {
                    "contact_id": contact_id,
                    "call_type": call_type
                }
                
                async with session.post(
                    f"{self.backend_url}/api/calls/initiate",
                    json=call_data,
                    headers=self.get_auth_headers()
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logging.info(f"Call initiated to {contact_id}")
                        return {'success': True, 'data': result}
                    else:
                        error_text = await response.text()
                        logging.error(f"Initiate call failed: {error_text}")
                        return {'success': False, 'error': error_text}
                        
        except Exception as e:
            logging.error(f"Initiate call error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """End ongoing call"""
        try:
            if not self.auth_token:
                return {'success': False, 'error': 'Not authenticated'}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/api/calls/{call_id}/end",
                    headers=self.get_auth_headers()
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logging.info(f"Call {call_id} ended")
                        return {'success': True, 'data': result}
                    else:
                        error_text = await response.text()
                        logging.error(f"End call failed: {error_text}")
                        return {'success': False, 'error': error_text}
                        
        except Exception as e:
            logging.error(f"End call error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==================== Quantum Status Methods ====================
    
    async def get_quantum_status(self) -> Dict[str, Any]:
        """Get current quantum status from backend"""
        try:
            if not self.auth_token:
                return {'success': False, 'error': 'Not authenticated'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.backend_url}/api/quantum/status",
                    headers=self.get_auth_headers()
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logging.debug("Retrieved quantum status")
                        return {'success': True, 'data': result}
                    else:
                        error_text = await response.text()
                        logging.error(f"Get quantum status failed: {error_text}")
                        return {'success': False, 'error': error_text}
                        
        except Exception as e:
            logging.error(f"Get quantum status error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def set_security_level(self, level: str) -> Dict[str, Any]:
        """Set quantum security level"""
        try:
            if not self.auth_token:
                return {'success': False, 'error': 'Not authenticated'}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/api/quantum/security-level",
                    params={'level': level},
                    headers=self.get_auth_headers()
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logging.info(f"Security level set to {level}")
                        return {'success': True, 'data': result}
                    else:
                        error_text = await response.text()
                        logging.error(f"Set security level failed: {error_text}")
                        return {'success': False, 'error': error_text}
                        
        except Exception as e:
            logging.error(f"Set security level error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==================== Callback Registration ====================
    
    def register_message_callback(self, callback: Callable):
        """Register callback for incoming chat messages"""
        self.message_callbacks.append(callback)
    
    def register_status_callback(self, callback: Callable):
        """Register callback for quantum status updates"""
        self.status_callbacks.append(callback)
    
    def register_call_callback(self, callback: Callable):
        """Register callback for call events"""
        self.call_callbacks.append(callback)
    
    # ==================== Utility Methods ====================
    
    async def health_check(self) -> Dict[str, Any]:
        """Check backend health"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/health") as response:
                    if response.status == 200:
                        result = await response.json()
                        return {'success': True, 'data': result}
                    else:
                        return {'success': False, 'error': f"Health check failed: {response.status}"}
                        
        except Exception as e:
            logging.error(f"Health check error: {e}")
            return {'success': False, 'error': str(e)}
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.auth_token is not None
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current user data"""
        return self.user_data
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        self.auth_token = None
        self.user_data = None
        logging.info("API Client cleanup completed")


# ==================== Standalone Test Functions ====================

async def test_api_client():
    """Test the API client functionality"""
    client = QuMailAPIClient()
    
    # Test health check
    print("Testing health check...")
    health = await client.health_check()
    print(f"Health check: {health}")
    
    # Test login
    print("\nTesting login...")
    login_result = await client.login("demo@qumail.com", "password")
    print(f"Login result: {login_result}")
    
    if login_result['success']:
        # Test get inbox
        print("\nTesting get inbox...")
        inbox_result = await client.get_inbox()
        print(f"Inbox result: {inbox_result}")
        
        # Test quantum status
        print("\nTesting quantum status...")
        status_result = await client.get_quantum_status()
        print(f"Quantum status: {status_result}")
        
        # Test send email
        print("\nTesting send email...")
        email_result = await client.send_email(
            "alice@qumail.com", 
            "Test Email", 
            "This is a test email from the API client",
            "L2"
        )
        print(f"Send email result: {email_result}")
        
        # Test WebSocket connection
        print("\nTesting WebSocket connection...")
        ws_connected = await client.connect_chat_websocket()
        print(f"WebSocket connected: {ws_connected}")
        
        if ws_connected:
            # Wait a bit for WebSocket to establish
            await asyncio.sleep(1)
            
            # Test send chat message
            print("\nTesting send chat message...")
            chat_sent = await client.send_chat_message("alice@qumail.com", "Hello from API client!", "L2")
            print(f"Chat message sent: {chat_sent}")
        
        # Test logout
        print("\nTesting logout...")
        logout_result = await client.logout()
        print(f"Logout result: {logout_result}")
    
    await client.cleanup()

if __name__ == "__main__":
    # Run tests
    asyncio.run(test_api_client())