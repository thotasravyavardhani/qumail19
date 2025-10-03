// Quantum Service for QuMail Web
// Handles quantum status, security levels, and KME communication

import authService from './authService';

class QuantumService {
  constructor() {
    this.baseURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  }

  // Get current quantum/KME status
  async getQuantumStatus() {
    try {
      const response = await fetch(`${this.baseURL}/api/quantum/status`, {
        headers: authService.getAuthHeaders()
      });

      if (!response.ok) {
        throw new Error('Failed to fetch quantum status');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Quantum status fetch error:', error);
      throw error;
    }
  }

  // Set security level (L1/L2/L3/L4)
  async setSecurityLevel(level) {
    try {
      const response = await fetch(`${this.baseURL}/api/quantum/security-level`, {
        method: 'POST',
        headers: {
          ...authService.getAuthHeaders(),
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `level=${encodeURIComponent(level)}`
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to set security level');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Security level change error:', error);
      throw error;
    }
  }

  // Get security level descriptions
  getSecurityLevelInfo() {
    return {
      L1: {
        name: 'Quantum OTP',
        description: 'One-Time Pad with perfect secrecy',
        color: 'var(--quantum-cyan)',
        icon: '🔐',
        maxSize: '50KB',
        keyConsumption: 'Equal to data size'
      },
      L2: {
        name: 'Quantum-aided AES',
        description: 'AES-256-GCM with quantum seed',
        color: 'var(--primary-blue)',
        icon: '🛡️',
        maxSize: 'Unlimited',
        keyConsumption: '256 bits'
      },
      L3: {
        name: 'Post-Quantum Crypto',
        description: 'Kyber KEM + File encryption',
        color: 'var(--secondary-green)',
        icon: '🔮',
        maxSize: 'Unlimited',
        keyConsumption: '512 bits + FEK'
      },
      L4: {
        name: 'Standard TLS',
        description: 'Traditional TLS encryption only',
        color: 'var(--text-secondary)',
        icon: '🔒',
        maxSize: 'Unlimited',
        keyConsumption: 'None'
      }
    };
  }

  // Format quantum status for display
  formatQuantumStatus(status) {
    const statusMap = {
      'connected': {
        label: 'QKD Active',
        icon: 'Ψ',
        color: 'var(--success-green)',
        pulse: true
      },
      'degraded': {
        label: 'QKD Degraded',
        icon: '⚠️',
        color: 'var(--warning-orange)',
        pulse: true
      },
      'error': {
        label: 'QKD Error',
        icon: '❌',
        color: 'var(--error-red)',
        pulse: false
      },
      'initializing': {
        label: 'Initializing...',
        icon: '⏳',
        color: 'var(--text-hint)',
        pulse: false
      },
      'disconnected': {
        label: 'Disconnected',
        icon: '🔴',
        color: 'var(--error-red)',
        pulse: false
      }
    };

    return statusMap[status] || statusMap['disconnected'];
  }

  // Format success rate
  formatSuccessRate(rate) {
    if (rate >= 95) return { level: 'high', color: 'var(--success-green)' };
    if (rate >= 80) return { level: 'medium', color: 'var(--warning-orange)' };
    return { level: 'low', color: 'var(--error-red)' };
  }

  // Format uptime
  formatUptime(seconds) {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
    return `${Math.floor(seconds / 86400)}d`;
  }
  // ============================================================================
  // PQC Hybrid Call Endpoints - Phase I + III Implementation
  // ============================================================================

  // Initiate hybrid PQC call
  async initiateHybridCall(contactId, callType = 'audio') {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/calls/initiate`, {
        method: 'POST',
        headers: {
          ...authService.getAuthHeaders(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contact_id: contactId,
          call_type: callType
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to initiate hybrid call');
      }

      const data = await response.json();
      console.log('✅ Hybrid PQC call initiated:', data);
      return data;
    } catch (error) {
      console.error('❌ Hybrid call initiation error:', error);
      throw error;
    }
  }

  // Send hybrid public keys (Responder - Step 3)
  async sendHybridPublicKeys(callId, hybridKeys) {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/calls/${callId}/public_key`, {
        method: 'PUT',
        headers: {
          ...authService.getAuthHeaders(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          pqc_pub_key: hybridKeys.kyber_public_key,
          classic_pub_key: hybridKeys.x25519_public_key,
          signature: hybridKeys.signature || 'placeholder_signature'
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to send hybrid public keys');
      }

      const data = await response.json();
      console.log('✅ Hybrid public keys sent:', data);
      return data;
    } catch (error) {
      console.error('❌ Public key transmission error:', error);
      throw error;
    }
  }

  // Send hybrid ciphertext (Initiator - Step 5)
  async sendHybridCiphertext(callId, encapsulatedData) {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/calls/${callId}/ciphertext`, {
        method: 'PUT',
        headers: {
          ...authService.getAuthHeaders(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          pqc_ciphertext: encapsulatedData.kyber_ciphertext,
          classic_key_share: encapsulatedData.x25519_public_key,
          signature: encapsulatedData.signature || 'placeholder_signature'
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to send hybrid ciphertext');
      }

      const data = await response.json();
      console.log('✅ Hybrid ciphertext sent:', data);
      return data;
    } catch (error) {
      console.error('❌ Ciphertext transmission error:', error);
      throw error;
    }
  }

  // End quantum call
  async endQuantumCall(callId) {
    try {
      const response = await fetch(`${this.baseURL}/api/calls/${callId}/end`, {
        method: 'POST',
        headers: authService.getAuthHeaders()
      });

      if (!response.ok) {
        throw new Error('Failed to end quantum call');
      }

      const data = await response.json();
      console.log('✅ Quantum call ended:', data);
      return data;
    } catch (error) {
      console.error('❌ Call end error:', error);
      throw error;
    }
  }

  // ============================================================================
  // Frontend PQC Crypto Simulation - JavaScript Implementation
  // ============================================================================

  // Generate hybrid key pair (Kyber + X25519 simulation)
  generateHybridKeyPair() {
    try {
      // Generate X25519-like key pair (simulation using crypto.subtle)
      const x25519KeyData = this._generateX25519KeyPair();
      
      // Generate Kyber-768-like key pair (deterministic simulation)
      const kyberKeyData = this._generateKyberKeyPair();
      
      const hybridKeyPair = {
        keypair_id: this._generateId('hybrid'),
        generated_at: new Date().toISOString(),
        
        // Classical Component
        x25519_public_key: x25519KeyData.publicKey,
        x25519_private_key: x25519KeyData.privateKey,
        
        // PQC Component  
        kyber_public_key: kyberKeyData.publicKey,
        kyber_secret_key: kyberKeyData.secretKey,
        
        // Metadata
        algorithm: 'Kyber-768+X25519-JS-Simulation',
        security_level: 'NIST-Level-3-Hybrid'
      };
      
      console.log('✅ Generated hybrid keypair:', hybridKeyPair.keypair_id);
      return hybridKeyPair;
    } catch (error) {
      console.error('❌ Hybrid keypair generation failed:', error);
      throw new Error(`Key generation failed: ${error.message}`);
    }
  }

  // Encapsulate hybrid key (Initiator side)
  encapsulateHybridKey(remoteHybridPublicKey) {
    try {
      // Extract remote public keys
      const remoteX25519Public = remoteHybridPublicKey.x25519_public_key;
      const remoteKyberPublic = remoteHybridPublicKey.kyber_public_key;
      
      // Generate our ephemeral keys for this exchange
      const ourX25519Keys = this._generateX25519KeyPair();
      
      // Perform X25519 ECDH (simulation)
      const x25519SharedSecret = this._performX25519ECDH(ourX25519Keys.privateKey, remoteX25519Public);
      
      // Perform Kyber encapsulation (simulation)
      const kyberResult = this._kyberEncapsulate(remoteKyberPublic);
      
      // Derive final session key using HKDF simulation
      const finalSessionKey = this._deriveHybridSessionKey(kyberResult.sharedSecret, x25519SharedSecret);
      
      const encapsulationResult = {
        encapsulation_id: this._generateId('encap'),
        timestamp: new Date().toISOString(),
        
        // Classical Component
        x25519_public_key: ourX25519Keys.publicKey,
        
        // PQC Component
        kyber_ciphertext: kyberResult.ciphertext,
        kyber_auth_tag: kyberResult.authTag,
        
        // Final derived session key (for testing/simulation)
        session_key: finalSessionKey,
        
        // Metadata
        algorithm: 'Kyber-768+X25519-HKDF-JS',
        security_level: 'NIST-Level-3-Hybrid'
      };
      
      console.log('✅ Hybrid encapsulation completed:', encapsulationResult.encapsulation_id);
      return encapsulationResult;
    } catch (error) {
      console.error('❌ Hybrid encapsulation failed:', error);
      throw new Error(`Key encapsulation failed: ${error.message}`);
    }
  }

  // Decapsulate hybrid key (Responder side)
  decapsulateHybridKey(encapsulatedData, ourHybridKeyPair) {
    try {
      // Extract our private keys
      const ourX25519Private = ourHybridKeyPair.x25519_private_key;
      const ourKyberSecret = ourHybridKeyPair.kyber_secret_key;
      
      // Extract remote data
      const remoteX25519Public = encapsulatedData.x25519_public_key;
      const kyberCiphertext = encapsulatedData.kyber_ciphertext;
      const kyberAuthTag = encapsulatedData.kyber_auth_tag;
      
      // Perform X25519 ECDH (simulation)
      const x25519SharedSecret = this._performX25519ECDH(ourX25519Private, remoteX25519Public);
      
      // Perform Kyber decapsulation (simulation)
      const kyberSharedSecret = this._kyberDecapsulate(kyberCiphertext, kyberAuthTag, ourKyberSecret);
      
      // Derive final session key (same HKDF as encapsulation)
      const finalSessionKey = this._deriveHybridSessionKey(kyberSharedSecret, x25519SharedSecret);
      
      console.log('✅ Hybrid decapsulation completed successfully');
      return finalSessionKey;
    } catch (error) {
      console.error('❌ Hybrid decapsulation failed:', error);
      throw new Error(`Key decapsulation failed: ${error.message}`);
    }
  }

  // ============================================================================
  // Private Helper Functions - Cryptographic Simulations
  // ============================================================================

  _generateX25519KeyPair() {
    // Simulate X25519 key generation using random data
    const privateKey = this._generateRandomBase64(32); // 32 bytes private key
    const publicKey = this._generateRandomBase64(32);  // 32 bytes public key
    return { privateKey, publicKey };
  }

  _generateKyberKeyPair() {
    // Simulate Kyber-768 key generation with deterministic relationship
    const secretKey = this._generateRandomBase64(2400); // Kyber-768 secret key size
    
    // Generate deterministic public key from secret key (simulation)
    const publicKey = this._deriveKyberPublicKey(secretKey);
    
    return { 
      secretKey, 
      publicKey,
      validation: this._generateRandomBase64(32)
    };
  }

  _deriveKyberPublicKey(secretKey) {
    // Deterministic public key derivation simulation
    const hash = this._simpleHash(secretKey + 'QuMail-Kyber-PubKey-Derivation');
    return btoa(hash).substring(0, 1184); // Simulate Kyber-768 public key size
  }

  _performX25519ECDH(ourPrivate, remotePublic) {
    // Simulate ECDH shared secret computation
    const combined = ourPrivate + remotePublic;
    return this._simpleHash(combined + 'X25519-SharedSecret');
  }

  _kyberEncapsulate(remoteKyberPublic) {
    // Simulate Kyber encapsulation
    const sharedSecret = this._simpleHash(remoteKyberPublic + 'Kyber-SharedSecret-Derivation');
    const ciphertext = this._simpleHash(sharedSecret + 'Kyber-Ciphertext');
    const authTag = this._simpleHash(ciphertext + 'Kyber-AuthTag').substring(0, 32);
    
    return {
      sharedSecret,
      ciphertext: btoa(ciphertext),
      authTag: btoa(authTag)
    };
  }

  _kyberDecapsulate(ciphertext, authTag, ourKyberSecret) {
    // Simulate Kyber decapsulation by deriving the same shared secret
    // In real Kyber, this would use the secret key to derive the same shared secret
    
    // Reconstruct public key from secret key (deterministic)
    const ourPublicKey = this._deriveKyberPublicKey(ourKyberSecret);
    
    // Use same method as encapsulation to get shared secret
    const sharedSecret = this._simpleHash(ourPublicKey + 'Kyber-SharedSecret-Derivation');
    
    return sharedSecret;
  }

  _deriveHybridSessionKey(kyberSharedSecret, x25519SharedSecret) {
    // Simulate HKDF for final session key derivation
    const combinedSecrets = kyberSharedSecret + x25519SharedSecret;
    const salt = 'QuMail-Hybrid-Session-Key-v1';
    return this._simpleHash(combinedSecrets + salt);
  }

  _generateRandomBase64(byteLength) {
    const array = new Uint8Array(byteLength);
    crypto.getRandomValues(array);
    return btoa(String.fromCharCode(...array));
  }

  _generateId(prefix) {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;
  }

  _simpleHash(input) {
    // Simple hash function for simulation (not cryptographically secure)
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(16).padStart(8, '0').repeat(4); // Create longer hash
  }
}

// Export singleton instance
const quantumService = new QuantumService();
export default quantumService;


