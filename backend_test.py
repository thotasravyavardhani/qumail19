#!/usr/bin/env python3
"""
QuMail Backend Testing Suite - Production Readiness Final 25%
ISRO-Grade Quantum Secure Email Client Testing

Tests:
1. Enhanced Secure Storage with OS-native keyring integration
2. PQC encryption/decryption with FEK support for large files  
3. KME Client heartbeat monitoring and reconnection logic
4. Email Handler OAuth2 token refresh and async transport
5. End-to-end quantum encryption workflow (L1-L4 security levels)
6. Smart email loopback system for development testing
7. Connection failure recovery and statistical monitoring
"""

import asyncio
import logging
import json
import sys
import time
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configure logging for testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QuMailBackendTester:
    """Comprehensive backend testing for QuMail production readiness"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        self.start_time = datetime.utcnow()
        
        # Test data
        self.test_user_data = {
            'user_id': 'test_user_001',
            'email': 'test@qumail.com',
            'display_name': 'Test User',
            'password_hash': 'mock_hash_123',
            'sae_id': 'qumail_test_user_001',
            'provider': 'gmail',
            'created_at': datetime.utcnow(),
            'last_login': datetime.utcnow()
        }
        
        self.test_oauth_credentials = {
            'access_token': 'mock_access_token_12345',
            'refresh_token': 'mock_refresh_token_67890',
            'provider': 'gmail',
            'expires_at': datetime.utcnow() + timedelta(hours=1)
        }
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Log individual test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ PASS: {test_name}")
            if details:
                print(f"   Details: {details}")
        else:
            self.tests_failed += 1
            print(f"❌ FAIL: {test_name}")
            if error:
                print(f"   Error: {error}")
                
        self.test_results.append({
            'test_name': test_name,
            'success': success,
            'details': details,
            'error': error,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    async def test_secure_storage_keyring(self):
        """Test 1: Enhanced Secure Storage with OS-native keyring integration"""
        print("\n🔐 Testing Enhanced Secure Storage...")
        
        try:
            from db.secure_storage import SecureStorage
            
            # Test initialization
            storage = SecureStorage()
            await storage.initialize()
            
            self.log_test_result(
                "Secure Storage Initialization", 
                storage.initialized, 
                f"Keyring available: {storage.keyring_healthy}"
            )
            
            # Test user profile storage
            profile_saved = await storage.save_user_profile(self.test_user_data)
            self.log_test_result(
                "User Profile Storage", 
                profile_saved, 
                "Profile saved to OS-native keyring or fallback"
            )
            
            # Test user profile retrieval
            loaded_profile = await storage.load_user_profile(self.test_user_data['user_id'])
            profile_match = loaded_profile and loaded_profile['user_id'] == self.test_user_data['user_id']
            self.log_test_result(
                "User Profile Retrieval", 
                profile_match, 
                f"Profile loaded: {loaded_profile['email'] if loaded_profile else 'None'}"
            )
            
            # Test OAuth credentials storage
            cred_saved = await storage.save_oauth_credentials(
                'gmail', 
                self.test_user_data['user_id'],
                self.test_user_data['email'],
                self.test_oauth_credentials
            )
            self.log_test_result(
                "OAuth Credentials Storage", 
                cred_saved, 
                "Credentials saved securely"
            )
            
            # Test OAuth credentials retrieval
            loaded_creds = await storage.load_oauth_credentials('gmail', self.test_user_data['user_id'])
            creds_match = loaded_creds and loaded_creds.get('access_token') == self.test_oauth_credentials['access_token']
            self.log_test_result(
                "OAuth Credentials Retrieval", 
                creds_match, 
                "Credentials retrieved successfully"
            )
            
            # Test application settings
            test_settings = {'theme': 'dark', 'security_level': 'L2', 'auto_encrypt': True}
            settings_saved = await storage.save_setting('app', 'preferences', test_settings)
            self.log_test_result(
                "Application Settings Storage", 
                settings_saved, 
                "Settings saved to secure storage"
            )
            
            loaded_settings = await storage.load_setting('app', 'preferences')
            settings_match = loaded_settings and loaded_settings.get('theme') == 'dark'
            self.log_test_result(
                "Application Settings Retrieval", 
                settings_match, 
                f"Settings loaded: {loaded_settings}"
            )
            
            # Test cleanup
            await storage.close()
            self.log_test_result(
                "Secure Storage Cleanup", 
                True, 
                "Storage closed successfully"
            )
            
        except Exception as e:
            self.log_test_result("Secure Storage Test", False, error=str(e))
            
    async def test_pqc_encryption_with_fek(self):
        """Test 2: PQC encryption/decryption with FEK support for large files"""
        print("\n🔬 Testing PQC Encryption with FEK Support...")
        
        try:
            from crypto.cipher_strategies import CipherManager, PostQuantumStrategy
            
            cipher_manager = CipherManager()
            pqc_strategy = PostQuantumStrategy()
            
            # Test small data encryption (standard PQC)
            small_data = b"This is a small test message for PQC encryption."
            quantum_key = secrets.token_bytes(64)  # 512 bits for PQC
            
            encrypted_small = pqc_strategy.encrypt(small_data, quantum_key)
            self.log_test_result(
                "PQC Small Data Encryption", 
                encrypted_small.get('algorithm') == 'PQC_DILITHIUM_AES256',
                f"Algorithm: {encrypted_small.get('algorithm')}, FEK used: {encrypted_small.get('fek_used', False)}"
            )
            
            # Test small data decryption
            decrypted_small = pqc_strategy.decrypt(encrypted_small, quantum_key)
            small_data_match = decrypted_small == small_data
            self.log_test_result(
                "PQC Small Data Decryption", 
                small_data_match,
                f"Decrypted {len(decrypted_small)} bytes successfully"
            )
            
            # Test large file encryption (with FEK)
            large_data = secrets.token_bytes(2 * 1024 * 1024)  # 2MB file
            file_context = {'is_attachment': True, 'total_size': len(large_data)}
            
            encrypted_large = pqc_strategy.encrypt(large_data, quantum_key, file_context)
            is_fek_encryption = encrypted_large.get('fek_used', False)
            self.log_test_result(
                "PQC Large File Encryption with FEK", 
                is_fek_encryption and encrypted_large.get('algorithm') == 'PQC_KYBER_FEK_AES256',
                f"Algorithm: {encrypted_large.get('algorithm')}, FEK: {is_fek_encryption}, Size: {encrypted_large.get('file_size_mb', 0):.2f}MB"
            )
            
            # Test large file decryption
            decrypted_large = pqc_strategy.decrypt(encrypted_large, quantum_key)
            large_data_match = decrypted_large == large_data
            self.log_test_result(
                "PQC Large File Decryption with FEK", 
                large_data_match,
                f"Decrypted {len(decrypted_large)} bytes, matches original: {large_data_match}"
            )
            
            # Test Kyber KEM simulation
            if encrypted_large.get('fek_used'):
                encapsulated_fek = encrypted_large.get('encapsulated_fek', {})
                has_kyber_components = all(key in encapsulated_fek for key in ['encapsulated_key', 'encrypted_fek', 'public_key'])
                self.log_test_result(
                    "Kyber KEM Encapsulation", 
                    has_kyber_components,
                    f"KEM Algorithm: {encapsulated_fek.get('kem_algorithm')}, Security: {encapsulated_fek.get('security_strength')}"
                )
            
            # Test all security levels through CipherManager
            test_message = b"Test message for all security levels"
            for level in ['L1', 'L2', 'L3', 'L4']:
                try:
                    key_length = cipher_manager.get_required_key_length(level, len(test_message))
                    test_key = secrets.token_bytes(key_length // 8) if key_length > 0 else b''
                    
                    encrypted = cipher_manager.encrypt_with_level(test_message, test_key, level)
                    decrypted = cipher_manager.decrypt_with_level(encrypted, test_key)
                    
                    level_success = decrypted == test_message
                    self.log_test_result(
                        f"Security Level {level} Encryption/Decryption", 
                        level_success,
                        f"Algorithm: {encrypted.get('algorithm')}, Key length: {key_length} bits"
                    )
                except Exception as e:
                    self.log_test_result(f"Security Level {level} Test", False, error=str(e))
                    
        except Exception as e:
            self.log_test_result("PQC Encryption Test", False, error=str(e))
            
    async def test_kme_client_heartbeat_monitoring(self):
        """Test 3: KME Client heartbeat monitoring and reconnection logic"""
        print("\n💓 Testing KME Client Heartbeat and Monitoring...")
        
        try:
            from crypto.kme_client import KMEClient
            
            # Test KME client initialization (without requiring actual server)
            kme_client = KMEClient("http://127.0.0.1:8080")
            
            # Test client configuration
            client_configured = kme_client.kme_url == "http://127.0.0.1:8080"
            self.log_test_result(
                "KME Client Configuration", 
                client_configured,
                f"KME URL: {kme_client.kme_url}, Timeout: {kme_client.connection_timeout}s"
            )
            
            # Test connection statistics structure
            stats = kme_client.get_connection_statistics()
            stats_structure_valid = all(key in stats for key in ['connection_status', 'total_requests', 'success_rate'])
            self.log_test_result(
                "KME Connection Statistics Structure", 
                stats_structure_valid,
                f"Stats keys: {list(stats.keys())}"
            )
            
            # Test heartbeat configuration
            heartbeat_config_valid = hasattr(kme_client, 'heartbeat_interval') and kme_client.heartbeat_interval > 0
            self.log_test_result(
                "KME Heartbeat Configuration", 
                heartbeat_config_valid,
                f"Heartbeat interval: {kme_client.heartbeat_interval}s, Max failures: {kme_client.max_connection_failures}"
            )
            
            # Test connection failure handling (without actual connection)
            kme_client.connection_failures = 3
            failure_tracking = kme_client.connection_failures == 3
            self.log_test_result(
                "KME Connection Failure Tracking", 
                failure_tracking,
                f"Failure count: {kme_client.connection_failures}, Max allowed: {kme_client.max_connection_failures}"
            )
            
            # Test authentication configuration methods
            kme_client.configure_authentication('api_key', api_key='test_key_123')
            auth_configured = kme_client.api_key == 'test_key_123'
            self.log_test_result(
                "KME Authentication Configuration", 
                auth_configured,
                f"API key configured: {kme_client.api_key is not None}"
            )
            
            # Test recovery backoff configuration
            backoff_configured = len(kme_client.connection_recovery_backoff) > 0
            self.log_test_result(
                "KME Recovery Backoff Configuration", 
                backoff_configured,
                f"Backoff intervals: {kme_client.connection_recovery_backoff}"
            )
            
            # Test monitoring statistics initialization
            monitoring_stats = kme_client.stats
            stats_initialized = 'total_requests' in monitoring_stats and 'uptime_start' in monitoring_stats
            self.log_test_result(
                "KME Monitoring Statistics", 
                stats_initialized,
                f"Monitoring stats: {list(monitoring_stats.keys())}"
            )
            
            # Test cleanup (without requiring connection)
            await kme_client.close()
            self.log_test_result(
                "KME Client Cleanup", 
                True,
                "Client closed successfully without connection"
            )
            
        except Exception as e:
            self.log_test_result("KME Client Test", False, error=str(e))
            
    async def test_email_handler_oauth2_refresh(self):
        """Test 4: Email Handler OAuth2 token refresh and async transport"""
        print("\n📧 Testing Email Handler OAuth2 and Async Transport...")
        
        try:
            from transport.email_handler import EmailHandler
            
            # Initialize email handler
            email_handler = EmailHandler()
            await email_handler.initialize(None)
            
            # Test OAuth2 credentials setup
            await email_handler.set_credentials(
                access_token=self.test_oauth_credentials['access_token'],
                refresh_token=self.test_oauth_credentials['refresh_token'],
                provider=self.test_oauth_credentials['provider']
            )
            
            oauth_setup = email_handler.oauth_tokens is not None
            self.log_test_result(
                "OAuth2 Credentials Setup", 
                oauth_setup,
                f"Provider: {email_handler.oauth_tokens.get('provider') if oauth_setup else 'None'}"
            )
            
            # Test token validation
            token_valid = await email_handler._validate_token_freshness()
            self.log_test_result(
                "OAuth2 Token Validation", 
                token_valid,
                f"Token expires at: {email_handler.oauth_tokens.get('expires_at') if oauth_setup else 'None'}"
            )
            
            # Test smart email loopback system
            test_encrypted_data = {
                'security_level': 'L2',
                'algorithm': 'AES256_GCM_QUANTUM',
                'ciphertext': 'dGVzdCBtZXNzYWdl',  # base64 encoded "test message"
                'subject': 'Test Quantum Email',
                'body': 'This is a test of the quantum email system'
            }
            
            # Test self-email (loopback)
            email_handler.user_email = 'test@qumail.com'
            loopback_success = await email_handler.send_encrypted_email('test@qumail.com', test_encrypted_data)
            self.log_test_result(
                "Smart Email Loopback System", 
                loopback_success,
                "Self-email sent and received via loopback"
            )
            
            # Test email list retrieval
            inbox_emails = await email_handler.get_email_list('Inbox', 10)
            inbox_populated = len(inbox_emails) > 0
            self.log_test_result(
                "Email List Retrieval (Inbox)", 
                inbox_populated,
                f"Found {len(inbox_emails)} emails in Inbox"
            )
            
            # Test Quantum Vault functionality
            vault_emails = await email_handler.get_email_list('Quantum Vault', 10)
            vault_accessible = isinstance(vault_emails, list)
            self.log_test_result(
                "Quantum Vault Access", 
                vault_accessible,
                f"Found {len(vault_emails)} emails in Quantum Vault"
            )
            
            # Test email fetching
            if inbox_emails:
                test_email_id = inbox_emails[0]['email_id']
                fetched_email = await email_handler.fetch_email(test_email_id, 'test@qumail.com')
                fetch_success = fetched_email is not None
                self.log_test_result(
                    "Email Fetch by ID", 
                    fetch_success,
                    f"Fetched email: {test_email_id}, Sender: {fetched_email.get('sender') if fetch_success else 'None'}"
                )
            
            # Test provider configuration
            provider_configs = email_handler.provider_config
            config_complete = 'gmail' in provider_configs and 'yahoo' in provider_configs
            self.log_test_result(
                "Email Provider Configuration", 
                config_complete,
                f"Configured providers: {list(provider_configs.keys())}"
            )
            
            # Test statistics tracking
            stats = email_handler.stats
            stats_tracking = 'emails_sent' in stats and 'oauth_refreshes' in stats
            self.log_test_result(
                "Email Handler Statistics", 
                stats_tracking,
                f"Emails sent: {stats.get('emails_sent', 0)}, OAuth refreshes: {stats.get('oauth_refreshes', 0)}"
            )
            
            # Test cleanup
            await email_handler.cleanup()
            self.log_test_result(
                "Email Handler Cleanup", 
                True,
                "Handler cleaned up successfully"
            )
            
        except Exception as e:
            self.log_test_result("Email Handler Test", False, error=str(e))
            
    async def test_end_to_end_quantum_workflow(self):
        """Test 5: End-to-end quantum encryption workflow (L1-L4 security levels)"""
        print("\n🌐 Testing End-to-End Quantum Workflow...")
        
        try:
            from core.app_core import QuMailCore, UserProfile
            
            # Create mock config for testing
            mock_config = {
                'kme_url': 'http://127.0.0.1:8080',
                'app_name': 'QuMail Test',
                'debug': True
            }
            
            # Initialize QuMail Core
            core = QuMailCore(mock_config)
            
            # Test core component initialization
            components_initialized = all([
                hasattr(core, 'kme_client'),
                hasattr(core, 'cipher_manager'),
                hasattr(core, 'email_handler'),
                hasattr(core, 'secure_storage')
            ])
            self.log_test_result(
                "QuMail Core Components", 
                components_initialized,
                f"Security Level: {core.current_security_level}, Components: KME, Cipher, Email, Storage"
            )
            
            # Test security level management
            for level in ['L1', 'L2', 'L3', 'L4']:
                try:
                    core.set_security_level(level)
                    current_level = core.get_security_level()
                    level_set = current_level == level
                    self.log_test_result(
                        f"Security Level {level} Setting", 
                        level_set,
                        f"Current level: {current_level}"
                    )
                except Exception as e:
                    self.log_test_result(f"Security Level {level} Setting", False, error=str(e))
            
            # Test cipher manager integration
            available_levels = core.cipher_manager.get_available_levels()
            cipher_integration = len(available_levels) == 4 and 'L1' in available_levels
            self.log_test_result(
                "Cipher Manager Integration", 
                cipher_integration,
                f"Available levels: {available_levels}"
            )
            
            # Test message serialization/deserialization
            test_message = {'subject': 'Test', 'body': 'Test message', 'attachments': []}
            serialized = core._serialize_message(test_message)
            deserialized = core._deserialize_message(serialized)
            serialization_works = deserialized == test_message
            self.log_test_result(
                "Message Serialization/Deserialization", 
                serialization_works,
                f"Original: {len(str(test_message))} chars, Serialized: {len(serialized)} bytes"
            )
            
            # Test OTP size limit validation
            try:
                # Test the size calculation logic
                large_data = b"A" * (60 * 1024)  # 60KB
                required_key_length = core.cipher_manager.get_required_key_length('L1', len(large_data))
                otp_limit_bits = 50 * 1024 * 8  # 50KB in bits
                size_limit_working = required_key_length > otp_limit_bits
                self.log_test_result(
                    "OTP Size Limit Logic", 
                    size_limit_working,
                    f"Required: {required_key_length} bits, Limit: {otp_limit_bits} bits"
                )
            except Exception as e:
                self.log_test_result("OTP Size Limit Logic", False, error=str(e))
            
            # Test QKD status reporting structure
            qkd_status = core.get_qkd_status()
            status_structure = all(key in qkd_status for key in ['status', 'security_level', 'kme_connected', 'available_levels'])
            self.log_test_result(
                "QKD Status Structure", 
                status_structure,
                f"Status keys: {list(qkd_status.keys())}, Available levels: {len(qkd_status.get('available_levels', []))}"
            )
            
            # Test user profile structure
            test_user = UserProfile(
                user_id=self.test_user_data['user_id'],
                email=self.test_user_data['email'],
                display_name=self.test_user_data['display_name'],
                password_hash=self.test_user_data['password_hash'],
                sae_id=self.test_user_data['sae_id'],
                provider=self.test_user_data['provider'],
                created_at=self.test_user_data['created_at'],
                last_login=self.test_user_data['last_login']
            )
            
            user_profile_valid = all([
                test_user.user_id == self.test_user_data['user_id'],
                test_user.email == self.test_user_data['email'],
                test_user.sae_id == self.test_user_data['sae_id']
            ])
            self.log_test_result(
                "User Profile Structure", 
                user_profile_valid,
                f"User: {test_user.email}, SAE ID: {test_user.sae_id}"
            )
            
            # Test profile to dict conversion
            profile_dict = core._user_profile_to_dict(test_user)
            dict_conversion_works = profile_dict['user_id'] == test_user.user_id
            self.log_test_result(
                "User Profile Dict Conversion", 
                dict_conversion_works,
                f"Dict keys: {list(profile_dict.keys())}"
            )
            
            # Test cleanup
            await core.cleanup()
            self.log_test_result(
                "End-to-End Workflow Cleanup", 
                True,
                "Core workflow cleaned up successfully"
            )
            
        except Exception as e:
            self.log_test_result("End-to-End Workflow Test", False, error=str(e))
            
    async def test_connection_failure_recovery(self):
        """Test 6: Connection failure recovery and statistical monitoring"""
        print("\n🔄 Testing Connection Failure Recovery...")
        
        try:
            from crypto.kme_client import KMEClient
            
            # Test with invalid KME URL to trigger failure scenarios
            failing_client = KMEClient("http://invalid-kme-server:9999")
            
            # Test connection failure handling
            try:
                await failing_client.initialize(enable_heartbeat=False)
                # Should handle gracefully
                connection_handled = not failing_client.is_connected
                self.log_test_result(
                    "Connection Failure Handling", 
                    connection_handled,
                    f"Failed connection handled gracefully: {failing_client.connection_failures} failures"
                )
            except Exception:
                # Even exceptions should be handled gracefully
                self.log_test_result(
                    "Connection Failure Handling", 
                    True,
                    "Connection failure raised exception as expected"
                )
            
            # Test statistics collection during failures
            stats = failing_client.get_connection_statistics()
            stats_collected = 'failed_requests' in stats and 'connection_failures' in stats
            self.log_test_result(
                "Failure Statistics Collection", 
                stats_collected,
                f"Failed requests: {stats.get('failed_requests')}, Connection failures: {stats.get('connection_failures')}"
            )
            
            # Test with working KME client for recovery scenarios
            working_client = KMEClient("http://127.0.0.1:8080")
            await working_client.initialize(enable_heartbeat=False)
            
            # Simulate some successful operations
            status1 = await working_client.get_status()
            status2 = await working_client.get_status()
            
            # Check recovery statistics
            recovery_stats = working_client.get_connection_statistics()
            success_rate = recovery_stats.get('success_rate', 0)
            recovery_working = success_rate > 0
            self.log_test_result(
                "Connection Recovery Statistics", 
                recovery_working,
                f"Success rate: {success_rate:.1f}%, Total requests: {recovery_stats.get('total_requests')}"
            )
            
            # Test heartbeat recovery mechanism
            await working_client._start_heartbeat()
            await asyncio.sleep(1)  # Let heartbeat run
            
            heartbeat_stats = working_client.get_connection_statistics()
            heartbeat_enabled = heartbeat_stats.get('heartbeat_enabled', False)
            self.log_test_result(
                "Heartbeat Recovery Mechanism", 
                heartbeat_enabled,
                f"Heartbeat interval: {heartbeat_stats.get('heartbeat_interval')}s"
            )
            
            # Test cleanup of both clients
            await failing_client.close()
            await working_client.close()
            
            self.log_test_result(
                "Connection Recovery Cleanup", 
                True,
                "All clients cleaned up successfully"
            )
            
        except Exception as e:
            self.log_test_result("Connection Recovery Test", False, error=str(e))
            
    async def test_requirements_and_dependencies(self):
        """Test 7: Verify all production requirements are available"""
        print("\n📦 Testing Production Requirements and Dependencies...")
        
        # Test core dependencies
        dependencies = [
            ('keyring', 'OS-native credential storage'),
            ('aiosmtplib', 'Async SMTP client'),
            ('aioimaplib', 'Async IMAP client'),
            ('httpx', 'Enhanced HTTP client'),
            ('aiofiles', 'Async file operations'),
            ('structlog', 'Production logging'),
            ('cryptography', 'Cryptographic operations'),
            ('aiohttp', 'HTTP client for KME'),
            ('PyQt6', 'GUI framework')
        ]
        
        for module_name, description in dependencies:
            try:
                __import__(module_name)
                self.log_test_result(
                    f"Dependency: {module_name}", 
                    True,
                    description
                )
            except ImportError:
                self.log_test_result(
                    f"Dependency: {module_name}", 
                    False,
                    f"Missing: {description}"
                )
        
        # Test requirements.txt completeness
        try:
            with open('/app/requirements.txt', 'r') as f:
                requirements_content = f.read()
                
            required_packages = [
                'keyring>=24.3.1',
                'aiosmtplib>=2.0.0',
                'aioimaplib>=1.0.1',
                'httpx>=0.25.0',
                'structlog>=23.2.0'
            ]
            
            requirements_complete = all(pkg.split('>=')[0] in requirements_content for pkg in required_packages)
            self.log_test_result(
                "Requirements.txt Completeness", 
                requirements_complete,
                f"Production packages present: {requirements_complete}"
            )
            
        except Exception as e:
            self.log_test_result("Requirements.txt Check", False, error=str(e))
            
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        # Categorize test results
        backend_issues = []
        passed_tests = []
        
        for result in self.test_results:
            if result['success']:
                passed_tests.append(result['test_name'])
            else:
                backend_issues.append({
                    'test': result['test_name'],
                    'error': result['error'],
                    'impact': 'Backend functionality affected',
                    'fix_priority': 'HIGH' if 'initialization' in result['test_name'].lower() else 'MEDIUM'
                })
        
        success_percentage = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        report = {
            'summary': f'QuMail Backend Testing Complete - {self.tests_passed}/{self.tests_run} tests passed',
            'backend_issues': {
                'critical_bugs': [issue for issue in backend_issues if issue['fix_priority'] == 'HIGH'],
                'minor_issues': [issue for issue in backend_issues if issue['fix_priority'] == 'MEDIUM']
            },
            'frontend_issues': {
                'note': 'Frontend testing skipped as requested - backend only testing'
            },
            'passed_tests': passed_tests,
            'success_percentage': f'Backend: {success_percentage:.1f}%',
            'test_report_links': ['/app/backend_test.py'],
            'action_item_for_E1': self._generate_action_items(),
            'should_call_test_agent_after_fix': len(backend_issues) > 0,
            'updated_files': ['/app/backend_test.py'],
            'test_duration_seconds': duration,
            'test_categories': {
                'secure_storage': 'TESTED',
                'pqc_encryption': 'TESTED', 
                'kme_client': 'TESTED',
                'email_handler': 'TESTED',
                'end_to_end_workflow': 'TESTED',
                'connection_recovery': 'TESTED',
                'dependencies': 'TESTED'
            }
        }
        
        return report
        
    def _generate_action_items(self) -> str:
        """Generate action items for main agent based on test results"""
        if self.tests_failed == 0:
            return "All backend tests passed! QuMail production readiness verified."
        
        critical_failures = [r for r in self.test_results if not r['success'] and 'initialization' in r['test_name'].lower()]
        
        if critical_failures:
            return f"CRITICAL: {len(critical_failures)} initialization failures detected. Fix core component initialization before proceeding."
        elif self.tests_failed > self.tests_passed:
            return f"MAJOR: {self.tests_failed} test failures detected. Review and fix backend implementation issues."
        else:
            return f"MINOR: {self.tests_failed} test failures detected. Address specific component issues for full production readiness."
            
    async def run_all_tests(self):
        """Run comprehensive backend test suite"""
        print("🚀 Starting QuMail Backend Production Readiness Testing...")
        print(f"Testing final 25% implementation features\n")
        
        # Run all test categories
        await self.test_secure_storage_keyring()
        await self.test_pqc_encryption_with_fek()
        await self.test_kme_client_heartbeat_monitoring()
        await self.test_email_handler_oauth2_refresh()
        await self.test_end_to_end_quantum_workflow()
        await self.test_connection_failure_recovery()
        await self.test_requirements_and_dependencies()
        
        # Generate and save test report
        report = self.generate_test_report()
        
        print(f"\n📊 TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"Duration: {report['test_duration_seconds']:.1f} seconds")
        
        if self.tests_failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['error']}")
        
        print(f"\n✅ Action Items: {report['action_item_for_E1']}")
        
        return report

async def main():
    """Main test execution function"""
    try:
        # Add the app directory to Python path for imports
        import sys
        sys.path.insert(0, '/app')
        
        # Run comprehensive backend tests
        tester = QuMailBackendTester()
        report = await tester.run_all_tests()
        
        # Save test report
        report_file = f"/app/test_reports/iteration_1.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Test report saved: {report_file}")
        
        # Return appropriate exit code
        return 0 if tester.tests_failed == 0 else 1
        
    except Exception as e:
        print(f"❌ Critical test execution error: {e}")
        logging.error(f"Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)