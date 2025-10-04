#!/usr/bin/env python3
"""
Real Email Handler Test - Test actual EmailHandler with real-world token logic.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

# --- MOCK DEPENDENCIES (for Test Isolation and Stability) ---
# We use this to satisfy the `from utils.config import load_config` import.
class MockConfigModule:
    """Mock object to stand in for the 'utils.config' module."""
    def load_config():
        # Using real Google Client ID/Secret for the Google OAuth provider configuration
        return {
            'gmail_client_id': '625603387439-c1m3r94itc81cjltgqgg1lb9kqq9c5dg.apps.googleusercontent.com',
            'gmail_client_secret': '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',
        }

# --- CRITICAL FIX: REAL-WORLD MOCK OAUTH MANAGER ---
# This simulates a production-ready OAuth2Manager that successfully refreshes the token.
class RealWorldMockOAuth2Manager:
    """Simulates an OAuth2Manager with a *real, persistent* refresh token."""
    def __init__(self):
        self.real_refresh_token = "MOCK_PERSISTENT_REFRESH_TOKEN_FOR_TEST" 

    async def ensure_valid_token(self, provider: str, user_id: str) -> Optional[str]:
        """Simulates successful token refresh and returns a valid access token."""
        if provider.lower() == 'gmail' and user_id == 'test@qumail.com':
            logging.info("OAUTH FIX: Simulating token refresh and returning a hardcoded fresh token.")
            # This is the token the EmailHandler should store internally.
            return "MOCK_FRESH_ACCESS_TOKEN_FOR_XOAUTH2"
        return None

# --- ENVIRONMENT SETUP ---
def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add project root to sys.path to resolve sub-package paths
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(current_dir))

# --- DYNAMICALLY LOAD EMAIL HANDLER ---
# Temporarily mock the utils.config module
sys.modules['utils.config'] = MockConfigModule

# Use dynamic loading to get EmailHandler
try:
    import importlib.util
    file_path = current_dir / "transport" / "email_handler.py"
    spec = importlib.util.spec_from_file_location("email_handler", file_path)
    email_handler_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(email_handler_module)
    EmailHandler = email_handler_module.EmailHandler

except Exception as e:
    # If standard import fails, EmailHandler will be defined as a Mock to prevent crashing
    logging.error(f"FATAL: Could not import EmailHandler module: {e}")
    class EmailHandler:
        def __init__(self): pass
        async def initialize(self, *args): pass
        async def set_credentials(self, *args): pass
        async def send_encrypted_email(self, *args): return False
        async def get_email_list(self, *args): return []
        async def check_connection_health(self): return {'oauth_valid': False, 'overall_healthy': False}
        async def cleanup(self): pass
        def get_connection_statistics(self): return {}
    raise e
finally:
    # Clean up the mock module
    if 'utils.config' in sys.modules and sys.modules['utils.config'] is MockConfigModule:
        del sys.modules['utils.config']


# --- TEST CORE ---
async def test_email_handler_oauth_connectivity():
    """Focuses specifically on successful OAuth token update logic integration."""
    print("=== Testing Email Handler OAuth Integration ===")

    oauth_manager = RealWorldMockOAuth2Manager()
    
    try:
        email_handler = EmailHandler()
        # CRITICAL FIX 1: Set a user_id on the handler instance.
        email_handler.user_id = 'test@qumail.com' 
        
        await email_handler.initialize(type('obj', (object,), {'email': email_handler.user_id}))
        
        # 1. Set expired/old credentials initially
        initial_token = "OLD_EXPIRED_TOKEN"
        fresh_expected_token = "MOCK_FRESH_ACCESS_TOKEN_FOR_XOAUTH2"
        await email_handler.set_credentials(
            initial_token, 
            oauth_manager.real_refresh_token, 
            "gmail", 
            oauth_manager
        )
        print(f"Initial token: {email_handler.oauth_tokens.get('access_token')}")
        print("✓ Credentials set successfully.")

        # 2. Trigger the pre-connection validation by sending an email
        # This will call the mocked `ensure_valid_token` and update `self.oauth_tokens['access_token']`.
        print("Attempting to send email to trigger OAuth token check...")
        await email_handler.send_encrypted_email(
            "recipient@example.com", 
            {"encrypted_data": "payload", "security_level": "L1"}
        )
        
        # 3. CRITICAL FIX 2: Check the access token after the operation
        final_token = email_handler.oauth_tokens.get('access_token')
        
        print("\n--- OAuth Check Results ---")
        print(f"Final token in Handler: {final_token}")

        # The EmailHandler should have successfully called the mock manager and updated its token
        assert final_token == fresh_expected_token, \
            f"Expected token '{fresh_expected_token}' but found '{final_token}'."
        print("✓ Access token refresh logic successfully integrated and verified.")

        # Test passes if the token was updated
        return True
    
    except AssertionError as e:
        logging.error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        logging.error(f"OAuth Integration Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if 'email_handler' in sys.modules and 'email_handler' in locals():
            await email_handler.cleanup()


async def main():
    setup_logging()
    
    print("🔧 QuMail Email Handler OAuth Fix Test")
    print("=" * 60)
    
    test_name = "Email Handler OAuth Integration"
    print(f"\n🧪 Running {test_name} test...")
    result = await test_email_handler_oauth_connectivity()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"{test_name}: {status}")
    
    if result:
        print("\n🎉 ALL CRITICAL OAUTH LOGIC PASSED!")
        print("The EmailHandler can now correctly coordinate token refresh with the OAuth2Manager.")
    else:
        print("\n⚠️  Critical OAuth logic failed.")

if __name__ == "__main__":
    asyncio.run(main())