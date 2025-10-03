#!/usr/bin/env python3
"""
Test script to verify the persistence fix works correctly
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, '/app')

from db.secure_storage import SecureStorage
from core.app_core import QuMailCore, UserProfile

async def test_persistence_fix():
    """Test the user profile persistence fix"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    print("🔧 Testing QuMail Persistence Fix...")
    
    try:
        # Initialize secure storage
        storage = SecureStorage("/tmp/test_qumail.db")
        await storage.initialize()
        
        # Create a test user profile
        test_profile = UserProfile(
            user_id="test_user_123",
            email="test@qumail.com",
            display_name="Test User",
            sae_id="qumail_test_user_123",
            provider="qumail_native",
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        
        # Test the core's _user_profile_to_dict method
        core = QuMailCore({'kme_url': 'http://127.0.0.1:8080'})
        profile_dict = core._user_profile_to_dict(test_profile)
        
        print(f"📝 Profile dict generated: {profile_dict}")
        
        # Verify the dict has the correct fields
        expected_fields = ['user_id', 'email', 'display_name', 'sae_id', 'provider', 'created_at', 'updated_at']
        missing_fields = [field for field in expected_fields if field not in profile_dict]
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
            
        if 'last_login' in profile_dict:
            print("❌ Profile dict still contains 'last_login' field - should be 'updated_at'")
            return False
            
        print("✅ Profile dict has correct field mapping")
        
        # Test saving the profile
        save_success = await storage.save_user_profile(profile_dict)
        
        if not save_success:
            print("❌ Failed to save user profile")
            return False
            
        print("✅ User profile saved successfully")
        
        # Test loading the profile
        loaded_profile = await storage.load_user_profile("test_user_123")
        
        if not loaded_profile:
            print("❌ Failed to load user profile")
            return False
            
        print(f"📖 Profile loaded: {loaded_profile}")
        
        # Verify the loaded profile has correct fields
        if 'updated_at' in loaded_profile:
            print("❌ Loaded profile contains 'updated_at' - should be mapped to 'last_login'")
            return False
            
        if 'last_login' not in loaded_profile:
            print("❌ Loaded profile missing 'last_login' field")
            return False
            
        print("✅ Profile loaded with correct field mapping")
        
        # Test that we can recreate UserProfile from loaded data
        try:
            # Convert string timestamps back to datetime objects
            loaded_profile['created_at'] = datetime.fromisoformat(loaded_profile['created_at'])
            loaded_profile['last_login'] = datetime.fromisoformat(loaded_profile['last_login'])
            
            recreated_profile = UserProfile(**loaded_profile)
            print(f"✅ UserProfile recreated: {recreated_profile.email}")
        except Exception as e:
            print(f"❌ Failed to recreate UserProfile: {e}")
            return False
        
        # Clean up
        await storage.close()
        
        print("🎉 All persistence tests passed! The fix is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_persistence_fix())
    sys.exit(0 if result else 1)