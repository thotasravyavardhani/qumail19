#!/usr/bin/env python3
"""
Test script to verify KME client recursion fix and PQC features
"""

import asyncio
import logging
import sys
import os

# Add the app directory to the path
sys.path.insert(0, '/app')

from crypto.kme_client import KMEClient
from crypto.cipher_strategies import CipherManager, PostQuantumStrategy
from core.app_core import QuMailCore

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_kme_recursion_fix():
    """Test that KME client no longer has recursion issues"""
    print("=== Testing KME Client Recursion Fix ===")
    
    try:
        # Create KME client
        kme_client = KMEClient("http://127.0.0.1:8080")
        
        # Test initialization without recursion
        print("1. Testing KME initialization...")
        await kme_client.initialize(enable_heartbeat=False)  # Disable heartbeat for test
        
        print(f"   - KME connected: {kme_client.is_connected}")
        print(f"   - Connection failures: {kme_client.connection_failures}")
        
        # Test status request (this would previously cause recursion)
        print("2. Testing status request...")
        status = await kme_client.get_status()
        print(f"   - Status response: {status}")
        
        # Test multiple requests to ensure no recursion
        print("3. Testing multiple requests...")
        for i in range(3):
            result = await kme_client.get_status()
            print(f"   - Request {i+1}: {result is not None}")
        
        # Test heartbeat functionality
        print("4. Testing heartbeat monitoring...")
        await kme_client._start_heartbeat()
        
        # Wait a bit for heartbeat
        await asyncio.sleep(2)
        
        print(f"   - Heartbeat enabled: {kme_client.heartbeat_enabled}")
        
        # Stop heartbeat
        await kme_client.stop_heartbeat()
        
        # Cleanup
        await kme_client.close()
        
        print("✅ KME recursion fix test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ KME recursion fix test FAILED: {e}")
        return False

async def test_pqc_file_encryption():
    """Test PQC file encryption features"""
    print("\\n=== Testing PQC File Encryption ===")
    
    try:
        # Create cipher manager
        cipher_manager = CipherManager()
        pqc_strategy = cipher_manager.strategies['L3']
        
        # Test small file (standard PQC)
        print("1. Testing standard PQC encryption...")
        small_data = b"This is a test message for PQC encryption"
        quantum_key = os.urandom(64)  # 512 bits for Kyber
        
        encrypted_small = pqc_strategy.encrypt(small_data, quantum_key)
        print(f"   - Algorithm: {encrypted_small['algorithm']}")
        print(f"   - FEK used: {encrypted_small.get('fek_used', False)}")
        
        decrypted_small = pqc_strategy.decrypt(encrypted_small, quantum_key)
        assert decrypted_small == small_data
        print("   ✅ Standard PQC encryption/decryption works")
        
        # Test large file (with FEK)
        print("2. Testing PQC file encryption with FEK...")
        
        # Simulate 20MB file
        large_data = os.urandom(20 * 1024 * 1024)  # 20MB of random data
        file_context = {
            'is_attachment': True,
            'total_size': len(large_data),
            'attachment_count': 1
        }
        
        encrypted_large = pqc_strategy.encrypt(large_data, quantum_key, file_context)
        print(f"   - Algorithm: {encrypted_large['algorithm']}")
        print(f"   - Encryption mode: {encrypted_large['encryption_mode']}")  
        print(f"   - FEK used: {encrypted_large.get('fek_used', False)}")
        print(f"   - File size: {encrypted_large['file_size_mb']:.2f} MB")
        print(f"   - PQC algorithm: {encrypted_large['pqc_algorithm']}")
        
        # Test decryption
        decrypted_large = pqc_strategy.decrypt(encrypted_large, quantum_key)
        assert decrypted_large == large_data
        print("   ✅ PQC file encryption with FEK works")
        
        # Test Kyber encapsulation details
        if encrypted_large.get('encapsulated_fek'):
            encap_data = encrypted_large['encapsulated_fek']
            print(f"   - KEM implementation: {encap_data.get('implementation', 'unknown')}")
            print(f"   - Security strength: {encap_data.get('security_strength', 'unknown')}")
        
        print("✅ PQC file encryption test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ PQC file encryption test FAILED: {e}")
        return False

async def test_core_integration():
    """Test core application integration"""
    print("\\n=== Testing Core Integration ===")
    
    try:
        # Create core with mock config
        config = {
            'kme_url': 'http://127.0.0.1:8080',
            'storage_path': '/tmp/qumail_test'
        }
        
        core = QuMailCore(config)
        
        # Test initialization
        print("1. Testing core initialization...")
        await core.initialize()
        
        print(f"   - QKD status: {core.qkd_status}")
        print(f"   - Current security level: {core.current_security_level}")
        
        # Test QKD status
        print("2. Testing QKD status...")
        qkd_status = core.get_qkd_status()
        print(f"   - Status: {qkd_status['status']}")
        print(f"   - KME connected: {qkd_status['kme_connected']}")
        print(f"   - Available levels: {qkd_status['available_levels']}")
        print(f"   - Heartbeat enabled: {qkd_status.get('heartbeat_enabled', False)}")
        
        # Test PQC statistics
        print("3. Testing PQC statistics...")
        pqc_stats = core.get_pqc_statistics()
        print(f"   - Files encrypted: {pqc_stats['files_encrypted']}")
        print(f"   - Total size MB: {pqc_stats['total_size_mb']}")
        print(f"   - FEK operations: {pqc_stats['fek_operations']}")
        
        # Test security level change
        print("4. Testing security level changes...")
        core.set_security_level('L3')
        assert core.get_security_level() == 'L3'
        print("   - Security level changed to L3")
        
        # Cleanup
        await core.cleanup()
        
        print("✅ Core integration test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Core integration test FAILED: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 QuMail KME Fix and PQC Feature Test Suite")
    print("=" * 50)
    
    tests = [
        test_kme_recursion_fix,
        test_pqc_file_encryption,
        test_core_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests PASSED! KME recursion fix and PQC features are working correctly.")
    else:
        print(f"⚠️  {total - passed} test(s) FAILED. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"💥 Test suite crashed: {e}")
        sys.exit(1)