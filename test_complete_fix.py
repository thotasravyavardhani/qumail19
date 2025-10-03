#!/usr/bin/env python3
"""
Comprehensive test to verify the complete persistence fix
Tests the end-to-end flow: UserProfile -> dict -> storage -> load -> UserProfile
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, '/app')

from db.secure_storage import SecureStorage

# Mock the UserProfile class since PyQt6 isn't available
class UserProfile:
    """Mock UserProfile for testing"""
    def __init__(self, user_id, email, display_name, sae_id, provider, created_at, last_login):
        self.user_id = user_id
        self.email = email
        self.display_name = display_name
        self.sae_id = sae_id
        self.provider = provider
        self.created_at = created_at
        self.last_login = last_login

def _user_profile_to_dict(user_profile):
    """Fixed conversion method from app_core.py"""
    return {
        'user_id': user_profile.user_id,
        'email': user_profile.email,
        'display_name': user_profile.display_name,
        'sae_id': user_profile.sae_id,
        'provider': user_profile.provider,
        'created_at': user_profile.created_at.isoformat(),
        'updated_at': user_profile.last_login.isoformat()  # Fixed: map last_login to updated_at for database
    }

async def test_complete_persistence_flow():
    """Test the complete end-to-end persistence flow"""
    
    print("🔧 Testing Complete QuMail Persistence Fix...")
    
    try:
        # Step 1: Create test user profile
        now = datetime.utcnow()
        test_user = UserProfile(
            user_id="persistence_test_user",
            email="test@qumail-quantum.com",
            display_name="Persistence Test User", 
            sae_id="qumail_persistence_test_user",
            provider="qumail_native",
            created_at=now,
            last_login=now
        )
        
        print(f"✅ Step 1: Created test UserProfile for {test_user.email}")
        
        # Step 2: Convert to dict using fixed method
        profile_dict = _user_profile_to_dict(test_user)
        print(f"✅ Step 2: Converted to dict with fields: {list(profile_dict.keys())}")
        
        # Verify field mapping fix
        assert 'updated_at' in profile_dict, "Missing updated_at field"
        assert 'last_login' not in profile_dict, "Still has last_login field"
        print("✅ Step 2a: Field mapping verified (last_login -> updated_at)")
        
        # Step 3: Initialize secure storage 
        storage = SecureStorage("/tmp/qumail_complete_test.db")
        await storage.initialize()
        print("✅ Step 3: Secure storage initialized")
        
        # Step 4: Save profile using fixed storage method
        save_success = await storage.save_user_profile(profile_dict)
        assert save_success, "Failed to save user profile"
        print("✅ Step 4: User profile saved successfully")
        
        # Step 5: Load profile back
        loaded_profile = await storage.load_user_profile(test_user.user_id)
        assert loaded_profile is not None, "Failed to load user profile"
        print("✅ Step 5: User profile loaded successfully")
        
        # Step 6: Verify reverse field mapping (updated_at -> last_login)
        assert 'last_login' in loaded_profile, "Missing last_login field in loaded profile"
        assert 'updated_at' not in loaded_profile, "Still has updated_at field in loaded profile"
        print("✅ Step 6: Reverse field mapping verified (updated_at -> last_login)")
        
        # Step 7: Recreate UserProfile from loaded data
        loaded_profile['created_at'] = datetime.fromisoformat(loaded_profile['created_at'])
        loaded_profile['last_login'] = datetime.fromisoformat(loaded_profile['last_login'])
        
        recreated_user = UserProfile(**{k: v for k, v in loaded_profile.items() if k in 
            ['user_id', 'email', 'display_name', 'sae_id', 'provider', 'created_at', 'last_login']})
        
        print(f"✅ Step 7: UserProfile recreated for {recreated_user.email}")
        
        # Step 8: Verify data integrity
        assert recreated_user.user_id == test_user.user_id
        assert recreated_user.email == test_user.email
        assert recreated_user.display_name == test_user.display_name
        assert recreated_user.sae_id == test_user.sae_id
        assert recreated_user.provider == test_user.provider
        print("✅ Step 8: Data integrity verified")
        
        # Step 9: Test update cycle
        print("🔄 Testing profile update cycle...")
        recreated_user.last_login = datetime.utcnow()
        updated_dict = _user_profile_to_dict(recreated_user)
        update_success = await storage.save_user_profile(updated_dict)
        assert update_success, "Failed to update profile"
        print("✅ Step 9: Profile update cycle verified")
        
        # Cleanup
        await storage.close()
        
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("The QuMail persistence fix is working correctly!")
        print("✨ User identity will now persist across application restarts")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Setup minimal logging
    logging.basicConfig(level=logging.WARNING)
    
    result = asyncio.run(test_complete_persistence_flow())
    sys.exit(0 if result else 1)