#!/usr/bin/env python3
"""
Large File Generator for PQC Testing
Creates test files of various sizes to demonstrate PQC file encryption
"""

import os
import secrets
import logging
from pathlib import Path

def create_test_file(file_path: str, size_mb: float, content_type: str = "binary") -> str:
    """
    Create a test file of specified size
    
    Args:
        file_path: Path where to create the file
        size_mb: Size in megabytes
        content_type: 'binary', 'text', 'image_sim', or 'document_sim'
    
    Returns:
        Actual file path created
    """
    try:
        size_bytes = int(size_mb * 1024 * 1024)
        
        with open(file_path, 'wb') as f:
            if content_type == "text":
                # Generate text content
                text_chunk = "This is a test file for PQC (Post-Quantum Cryptography) encryption demonstration. " * 100
                text_bytes = text_chunk.encode('utf-8')
                
                written = 0
                while written < size_bytes:
                    chunk_size = min(len(text_bytes), size_bytes - written)
                    f.write(text_bytes[:chunk_size])
                    written += chunk_size
                    
            elif content_type == "image_sim":
                # Simulate image file with header + random data
                # PNG-like header simulation
                f.write(b'\x89PNG\r\n\x1a\n')
                f.write(b'IHDR' + secrets.token_bytes(16))  # Fake PNG header
                
                # Fill rest with random data
                remaining = size_bytes - 24
                while remaining > 0:
                    chunk_size = min(8192, remaining)
                    f.write(secrets.token_bytes(chunk_size))
                    remaining -= chunk_size
                    
            elif content_type == "document_sim":
                # Simulate document with structured content
                doc_content = f"""
PQC ENCRYPTED FILE SHARING TEST DOCUMENT
=========================================

File Size: {size_mb} MB
Content Type: Document Simulation
Security Level: Level 3 (Post-Quantum Cryptography)

CRYSTALS-Kyber Key Encapsulation Mechanism:
- Public Key Cryptography for quantum resistance
- Key encapsulation instead of encryption
- Optimized for large file scenarios

File Encryption Key (FEK) Process:
1. Generate 256-bit FEK for AES-256-GCM
2. Encrypt file data with FEK (high speed)
3. Encapsulate FEK with Kyber (quantum safe)
4. Transmit both encrypted file + encapsulated FEK

Security Benefits:
- Future-proof against quantum computers
- NIST-approved algorithms
- Two-layer security architecture
- Efficient for large files

""" + "PADDING CONTENT: " * 1000
                
                doc_bytes = doc_content.encode('utf-8')
                written = 0
                while written < size_bytes:
                    chunk_size = min(len(doc_bytes), size_bytes - written)
                    f.write(doc_bytes[:chunk_size])
                    written += chunk_size
                    
            else:  # binary (default)
                # Generate random binary content in chunks
                written = 0
                chunk_size = 8192  # 8KB chunks
                
                while written < size_bytes:
                    current_chunk_size = min(chunk_size, size_bytes - written)
                    f.write(secrets.token_bytes(current_chunk_size))
                    written += current_chunk_size
        
        actual_size = os.path.getsize(file_path)
        logging.info(f"Created test file: {file_path} ({actual_size / (1024*1024):.2f} MB)")
        return file_path
        
    except Exception as e:
        logging.error(f"Failed to create test file {file_path}: {e}")
        raise

def create_pqc_test_suite(base_dir: str = "/tmp/qumail_pqc_test"):
    """Create a complete test suite for PQC file encryption"""
    
    # Create test directory
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    
    test_files = []
    
    # Small file (should NOT trigger PQC)
    small_file = os.path.join(base_dir, "small_document.txt")
    create_test_file(small_file, 0.5, "text")  # 500KB
    test_files.append(("Small File (500KB)", small_file, "Should use standard L2/L3"))
    
    # Medium file (borderline)
    medium_file = os.path.join(base_dir, "medium_image.bin")
    create_test_file(medium_file, 2.5, "image_sim")  # 2.5MB
    test_files.append(("Medium File (2.5MB)", medium_file, "Should trigger FEK optimization"))
    
    # Large file (definitely PQC)
    large_file = os.path.join(base_dir, "large_document.txt")  
    create_test_file(large_file, 15.0, "document_sim")  # 15MB
    test_files.append(("Large File (15MB)", large_file, "Full PQC + FEK encryption"))
    
    # Very large file (stress test)
    xl_file = os.path.join(base_dir, "xl_data.bin")
    create_test_file(xl_file, 25.0, "binary")  # 25MB
    test_files.append(("XL File (25MB)", xl_file, "Heavy PQC processing"))
    
    # Simulated sensitive document
    sensitive_file = os.path.join(base_dir, "classified_quantum_research.pdf")
    create_test_file(sensitive_file, 8.0, "document_sim")  # 8MB
    test_files.append(("Classified Doc (8MB)", sensitive_file, "High-security PQC required"))
    
    print("\n🔐 PQC Test File Suite Created:")
    print("=" * 60)
    for name, path, description in test_files:
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"📁 {name}")
        print(f"   Path: {path}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Test: {description}")
        print()
        
    return test_files

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Creating PQC File Encryption Test Suite...")
    test_files = create_pqc_test_suite()
    
    print(f"✅ Created {len(test_files)} test files for PQC demonstration")
    print("\nTo test PQC file encryption:")
    print("1. Launch QuMail application")
    print("2. Compose new email")
    print("3. Attach any of the large files above")
    print("4. Select Level 3 (Post-Quantum Crypto)")
    print("5. Send to yourself to see full encryption cycle")
    print("\n📊 Files > 10MB will automatically suggest L3 PQC")
    print("🔒 Two-layer encryption: Kyber KEM + AES-256-GCM")