#!/usr/bin/env python3
"""
Integrated QuMail Core - Backend Integration Version
This version uses the API client for actual backend communication
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# Import the API client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import QuMailAPIClient

@dataclass
class UserProfile:
    """User profile data structure"""
    user_id: str
    email: str
    display_name: str
    sae_id: str
    password_hash: Optional[str] = None
    last_login: Optional[datetime] = None
    auth_token: Optional[str] = None
    provider: str = "qumail"
    created_at: Optional[datetime] = None

class IntegratedQuMailCore:
    """
    Integrated QuMail core that connects to the actual backend
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize integrated QuMail core"""
        self.config = config or {}
        self.current_user: Optional[UserProfile] = None
        
        # Initialize API client
        backend_url = self.config.get('backend_url', 'http://127.0.0.1:8001')
        self.api_client = QuMailAPIClient(backend_url)
        
        # Security settings
        self.current_security_level = 'L2'
        self.security_levels = {
            'L1': 'Quantum OTP',
            'L2': 'Quantum-aided AES', 
            'L3': 'Post-Quantum Crypto',
            'L4': 'Standard TLS Only'
        }
        
        # Local cache for performance
        self.email_cache = []
        self.chat_cache = {}
        
        # Status tracking
        self.quantum_status_cache = None
        self.last_status_update = None
        
        logging.info("Integrated QuMail Core initialized with backend API client")
    
    async def initialize(self):
        """Initialize the integrated core"""
        try:
            logging.info("Starting integrated QuMail Core initialization...")
            
            # Test backend connection
            health_result = await self.api_client.health_check()
            if not health_result['success']:
                raise Exception(f"Backend health check failed: {health_result.get('error')}")
            
            logging.info("Backend connection verified")
            
            # Setup callbacks for real-time events
            self.api_client.register_message_callback(self._on_new_message)
            self.api_client.register_status_callback(self._on_status_update)
            self.api_client.register_call_callback(self._on_call_event)
            
            logging.info("Integrated QuMail Core initialization completed")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize integrated QuMail Core: {e}")
            raise
    
    async def authenticate_user(self, provider: str = "qumail_native") -> bool:
        """Authenticate user with backend"""
        try:
            # For testing, use demo credentials
            # In a real app, this would come from a login dialog
            login_result = await self.api_client.login("demo@qumail.com", "password")
            
            if login_result['success']:
                user_data = login_result['data']['user']
                
                self.current_user = UserProfile(
                    user_id=user_data['sae_id'],
                    email=user_data['email'],
                    display_name=user_data['display_name'],
                    sae_id=user_data['sae_id'],
                    auth_token=login_result['data']['access_token'],
                    provider="qumail_backend",
                    last_login=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                
                # Connect to WebSocket for real-time features
                await self.api_client.connect_chat_websocket()
                
                logging.info(f"User authenticated successfully: {user_data['email']}")
                return True
            else:
                logging.error(f"Authentication failed: {login_result.get('error')}")
                return False
                
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            return False
    
    async def logout_user(self):
        """Logout current user"""
        try:
            if self.current_user:
                logging.info(f"Logging out user: {self.current_user.email}")
                
                # Logout from backend
                await self.api_client.logout()
                
                # Clear local data
                self.current_user = None
                self.email_cache.clear()
                self.chat_cache.clear()
                self.quantum_status_cache = None
                
                logging.info("User logout completed")
            
        except Exception as e:
            logging.error(f"Logout error: {e}")
    
    def set_security_level(self, level: str):
        """Set security level (this will be synced with backend)"""
        if level in self.security_levels:
            self.current_security_level = level
            
            # Update backend asynchronously
            asyncio.create_task(self._sync_security_level(level))
            
            logging.info(f"Security level changed to: {level}")
        else:
            logging.warning(f"Invalid security level: {level}")
    
    async def _sync_security_level(self, level: str):
        """Sync security level with backend"""
        try:
            result = await self.api_client.set_security_level(level)
            if result['success']:
                logging.info(f"Security level synced with backend: {level}")
            else:
                logging.error(f"Failed to sync security level: {result.get('error')}")
        except Exception as e:
            logging.error(f"Security level sync error: {e}")
    
    def get_qkd_status(self) -> Dict[str, Any]:
        """Get QKD status (cached with backend sync)"""
        # Return cached status if recent
        if (self.quantum_status_cache and self.last_status_update and 
            (datetime.utcnow() - self.last_status_update).seconds < 30):
            return self.quantum_status_cache
        
        # Fetch from backend asynchronously
        asyncio.create_task(self._update_quantum_status())
        
        # Return default status while fetching
        return {
            'status': 'active',
            'security_level': self.current_security_level,
            'kme_connected': True,
            'available_levels': list(self.security_levels.keys()),
            'heartbeat_enabled': True,
            'connection_failures': 0,
            'success_rate': 95.0,
            'uptime_seconds': 3600
        }
    
    async def _update_quantum_status(self):
        """Update quantum status from backend"""
        try:
            result = await self.api_client.get_quantum_status()
            if result['success']:
                self.quantum_status_cache = result['data']
                self.last_status_update = datetime.utcnow()
        except Exception as e:
            logging.error(f"Failed to update quantum status: {e}")
    
    def get_pqc_statistics(self) -> Dict[str, Any]:
        """Get PQC statistics"""
        if self.quantum_status_cache:
            return self.quantum_status_cache.get('pqc_stats', {})
        
        # Default stats
        return {
            'files_encrypted': 0,
            'total_size_encrypted': 0,
            'fek_operations': 0,
            'kyber_encapsulations': 0
        }
    
    # ==================== Email Operations ====================
    
    async def send_secure_email(self, to_address: str, subject: str, body: str, 
                              attachments: Optional[List] = None, security_level: str = None,
                              metadata: Optional[Dict] = None) -> bool:
        """Send secure email via backend"""
        try:
            if not self.current_user:
                logging.error("No authenticated user for email sending")
                return False
            
            security_level = security_level or self.current_security_level
            
            result = await self.api_client.send_email(
                to_address=to_address,
                subject=subject,
                body=body,
                security_level=security_level,
                attachments=attachments or []
            )
            
            if result['success']:
                logging.info(f"Email sent to {to_address}")
                
                # Clear email cache to force refresh
                self.email_cache.clear()
                
                return True
            else:
                logging.error(f"Failed to send email: {result.get('error')}")
                return False
                
        except Exception as e:
            logging.error(f"Send email error: {e}")
            return False
    
    async def get_email_list(self, folder: str = "Inbox", limit: int = 50) -> List[Dict]:
        """Get email list from backend"""
        try:
            if not self.current_user:
                logging.error("No authenticated user")
                return []
            
            result = await self.api_client.get_inbox(folder=folder, limit=limit)
            
            if result['success']:
                emails = result['data']['emails']
                
                # Convert to expected format
                formatted_emails = []
                for email in emails:
                    formatted_email = {
                        'email_id': email['email_id'],
                        'sender': email['sender'],
                        'subject': email['subject'],
                        'preview': email['preview'],
                        'received_at': email['received_at'],
                        'security_level': email['security_level'],
                        'folder': email['folder']
                    }
                    formatted_emails.append(formatted_email)
                
                # Update cache
                self.email_cache = formatted_emails
                
                logging.info(f"Retrieved {len(formatted_emails)} emails from {folder}")
                return formatted_emails
            else:
                logging.error(f"Failed to get emails: {result.get('error')}")
                return []
                
        except Exception as e:
            logging.error(f"Get email list error: {e}")
            return []
    
    async def receive_secure_email(self, email_id: str) -> Optional[Dict]:
        """Get email details from backend"""
        try:
            if not self.current_user:
                return None
            
            result = await self.api_client.get_email_details(email_id)
            
            if result['success']:
                email_data = result['data']
                logging.info(f"Retrieved email details for {email_id}")
                return email_data
            else:
                logging.error(f"Failed to get email details: {result.get('error')}")
                return None
                
        except Exception as e:
            logging.error(f"Receive email error: {e}")
            return None
    
    # ==================== Chat Operations ====================
    
    async def send_secure_chat_message(self, contact_id: str, message: str, 
                                     security_level: str = None) -> bool:
        """Send secure chat message via backend"""
        try:
            if not self.current_user:
                logging.error("No authenticated user for chat")
                return False
            
            security_level = security_level or self.current_security_level
            
            success = await self.api_client.send_chat_message(
                contact_id=contact_id,
                message=message,
                security_level=security_level
            )
            
            if success:
                logging.info(f"Chat message sent to {contact_id}")
                return True
            else:
                logging.error("Failed to send chat message")
                return False
                
        except Exception as e:
            logging.error(f"Send chat message error: {e}")
            return False
    
    async def get_chat_history_backend(self, contact_id: str, limit: int = 100) -> List[Dict]:
        """Get chat history from backend"""
        try:
            if not self.current_user:
                return []
            
            result = await self.api_client.get_chat_history(contact_id)
            
            if result['success']:
                messages = result['data']['messages']
                logging.info(f"Retrieved {len(messages)} chat messages with {contact_id}")
                return messages
            else:
                logging.error(f"Failed to get chat history: {result.get('error')}")
                return []
                
        except Exception as e:
            logging.error(f"Get chat history error: {e}")
            return []
    
    # ==================== Call Operations ====================
    
    async def initiate_secure_call(self, contact_id: str, call_type: str = 'audio') -> Dict[str, Any]:
        """Initiate secure call via backend"""
        try:
            if not self.current_user:
                return {'success': False, 'error': 'No authenticated user'}
            
            result = await self.api_client.initiate_call(
                contact_id=contact_id,
                call_type=call_type
            )
            
            if result['success']:
                logging.info(f"Call initiated to {contact_id}")
                return {
                    'success': True,
                    'call_id': result['data']['call_id'],
                    'call_data': result['data']
                }
            else:
                logging.error(f"Failed to initiate call: {result.get('error')}")
                return {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            logging.error(f"Initiate call error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def end_secure_call(self, call_id: str) -> bool:
        """End secure call via backend"""
        try:
            result = await self.api_client.end_call(call_id)
            
            if result['success']:
                logging.info(f"Call {call_id} ended")
                return True
            else:
                logging.error(f"Failed to end call: {result.get('error')}")
                return False
                
        except Exception as e:
            logging.error(f"End call error: {e}")
            return False
    
    # ==================== Real-time Event Callbacks ====================
    
    def _on_new_message(self, message_data: Dict):
        """Handle new chat message from WebSocket"""
        try:
            contact_id = message_data['contact_id']
            if contact_id not in self.chat_cache:
                self.chat_cache[contact_id] = []
            
            self.chat_cache[contact_id].append(message_data)
            logging.info(f"New message received from {message_data['sender_id']}")
            
            # In a real GUI app, this would trigger UI updates
            
        except Exception as e:
            logging.error(f"Handle new message error: {e}")
    
    def _on_status_update(self, status_data: Dict):
        """Handle quantum status update from WebSocket"""
        try:
            self.quantum_status_cache = status_data
            self.last_status_update = datetime.utcnow()
            logging.info("Quantum status updated via WebSocket")
            
            # In a real GUI app, this would trigger UI updates
            
        except Exception as e:
            logging.error(f"Handle status update error: {e}")
    
    def _on_call_event(self, call_data: Dict):
        """Handle call event from WebSocket"""
        try:
            event_type = call_data.get('type', 'unknown')
            logging.info(f"Call event received: {event_type}")
            
            # In a real GUI app, this would trigger call UI updates
            
        except Exception as e:
            logging.error(f"Handle call event error: {e}")
    
    # ==================== Utility Methods ====================
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            logging.info("Starting integrated QuMail Core cleanup...")
            
            # Cleanup API client
            await self.api_client.cleanup()
            
            # Clear local data
            self.current_user = None
            self.email_cache.clear()
            self.chat_cache.clear()
            self.quantum_status_cache = None
            
            logging.info("Integrated QuMail Core cleanup completed")
            
        except Exception as e:
            logging.error(f"Cleanup error: {e}")
    
    def get_application_statistics(self) -> Dict[str, Any]:
        """Get application statistics"""
        return {
            'user_authenticated': self.current_user is not None,
            'current_user_email': self.current_user.email if self.current_user else None,
            'security_level': self.current_security_level,
            'cached_emails': len(self.email_cache),
            'active_chats': len(self.chat_cache),
            'backend_connected': self.api_client.is_authenticated()
        }


# ==================== Test Function ====================

async def test_integrated_core():
    """Test the integrated core functionality"""
    core = IntegratedQuMailCore()
    
    try:
        print("Initializing integrated core...")
        await core.initialize()
        print("✓ Core initialized")
        
        print("\nAuthenticating user...")
        auth_success = await core.authenticate_user()
        print(f"✓ Authentication: {auth_success}")
        
        if auth_success:
            print(f"✓ Logged in as: {core.current_user.email}")
            
            # Test email operations
            print("\nTesting email operations...")
            
            # Send email
            email_sent = await core.send_secure_email(
                "alice@qumail.com",
                "Test from Integrated Core",
                "This email was sent using the integrated backend core.",
                security_level="L2"
            )
            print(f"✓ Email sent: {email_sent}")
            
            # Get emails
            emails = await core.get_email_list("Inbox", 10)
            print(f"✓ Retrieved {len(emails)} emails")
            
            # Test chat operations
            print("\nTesting chat operations...")
            
            # Send chat message
            chat_sent = await core.send_secure_chat_message(
                "alice@qumail.com",
                "Hello from integrated core!",
                "L2"
            )
            print(f"✓ Chat message sent: {chat_sent}")
            
            # Test call operations
            print("\nTesting call operations...")
            
            call_result = await core.initiate_secure_call("alice@qumail.com", "audio")
            print(f"✓ Call initiated: {call_result['success']}")
            
            if call_result['success']:
                call_id = call_result['call_id']
                end_result = await core.end_secure_call(call_id)
                print(f"✓ Call ended: {end_result}")
            
            # Test status
            print("\nTesting quantum status...")
            status = core.get_qkd_status()
            print(f"✓ QKD Status: {status['status']} - Level {status['security_level']}")
            
            # Test logout
            print("\nLogging out...")
            await core.logout_user()
            print("✓ Logged out")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    finally:
        await core.cleanup()
        print("✓ Cleanup completed")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_integrated_core())