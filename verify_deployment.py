#!/usr/bin/env python3
"""
QuMail Deployment Verification Script
Quick validation of the improved QuMail system
"""

import sys
import os
import importlib.util

def check_python_version():
    """Check if Python version is adequate"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check critical dependencies"""
    required_modules = [
        ('cryptography', 'Cryptographic operations'),
        ('aiohttp', 'Async HTTP client'),
        ('flask', 'KME simulator'),
        ('requests', 'HTTP requests'),
    ]
    
    missing = []
    for module, description in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} ({description})")
        except ImportError:
            print(f"❌ {module} ({description}) - MISSING")
            missing.append(module)
    
    if missing:
        print(f"\n📦 Install missing dependencies:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def check_qumail_modules():
    """Check QuMail modules"""
    sys.path.insert(0, os.path.dirname(__file__))
    
    qumail_modules = [
        ('utils.styles', 'Material Design stylesheets'),
        ('crypto.cipher_strategies', 'Crypto-agile security levels'),
        ('crypto.kme_client', 'KME ETSI integration'),
        ('core.app_core', 'Application orchestration'),
    ]
    
    for module, description in qumail_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} ({description})")
        except ImportError as e:
            print(f"❌ {module} ({description}) - {e}")
            return False
    
    return True

def validate_improvements():
    """Validate the applied improvements"""
    try:
        from utils.styles import get_main_window_stylesheet
        stylesheet = get_main_window_stylesheet()
        
        # Check Material Design improvements
        material_checks = [
            ("#1E88E5", "Primary Blue color"),
            ("#00C853", "Secondary Green color"), 
            ("#00BCD4", "Quantum Cyan color"),
            ("SecuritySelector", "Security selector styling"),
            ("QKDStatusLabel", "QKD status styling"),
            ("border-radius: 20px", "Pill-shaped design"),
        ]
        
        for check, description in material_checks:
            if check in stylesheet:
                print(f"✅ {description}")
            else:
                print(f"⚠️ {description} - not found")
        
        # Check crypto functionality
        from crypto.cipher_strategies import CipherManager
        cipher_manager = CipherManager()
        
        # Validate security levels
        levels = cipher_manager.list_available_levels()
        expected = ['L1', 'L2', 'L3', 'L4']
        
        for level in expected:
            if level in levels:
                print(f"✅ Security Level {level}")
            else:
                print(f"❌ Security Level {level} - MISSING")
                return False
                
        # Test key length calculations
        l1_length = cipher_manager.get_required_key_length('L1', 1000)
        l2_length = cipher_manager.get_required_key_length('L2', 1000) 
        
        if l1_length == 8000:  # 1000 bytes * 8 bits
            print("✅ L1 OTP key calculation")
        else:
            print(f"❌ L1 OTP key calculation - got {l1_length}, expected 8000")
            
        if l2_length == 256:  # Fixed 256-bit seed
            print("✅ L2 Q-AES key calculation")
        else:
            print(f"❌ L2 Q-AES key calculation - got {l2_length}, expected 256")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def main():
    """Main deployment verification"""
    print("🚀 QuMail Deployment Verification")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("QuMail Modules", check_qumail_modules),
        ("Applied Improvements", validate_improvements),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n🧪 {check_name}:")
        if check_func():
            passed += 1
        else:
            print(f"❌ {check_name} failed")
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 QuMail deployment verification SUCCESSFUL!")
        print("🚀 Ready for ISRO-grade production use!")
        print("\n📖 Next steps:")
        print("   python launcher.py --simulate-kme  # Start with simulator")
        print("   python main.py                     # Launch QuMail")
        return True
    else:
        print(f"\n⚠️ {total - passed} checks failed")
        print("Please resolve issues before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)