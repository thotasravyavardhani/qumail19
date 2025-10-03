#!/usr/bin/env python3
"""
Test script to identify HMAC backend issue
"""
import sys
import os
sys.path.append('/app')

try:
    # Test the cipher strategies
    from crypto.cipher_strategies import CipherManager, PostQuantumStrategy
    import secrets
    
    print("Testing PQC strategy...")
    pqc_strategy = PostQuantumStrategy()
    
    # Test with small data first
    small_data = b"Small test data"
    small_key = secrets.token_bytes(64)  # 512 bits for PQC
    
    print("Encrypting small data...")
    encrypted_small = pqc_strategy.encrypt(small_data, small_key)
    print(f"Small data encryption successful: {encrypted_small.get('algorithm')}")
    
    # Test with large data (will trigger FEK path)
    large_data = b"Large test data " * 100000  # About 1.5MB
    large_key = secrets.token_bytes(64)
    
    print("Encrypting large data (FEK path)...")
    encrypted_large = pqc_strategy.encrypt(large_data, large_key)
    print(f"Large data encryption successful: {encrypted_large.get('algorithm')}")
    
    print("All PQC tests passed!")
    
except Exception as e:
    print(f"Error during PQC testing: {e}")
    import traceback
    traceback.print_exc()