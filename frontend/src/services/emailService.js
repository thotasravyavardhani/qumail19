// Email Service for QuMail Web
// Handles quantum-encrypted email sending and receiving

import authService from './authService';
const API_URL = process.env.NODE_ENV === 'development' ? '' : process.env.REACT_APP_BACKEND_URL;

class EmailService {
  constructor() {
    this.baseURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  }
  async loadEmails(folder) {
        try {
            const response = await fetch(`${API_URL}/api/emails/${folder}`, {
                method: 'GET',
                headers: authService.getAuthHeaders() // IMPORTANT: Uses the stored token
            });

            if (!response.ok) {
                // Throwing an error here is what causes the "Failed to load emails" toast
                const errorData = await response.json();
                throw new Error(errorData.detail || `Server error loading ${folder}`);
            }

            return response.json();
        } catch (error) {
            console.error(`Error loading emails from ${folder}:`, error);
            throw error;
        }
    }
    
  // Send quantum-encrypted email
  async sendQuantumEmail(emailData) {
    try {
      const response = await fetch(`${this.baseURL}/api/messages/send`, {
        method: 'POST',
        headers: authService.getAuthHeaders(),
        body: JSON.stringify({
          to_address: emailData.to,
          subject: emailData.subject,
          body: emailData.body,
          security_level: emailData.securityLevel,
          attachments: emailData.attachments || []
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to send email');
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Send email error:', error);
      throw error;
    }
  }

  // Get inbox emails
  async getInbox(folder = 'Inbox', limit = 50) {
    try {
      const response = await fetch(
        `${this.baseURL}/api/messages/inbox?folder=${encodeURIComponent(folder)}&limit=${limit}`,
        {
          headers: authService.getAuthHeaders()
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch emails');
      }

      const result = await response.json();
      return result.emails || [];
    } catch (error) {
      console.error('Get inbox error:', error);
      throw error;
    }
  }

  // Get email details (decrypt)
  async getEmailDetails(emailId) {
    try {
      const response = await fetch(`${this.baseURL}/api/messages/${encodeURIComponent(emailId)}`, {
        headers: authService.getAuthHeaders()
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to decrypt email');
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Get email details error:', error);
      throw error;
    }
  }

  // Validate email addresses
  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Get demo email templates
  getDemoTemplates() {
    return [
      {
        id: 'quantum-test',
        name: 'Quantum Security Test',
        subject: 'Quantum Encrypted Message - Security Test',
        body: `This is a demonstration of quantum-secure email encryption using QuMail.

The message content is protected using:
- Quantum Key Distribution (QKD) from the Key Management Entity (KME)
- Post-Quantum Cryptography algorithms (CRYSTALS-Kyber)
- AES-256-GCM with quantum-derived keys

This email was sent via real SMTP but can only be decrypted using QuMail with the corresponding quantum keys.

Best regards,
QuMail Quantum Communications Team`,
        securityLevel: 'L2',
        category: 'demo'
      },
      {
        id: 'pqc-demo',
        name: 'Post-Quantum Demo',
        subject: '[PQC Protected] Future-Proof Communication',
        body: `Dear Quantum Communications Colleague,

This message demonstrates Post-Quantum Cryptography (PQC) protection against future quantum computer threats.

Technical Details:
- Encryption: CRYSTALS-Kyber KEM + AES-256-GCM
- Key Length: 512-bit quantum seed
- Quantum Resistance: Shor's and Grover's algorithms
- NIST Compliance: Level 5 equivalent security

The content remains secure even against quantum computing advances.

Regards,
ISRO Quantum Communications Research`,
        securityLevel: 'L3',
        category: 'technical'
      },
      {
        id: 'hackathon-demo',
        name: 'Hackathon Demonstration',
        subject: 'Smart India Hackathon - Quantum Email Demo',
        body: `Greetings from the Smart India Hackathon!

This email showcases our quantum-secure communication system built for ISRO-grade applications.

Key Features Demonstrated:
✅ Real-time KME integration with quantum key distribution
✅ Multi-level security (L1 OTP, L2 Q-AES, L3 PQC, L4 TLS)
✅ WebSocket-based real-time messaging
✅ PQC file encryption with Kyber KEM protection
✅ Production-ready OAuth2 integration

The email you're reading traveled through Gmail's servers but remained quantum-encrypted throughout the journey.

Team QuMail
Smart India Hackathon 2024`,
        securityLevel: 'L2',
        category: 'hackathon'
      }
    ];
  }

  // Get suggested recipients for demo
  getDemoRecipients() {
    return [
      {
        email: 'alice@qumail.com',
        name: 'Alice Smith',
        description: 'Demo user - internal QuMail network'
      },
      {
        email: 'bob@qumail.com',
        name: 'Bob Johnson',
        description: 'Demo user - internal QuMail network'
      },
      {
        email: 'demo@qumail.com',
        name: 'Demo Account',
        description: 'Demo user - internal QuMail network'
      }
    ];
  }

  // Get real email suggestions for external demo
  getRealEmailSuggestions() {
    return [
      {
        provider: 'Gmail',
        example: 'your.email@gmail.com',
        description: 'Send to your real Gmail account to see external delivery'
      },
      {
        provider: 'Yahoo',
        example: 'your.email@yahoo.com', 
        description: 'Send to Yahoo Mail to test cross-provider delivery'
      },
      {
        provider: 'Outlook',
        example: 'your.email@outlook.com',
        description: 'Send to Outlook/Hotmail for Microsoft integration test'
      }
    ];
  }

  // Format email for display
  formatEmail(email) {
    return {
      id: email.email_id,
      sender: email.sender,
      subject: email.subject,
      preview: email.preview || '',
      receivedAt: new Date(email.received_at),
      securityLevel: email.security_level,
      folder: email.folder,
      isEncrypted: email.security_level !== 'L4',
      isQuantum: ['L1', 'L2', 'L3'].includes(email.security_level),
      isPQC: email.security_level === 'L3'
    };
  }

  // Get security level info for emails
  getEmailSecurityInfo(level) {
    const securityMap = {
      'L1': {
        name: 'Quantum OTP',
        icon: '🔐',
        color: '#00BCD4',
        description: 'Perfect secrecy encryption'
      },
      'L2': {
        name: 'Quantum AES',
        icon: '🛡️', 
        color: '#2196F3',
        description: 'Quantum-aided AES-256-GCM'
      },
      'L3': {
        name: 'Post-Quantum',
        icon: '🔮',
        color: '#4CAF50',
        description: 'Kyber KEM + quantum resistance'
      },
      'L4': {
        name: 'Standard TLS',
        icon: '🔒',
        color: '#9E9E9E',
        description: 'Traditional TLS encryption'
      }
    };

    return securityMap[level] || securityMap['L4'];
  }

  // Estimate encryption time (for demo purposes)
  estimateEncryptionTime(securityLevel, messageLength) {
    const baseTimes = {
      'L1': 0.5, // OTP is fast but limited
      'L2': 0.8, // Quantum-aided AES
      'L3': 1.2, // PQC has overhead
      'L4': 0.3  // Just TLS
    };

    const baseTime = baseTimes[securityLevel] || 1;
    const lengthFactor = Math.log(messageLength / 1000 + 1); // Logarithmic scaling
    
    return Math.max(0.5, baseTime + lengthFactor * 0.2);
  }
}

// Export singleton instance
const emailService = new EmailService();
export default emailService;
