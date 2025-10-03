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
}

// Export singleton instance
const quantumService = new QuantumService();
export default quantumService;
