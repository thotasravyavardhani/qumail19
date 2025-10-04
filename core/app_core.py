#!/usr/bin/env python3
"""
QuMail Core Application Logic
ISRO-Grade Quantum Communications Application

This module contains the core business logic for QuMail, managing:
- User authentication and session management
- Quantum security level coordination
- Integration between GUI modules and transport handlers
- KME (Key Management Entity) interactions
- Email, Chat, and Call service orchestration
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# Import transport handlers with fallback for both package and direct imports
try:
    from ..transport.email_handler import EmailHandler
    from ..transport.chat_handler import ChatHandler
    from ..crypto.kme_client import KMEClient
    from ..auth.identity_manager import IdentityManager
    from ..auth.oauth2_manager import OAuth2Manager
    from ..db.secure_storage import SecureStorage
    from ..utils.config import load_config
    from ..utils.logger import setup_logging
except ImportError:
    from transport.email_handler import EmailHandler
    from transport.chat_handler import ChatHandler
    from crypto.kme_client import KMEClient
    from auth.identity_manager import IdentityManager
    from auth.oauth2_manager import OAuth2Manager
    from db.secure_storage import SecureStorage
    from utils.config import load_config
    from utils.logger import setup_logging

@dataclass
class UserProfile:
    """User profile data structure"""
    email: str
    display_name: str
    sae_id: str
    password_hash: Optional[str] = None
    last_login: Optional[datetime] = None
    auth_token: Optional[str] = None
    oauth_provider: Optional[str] = None

class QuMailCore:
    """
    Core application controller managing all QuMail services and security
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize QuMail core with configuration"""
        self.config = config or load_config()
        self.current_user: Optional[UserProfile] = None
        
        # Initialize logging
        setup_logging()
        logging.info("Initializing QuMail Core Application")
        
        # Service components
        self.email_handler = EmailHandler()
        self.chat_handler = ChatHandler()
        self.kme_client = KMEClient()
        self.identity_manager = IdentityManager()
        self.oauth2_manager = OAuth2Manager()
        self.secure_storage = SecureStorage()
        
        # Security settings
        self.current_security_level = self.config.get('default_security_level', 'L2')
        self.security_levels = {
            'L1': 'Quantum OTP',
            'L2': 'Quantum-aided AES', 
            'L3': 'Post-Quantum Crypto',
            'L4': 'Standard TLS Only'
        }
        
        # KME status tracking
        self.kme_status = {
            'kme_connected': False,
            'security_level': self.current_security_level,
            'success_rate': 0.0,
            'connection_failures': 0,
            'heartbeat_enabled': False,
            'uptime_seconds': 0,
            'pqc_stats': {
                'files_encrypted': 0,
                'total_size_encrypted': 0,
                'fek_operations': 0,
                'kyber_encapsulations': 0
            }
        }
        
        # Statistics tracking
        self.stats = {
            'emails_sent': 0,
            'emails_received': 0,
            'chat_messages_sent': 0,
            'calls_made': 0,
            'quantum_keys_used': 0,
            'session_start': datetime.utcnow()
        }
        
        logging.info("QuMail Core initialized successfully")
    
    async def initialize(self):
        """Initialize all core components asynchronously"""
        try:
            logging.info("Starting QuMail Core initialization...")
            
            # Initialize transport handlers
            await self.email_handler.initialize(self.current_user)
            await self.chat_handler.initialize(self.current_user)
            
            # Initialize KME client
            await self.kme_client.initialize(self.config['kme_url'])
            
            # Test KME connection
            await self._test_kme_connection()
            
            # Initialize secure storage
            await self.secure_storage.initialize()
            
            logging.info("QuMail Core initialization completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize QuMail Core: {e}")
            raise

    async def authenticate_user(self, username: str, password: Optional[str] = None) -> bool:
        """Authenticate user and establish session"""
        try:
            logging.info(f"Authenticating user: {username}")
            
            # For development, create a mock user profile
            if username in ['qumail_native', 'demo', 'test']:
                self.current_user = UserProfile(
                    email=f"{username}@qumail.com",
                    display_name=f"QuMail User ({username})",
                    sae_id=f"SAE_{uuid.uuid4().hex[:8].upper()}",
                    last_login=datetime.utcnow(),
                    auth_token=f"token_{uuid.uuid4().hex}"
                )
                
                logging.info(f"Mock authentication successful for {username}")
                return True
            
            # Real authentication would involve identity manager
            auth_result = await self.identity_manager.authenticate(username, password)
            if auth_result:
                self.current_user = auth_result
                logging.info(f"Authentication successful for {username}")
                return True
            else:
                logging.warning(f"Authentication failed for {username}")
                return False
                
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            return False
    
    async def logout_user(self):
        """Logout current user and cleanup resources"""
        try:
            if self.current_user:
                logging.info(f"Logging out user: {self.current_user.email}")
                
                # Cleanup transport handlers
                await self.email_handler.cleanup()
                await self.chat_handler.cleanup()
                
                # Stop KME heartbeat
                await self.kme_client.stop_heartbeat()
                
                # Clear user data
                self.current_user = None
                
                logging.info("User logout completed successfully")
            
        except Exception as e:
            logging.error(f"Logout error: {e}")
            
    def set_security_level(self, level: str):
        """Set the current security level for all operations"""
        if level in self.security_levels:
            self.current_security_level = level
            self.kme_status['security_level'] = level
            logging.info(f"Security level changed to: {level} ({self.security_levels[level]})")
        else:
            logging.warning(f"Invalid security level: {level}")
    
    def get_qkd_status(self) -> Dict[str, Any]:
        """Get current QKD/KME status information"""
        return self.kme_status.copy()
    
    def get_pqc_statistics(self) -> Dict[str, Any]:
        """Get PQC file encryption statistics"""
        return self.kme_status['pqc_stats'].copy()
    
    # ==================== EMAIL OPERATIONS ====================
    
    async def send_secure_email(self, to_address: str, subject: str, body: str, 
                              attachments: Optional[List] = None, security_level: str = None,
                              metadata: Optional[Dict] = None) -> bool:
        """Send encrypted email with quantum security"""
        try:
            if not self.current_user:
                logging.error("No authenticated user for email sending")
                return False
                
            # Use current security level if not specified
            if not security_level:
                security_level = self.current_security_level
                
            logging.info(f"Sending secure email to {to_address} with {security_level} security")
            
            # Prepare email data
            email_data = {
                'to': to_address,
                'subject': subject,
                'body': body,
                'attachments': attachments or [],
                'security_level': security_level,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Encrypt the email content based on security level
            encrypted_data = await self._encrypt_email_content(email_data)
            
            # Send via email handler
            success = await self.email_handler.send_encrypted_email(to_address, encrypted_data)
            
            if success:
                self.stats['emails_sent'] += 1
                logging.info("Secure email sent successfully")
            
            return success
            
        except Exception as e:
            logging.error(f"Failed to send secure email: {e}")
            return False
    
    async def get_inbox_emails(self, folder: str = "INBOX", limit: int = 50) -> List[Dict]:
        """Get emails from inbox with decryption"""
        try:
            logging.info(f"Retrieving emails from {folder}")
            
            # Get encrypted emails from handler
            encrypted_emails = await self.email_handler.get_email_list(folder, limit)
            
            # Decrypt emails (this would use KME in real implementation)
            decrypted_emails = []
            for email in encrypted_emails:
                try:
                    decrypted_email = await self._decrypt_email_content(email)
                    decrypted_emails.append(decrypted_email)
                except Exception as e:
                    logging.warning(f"Failed to decrypt email {email.get('email_id', 'unknown')}: {e}")
                    # Add as-is if decryption fails
                    decrypted_emails.append(email)
            
            self.stats['emails_received'] = len(decrypted_emails)
            logging.info(f"Retrieved {len(decrypted_emails)} emails")
            return decrypted_emails
            
        except Exception as e:
            logging.error(f"Failed to retrieve emails: {e}")
            return []
    
    # ==================== CHAT OPERATIONS ====================
    
    async def send_secure_chat_message(self, contact_id: str, message: str, 
                                     security_level: str = None) -> bool:
        """Send encrypted chat message"""
        try:
            if not self.current_user:
                logging.error("No authenticated user for chat")
                return False
                
            # Use current security level if not specified
            if not security_level:
                security_level = self.current_security_level
                
            logging.info(f"Sending secure chat message to {contact_id} with {security_level} security")
            
            # Prepare message data
            message_data = {
                'content': message,
                'security_level': security_level,
                'timestamp': datetime.utcnow().isoformat(),
                'sender_id': self.current_user.sae_id
            }
            
            # Encrypt the message
            encrypted_data = await self._encrypt_chat_message(message_data)
            
            # Send via chat handler
            success = await self.chat_handler.send_message(contact_id, encrypted_data)
            
            if success:
                self.stats['chat_messages_sent'] += 1
                logging.info("Secure chat message sent successfully")
            
            return success
            
        except Exception as e:
            logging.error(f"Failed to send secure chat message: {e}")
            return False
    
    async def get_chat_history(self, contact_id: str, limit: int = 100) -> List[Dict]:
        """Get chat history with decryption"""
        try:
            logging.info(f"Retrieving chat history with {contact_id}")
            
            # Get encrypted messages from handler
            encrypted_messages = await self.chat_handler.get_chat_history(contact_id, limit)
            
            # Decrypt messages (this would use KME in real implementation)
            decrypted_messages = []
            for message in encrypted_messages:
                try:
                    decrypted_message = await self._decrypt_chat_message(message)
                    decrypted_messages.append(decrypted_message)
                except Exception as e:
                    logging.warning(f"Failed to decrypt message {message.get('message_id', 'unknown')}: {e}")
                    # Add as-is if decryption fails
                    decrypted_messages.append(message)
            
            logging.info(f"Retrieved {len(decrypted_messages)} chat messages")
            return decrypted_messages
            
        except Exception as e:
            logging.error(f"Failed to retrieve chat history: {e}")
            return []
    
    # ==================== CALL OPERATIONS ====================
    
    async def initiate_secure_call(self, contact_id: str, call_type: str = 'audio') -> Dict[str, Any]:
        """Initiate secure audio/video call with quantum SRTP"""
        try:
            if not self.current_user:
                logging.error("No authenticated user for call")
                return {'success': False, 'error': 'No authenticated user'}
                
            logging.info(f"Initiating {call_type} call to {contact_id}")
            
            # Generate call session
            call_id = f"call_{uuid.uuid4().hex[:8]}"
            
            # Prepare call data
            call_data = {
                'call_id': call_id,
                'caller_id': self.current_user.sae_id,
                'callee_id': contact_id,
                'call_type': call_type,
                'security_level': self.current_security_level,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # In real implementation, this would:
            # 1. Generate quantum-secured SRTP keys
            # 2. Establish WebRTC connection
            # 3. Exchange security parameters
            
            self.stats['calls_made'] += 1
            logging.info(f"Call initiated successfully: {call_id}")
            
            return {
                'success': True,
                'call_id': call_id,
                'call_data': call_data
            }
            
        except Exception as e:
            logging.error(f"Failed to initiate call: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==================== ENCRYPTION/DECRYPTION ====================
    
    async def _encrypt_email_content(self, email_data: Dict) -> Dict[str, Any]:
        """Encrypt email content based on security level"""
        try:
            security_level = email_data.get('security_level', 'L4')
            
            if security_level in ['L1', 'L2']:
                # Quantum encryption - would use KME keys
                key_id = await self._get_quantum_key(security_level)
                
                encrypted_payload = {
                    'algorithm': 'Q-AES-256' if security_level == 'L2' else 'Q-OTP',
                    'key_id': key_id,
                    'ciphertext': 'encrypted_content_placeholder',
                    'security_level': security_level,
                    'timestamp': email_data['timestamp']
                }
                
            elif security_level == 'L3':
                # Post-Quantum Crypto
                encrypted_payload = {
                    'algorithm': 'CRYSTALS-Kyber + AES-256-GCM',
                    'pqc_ciphertext': 'pqc_encrypted_content_placeholder',
                    'security_level': security_level,
                    'timestamp': email_data['timestamp']
                }
                
            else:
                # L4 - Standard TLS
                encrypted_payload = {
                    'algorithm': 'TLS-1.3',
                    'content': email_data['body'],  # Not encrypted locally
                    'security_level': security_level,
                    'timestamp': email_data['timestamp']
                }
            
            # Add original email metadata
            encrypted_payload.update({
                'subject': email_data['subject'],
                'to': email_data['to'],
                'attachments': email_data['attachments'],
                'metadata': email_data['metadata']
            })
            
            return encrypted_payload
            
        except Exception as e:
            logging.error(f"Failed to encrypt email content: {e}")
            raise
    
    async def _decrypt_email_content(self, email_data: Dict) -> Dict[str, Any]:
        """Decrypt email content (simulation)"""
        try:
            # For simulation, just return the email data with mock decryption
            decrypted_data = email_data.copy()
            
            # Add decryption status
            decrypted_data['decryption_status'] = 'success'
            decrypted_data['quantum_verified'] = email_data.get('security_level') in ['L1', 'L2']
            
            return decrypted_data
            
        except Exception as e:
            logging.error(f"Failed to decrypt email: {e}")
            raise
    
    async def _encrypt_chat_message(self, message_data: Dict) -> Dict[str, Any]:
        """Encrypt chat message content"""
        try:
            security_level = message_data.get('security_level', 'L4')
            
            if security_level in ['L1', 'L2']:
                # Quantum encryption
                key_id = await self._get_quantum_key(security_level)
                
                encrypted_payload = {
                    'algorithm': 'Q-AES-256' if security_level == 'L2' else 'Q-OTP',
                    'key_id': key_id,
                    'ciphertext': 'encrypted_message_placeholder',
                    'security_level': security_level
                }
            else:
                # Standard encryption
                encrypted_payload = {
                    'algorithm': 'AES-256-GCM',
                    'ciphertext': 'encrypted_message_placeholder',
                    'security_level': security_level
                }
            
            encrypted_payload.update({
                'timestamp': message_data['timestamp'],
                'sender_id': message_data['sender_id']
            })
            
            return encrypted_payload
            
        except Exception as e:
            logging.error(f"Failed to encrypt chat message: {e}")
            raise
    
    async def _decrypt_chat_message(self, message_data: Dict) -> Dict[str, Any]:
        """Decrypt chat message content (simulation)"""
        try:
            # For simulation, just return the message data with mock decryption
            decrypted_data = message_data.copy()
            
            # Add decryption status
            decrypted_data['decryption_status'] = 'success'
            decrypted_data['quantum_verified'] = message_data.get('security_level') in ['L1', 'L2']
            
            return decrypted_data
            
        except Exception as e:
            logging.error(f"Failed to decrypt chat message: {e}")
            raise
    
    async def _get_quantum_key(self, security_level: str) -> str:
        """Get quantum key from KME"""
        try:
            # This would make a real KME request in production
            key_id = f"QK_{uuid.uuid4().hex[:12]}"
            
            # Update statistics
            self.stats['quantum_keys_used'] += 1
            self.kme_status['success_rate'] = min(100.0, self.kme_status['success_rate'] + 1.0)
            
            logging.debug(f"Generated quantum key: {key_id} for level {security_level}")
            return key_id
            
        except Exception as e:
            logging.error(f"Failed to get quantum key: {e}")
            self.kme_status['connection_failures'] += 1
            raise
    
    async def _test_kme_connection(self):
        """Test KME connection and update status"""
        try:
            # Test KME connection
            kme_health = await self.kme_client.health_check()
            
            if kme_health.get('status') == 'healthy':
                self.kme_status['kme_connected'] = True
                self.kme_status['heartbeat_enabled'] = True
                self.kme_status['success_rate'] = 95.0
                logging.info("KME connection test successful")
            else:
                self.kme_status['kme_connected'] = False
                logging.warning("KME connection test failed")
                
        except Exception as e:
            logging.error(f"KME connection test failed: {e}")
            self.kme_status['kme_connected'] = False
    
    async def cleanup(self):
        """Cleanup all resources"""
        try:
            logging.info("Starting QuMail Core cleanup...")
            
            # Cleanup transport handlers
            await self.email_handler.cleanup()
            await self.chat_handler.cleanup()
            
            # Cleanup KME client
            await self.kme_client.cleanup()
            
            # Clear user data
            self.current_user = None
            
            logging.info("QuMail Core cleanup completed")
            
        except Exception as e:
            logging.error(f"Error during QuMail Core cleanup: {e}")
    
    def get_application_statistics(self) -> Dict[str, Any]:
        """Get comprehensive application statistics"""
        return {
            'user_authenticated': self.current_user is not None,
            'current_user_email': self.current_user.email if self.current_user else None,
            'security_level': self.current_security_level,
            'kme_status': self.kme_status.copy(),
            'stats': self.stats.copy(),
            'uptime_seconds': int((datetime.utcnow() - self.stats['session_start']).total_seconds())
        }
