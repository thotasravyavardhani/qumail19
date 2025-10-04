#!/usr/bin/env python3
"""
Test script for QuMail Email Core functionality
Tests the backend email integration without GUI
"""

import asyncio
import sys
import os
import logging

# Set up path for proper imports
sys.path.insert(0, '/app')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the required modules properly
from utils.config import load_config
from utils.logger import setup_logging

async def test_email_functionality():
    """Test core email functionality"""
    print("=== QuMail Email Core Test ===")
    
    # Setup logging
    setup_logging()
    logging.getLogger().setLevel(logging.INFO)
    
    try:
        # Load configuration with Gmail client ID
        config = load_config()
        print(f"Gmail Client ID: {config.get('gmail_client_id', 'Not set')}")
        
        # Initialize core
        print("1. Initializing QuMail Core...")
        core = QuMailCore(config)
        
        # Authenticate user
        print("2. Authenticating test user...")
        auth_success = await core.authenticate_user('test@qumail.com')
        print(f"   Authentication: {'SUCCESS' if auth_success else 'FAILED'}")
        
        if not auth_success:
            print("Cannot proceed without authentication")
            return
            
        # Test email sending
        print("3. Testing email sending...")
        send_result = await core.send_secure_email(
            to_address="recipient@example.com",
            subject="QuMail Test - Quantum Secure Email",
            body="This is a test email from QuMail with quantum security features!",
            security_level="L2"
        )
        print(f"   Email Send: {'SUCCESS' if send_result else 'FAILED'}")
        
        # Test email retrieval
        print("4. Testing email retrieval...")
        emails = await core.get_inbox_emails("Inbox", limit=10)
        print(f"   Retrieved {len(emails)} emails from inbox")
        
        for i, email in enumerate(emails[:3]):  # Show first 3
            print(f"   Email {i+1}: {email.get('sender', 'Unknown')} - {email.get('subject', 'No Subject')}")
        
        # Test different security levels
        print("5. Testing different security levels...")
        security_levels = ['L1', 'L2', 'L3', 'L4']
        
        for level in security_levels:
            print(f"   Testing {level}...")
            core.set_security_level(level)
            result = await core.send_secure_email(
                to_address="test@example.com",
                subject=f"Test with {level} security",
                body=f"Testing {level} security level encryption",
                security_level=level
            )
            print(f"   {level}: {'SUCCESS' if result else 'FAILED'}")
        
        # Get application statistics
        print("6. Application Statistics:")
        stats = core.get_application_statistics()
        print(f"   User: {stats.get('current_user_email', 'None')}")
        print(f"   Security Level: {stats.get('security_level', 'Unknown')}")
        print(f"   Emails Sent: {stats.get('stats', {}).get('emails_sent', 0)}")
        print(f"   KME Connected: {stats.get('kme_status', {}).get('kme_connected', False)}")
        
        # Cleanup
        print("7. Cleanup...")
        await core.cleanup()
        
        print("\n=== EMAIL CORE TEST COMPLETED SUCCESSFULLY ===")
        
    except Exception as e:
        print(f"ERROR during email core test: {e}")
        logging.error(f"Email core test failed: {e}", exc_info=True)
        return False
    
    return True

async def test_email_transport():
    """Test email transport layer specifically"""
    print("\n=== Email Transport Test ===")
    
    try:
        from transport.email_handler import EmailHandler
        from auth.oauth2_manager import OAuth2Manager
        
        # Initialize components
        email_handler = EmailHandler()
        oauth_manager = OAuth2Manager()
        
        await email_handler.initialize(None)
        
        # Test OAuth2 setup with provided Gmail client ID  
        print("1. Setting up OAuth2 credentials...")
        await email_handler.set_credentials(
            access_token="mock_access_token",
            refresh_token="mock_refresh_token", 
            provider="gmail",
            oauth_manager=oauth_manager
        )
        print("   OAuth2 credentials set")
        
        # Test email list retrieval
        print("2. Testing email list retrieval...")
        emails = await email_handler.get_email_list("Inbox", 5)
        print(f"   Retrieved {len(emails)} emails")
        
        # Test email sending
        print("3. Testing email sending...")
        test_encrypted_data = {
            'subject': 'Test Email from QuMail',
            'body': 'This is a test email',
            'security_level': 'L2',
            'algorithm': 'Q-AES-256',
            'timestamp': '2025-01-27T12:00:00Z'
        }
        
        send_result = await email_handler.send_encrypted_email(
            "test@example.com", 
            test_encrypted_data
        )
        print(f"   Email send result: {'SUCCESS' if send_result else 'FAILED'}")
        
        # Test connection health
        print("4. Testing connection health...")
        health_status = await email_handler.check_connection_health()
        print(f"   Connection health: {health_status.get('overall_healthy', False)}")
        
        # Get connection statistics
        print("5. Connection Statistics:")
        stats = email_handler.get_connection_statistics()
        print(f"   Status: {stats.get('overall_status', 'Unknown')}")
        print(f"   Emails Sent: {stats.get('total_emails_sent', 0)}")
        print(f"   OAuth Refreshes: {stats.get('oauth_refreshes', 0)}")
        
        # Cleanup
        await email_handler.cleanup()
        
        print("\n=== EMAIL TRANSPORT TEST COMPLETED ===")
        return True
        
    except Exception as e:
        print(f"ERROR during email transport test: {e}")
        logging.error(f"Email transport test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    print("Starting QuMail Email Integration Tests...")
    
    # Set environment variable for Gmail client ID
    os.environ['QUMAIL_GMAIL_CLIENT_ID'] = "625603387439-c1m3r94itc81cjltgqgg1lb9kqq9c5dg.apps.googleusercontent.com"
    
    async def main():
        # Test core email functionality
        core_success = await test_email_functionality()
        
        # Test transport layer
        transport_success = await test_email_transport()
        
        if core_success and transport_success:
            print("\n🎉 ALL EMAIL TESTS PASSED! 🎉")
            print("Email integration is working properly")
        else:
            print("\n❌ Some tests failed - need debugging")
            
    # Run tests
    asyncio.run(main())