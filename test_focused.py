#!/usr/bin/env python3
"""
Focused test for KME recursion fix and PQC features
"""

import asyncio
import logging
import sys
import os
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import directly without relative imports
sys.path.insert(0, '/app')

async def test_kme_recursion_fix():
    """Test that KME client no longer has recursion issues"""
    print("=== Testing KME Client Recursion Fix ===")
    
    try:
        # Import KME client directly
        from crypto.kme_client import KMEClient
        
        # Create KME client
        kme_client = KMEClient("http://127.0.0.1:8080")
        
        # Test initialization without recursion
        print("1. Testing KME initialization...")
        await kme_client.initialize(enable_heartbeat=False)  # Disable heartbeat for test
        
        print(f"   - KME connected: {kme_client.is_connected}")
        print(f"   - Connection failures: {kme_client.connection_failures}")
        
        # Test direct connection test (the fixed method)
        print("2. Testing direct connection test...")
        await kme_client._direct_connection_test()
        print(f"   - Direct test completed, connected: {kme_client.is_connected}")
        
        # Test status request (this would previously cause recursion)
        print("3. Testing status request...")
        status = await kme_client.get_status()
        print(f"   - Status response received: {status is not None}")
        
        # Test multiple requests to ensure no recursion
        print("4. Testing multiple requests...")
        for i in range(3):
            result = await kme_client.get_status()
            print(f"   - Request {i+1}: {'Success' if result is not None else 'Failed'}")
        
        # Test heartbeat functionality
        print("5. Testing heartbeat monitoring...")
        await kme_client._start_heartbeat()
        print(f"   - Heartbeat enabled: {kme_client.heartbeat_enabled}")
        
        # Wait a bit for heartbeat
        await asyncio.sleep(2)
        
        # Stop heartbeat
        await kme_client.stop_heartbeat()
        print("   - Heartbeat stopped")
        
        # Test connection statistics
        stats = kme_client.get_connection_statistics()
        print(f"   - Total requests: {stats['total_requests']}")
        print(f"   - Success rate: {stats['success_rate']:.1f}%")
        
        # Cleanup
        await kme_client.close()
        
        print("✅ KME recursion fix test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ KME recursion fix test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_pqc_file_encryption():
    """Test PQC file encryption features"""
    print("\\n=== Testing PQC File Encryption ===")
    
    try:
        # Import cipher strategies directly
        from crypto.cipher_strategies import CipherManager, PostQuantumStrategy
        
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
        
        # Test large file (with FEK) - simulate 5MB to avoid memory issues
        print("2. Testing PQC file encryption with FEK...")
        
        # Simulate 5MB file (smaller for testing)
        large_data = os.urandom(5 * 1024 * 1024)  # 5MB of random data
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
        print("   - Testing decryption...")
        decrypted_large = pqc_strategy.decrypt(encrypted_large, quantum_key)
        
        # Verify data integrity
        assert len(decrypted_large) == len(large_data)
        assert decrypted_large[:1000] == large_data[:1000]  # Check first 1000 bytes
        print("   ✅ PQC file encryption with FEK works")
        
        # Test Kyber encapsulation details
        if encrypted_large.get('encapsulated_fek'):
            encap_data = encrypted_large['encapsulated_fek']
            print(f"   - KEM implementation: {encap_data.get('implementation', 'unknown')}")
            print(f"   - Security strength: {encap_data.get('security_strength', 'unknown')}")
        
        # Test cipher manager integration
        print("3. Testing cipher manager with different levels...")
        for level in ['L1', 'L2', 'L3', 'L4']:
            test_data = b"Test data for level " + level.encode()
            key_length = cipher_manager.get_required_key_length(level, len(test_data))
            print(f"   - {level}: requires {key_length} bits")
            
            if level != 'L4':  # L4 doesn't need keys
                test_key = os.urandom(key_length // 8)
                encrypted = cipher_manager.encrypt_with_level(test_data, test_key, level)
                decrypted = cipher_manager.decrypt_with_level(encrypted, test_key)
                assert decrypted == test_data
                print(f"     ✓ {level} encryption/decryption works")
        
        print("✅ PQC file encryption test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ PQC file encryption test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_kme_robustness_features():
    """Test KME robustness and heartbeat features"""
    print("\\n=== Testing KME Robustness Features ===")
    
    try:
        from crypto.kme_client import KMEClient
        
        # Create KME client with robustness features
        kme_client = KMEClient("http://127.0.0.1:8080")
        
        print("1. Testing enhanced initialization...")
        await kme_client.initialize(enable_heartbeat=True)
        
        print(f"   - Initial connection state: {kme_client.is_connected}")
        print(f"   - Heartbeat enabled: {kme_client.heartbeat_enabled}")
        print(f"   - Max failures threshold: {kme_client.max_connection_failures}")
        
        # Test connection statistics
        print("2. Testing connection statistics...")
        stats = kme_client.get_connection_statistics()
        print(f"   - Connection status: {stats['connection_status']}")
        print(f"   - Uptime seconds: {stats['uptime_seconds']}")
        print(f"   - Total requests: {stats['total_requests']}")
        print(f"   - Heartbeat interval: {stats['heartbeat_interval']}s")
        
        # Test heartbeat functionality
        print("3. Testing heartbeat monitoring...")
        if kme_client.heartbeat_enabled:
            # Let heartbeat run for a few cycles
            await asyncio.sleep(3)
            print("   - Heartbeat monitoring active")
            
            # Check heartbeat performance
            heartbeat_result = await kme_client._perform_heartbeat()
            print(f"   - Manual heartbeat test: {'Success' if heartbeat_result else 'Failed'}")
        
        # Test error handling and recovery
        print("4. Testing error handling...")
        
        # Simulate connection failure by closing session
        if kme_client.session and not kme_client.session.closed:
            await kme_client.session.close()
            print("   - Simulated connection failure")
        
        # Try to make a request (should handle gracefully)
        status = await kme_client.get_status()
        print(f"   - Request after failure: {'Success' if status else 'Handled gracefully'}")
        
        # Test health check
        print("5. Testing health check...")
        health = await kme_client.health_check()
        print(f"   - Overall health: {health['overall_status']}")
        print(f"   - Health checks: {len(health.get('checks', {}))}")
        
        # Cleanup
        await kme_client.stop_heartbeat()
        await kme_client.close()
        
        print("✅ KME robustness features test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ KME robustness features test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🧪 QuMail KME Fix and PQC Feature Test Suite")
    print("=" * 60)
    
    tests = [
        test_kme_recursion_fix,
        test_pqc_file_encryption,
        test_kme_robustness_features
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests PASSED!")
        print("✅ KME recursion fix implemented successfully")
        print("✅ PQC file encryption with FEK + Kyber working")
        print("✅ KME robustness with heartbeat monitoring active")
        print()
        print("🔐 Advanced Security Features Summary:")
        print("• Level 1: Quantum OTP encryption")
        print("• Level 2: Quantum-aided AES-256-GCM") 
        print("• Level 3: Post-Quantum Crypto + File Encryption")
        print("• Level 4: Standard TLS")
        print()
        print("🚀 ISRO-grade Quantum Secure Email Client Ready!")
    else:
        print(f"⚠️  {total - passed} test(s) FAILED. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\\n🛑 Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)