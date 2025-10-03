// File Service for QuMail Web
// Handles PQC file encryption and large file processing

import authService from './authService';

class FileService {
  constructor() {
    this.baseURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  }

  // Encrypt file with PQC (Priority Demo Feature)
  async encryptFile(file, securityLevel = 'L3', onProgress = null) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('security_level', securityLevel);

      const response = await fetch(`${this.baseURL}/api/files/encrypt`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'File encryption failed');
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('File encryption error:', error);
      throw error;
    }
  }

  // Validate file for PQC encryption
  validateFile(file) {
    const maxSize = 500 * 1024 * 1024; // 500MB limit for demo
    const minSize = 1024; // 1KB minimum for meaningful demo

    const validation = {
      isValid: true,
      errors: [],
      warnings: [],
      recommendations: {}
    };

    // Size validation
    if (file.size > maxSize) {
      validation.isValid = false;
      validation.errors.push(`File too large: ${(file.size / (1024*1024)).toFixed(1)}MB (max: 500MB)`);
    }

    if (file.size < minSize) {
      validation.warnings.push('File is very small - PQC benefits are minimal');
    }

    // Security level recommendations
    if (file.size > 50 * 1024 * 1024) { // >50MB
      validation.recommendations.securityLevel = 'L3';
      validation.recommendations.reason = 'Large files benefit from Kyber KEM protection';
    } else if (file.size > 10 * 1024 * 1024) { // >10MB
      validation.recommendations.securityLevel = 'L2';
      validation.recommendations.reason = 'Medium files work well with Quantum-aided AES';
    } else if (file.size < 50 * 1024) { // <50KB
      validation.recommendations.securityLevel = 'L1';
      validation.recommendations.reason = 'Small files can use Quantum OTP';
    }

    // File type analysis
    const fileExtension = file.name.split('.').pop()?.toLowerCase() || '';
    const sensitiveTypes = ['pdf', 'doc', 'docx', 'txt', 'jpg', 'png', 'mp4', 'zip'];
    
    if (sensitiveTypes.includes(fileExtension)) {
      validation.recommendations.encryption = true;
      validation.recommendations.fileTypeReason = `${fileExtension.toUpperCase()} files often contain sensitive data`;
    }

    return validation;
  }

  // Get file size categories for demo
  getFileSizeCategory(size) {
    if (size < 1024) return { category: 'bytes', value: size, unit: 'B', color: '#9E9E9E' };
    if (size < 1024 * 1024) return { category: 'kb', value: size / 1024, unit: 'KB', color: '#2196F3' };
    if (size < 1024 * 1024 * 1024) return { category: 'mb', value: size / (1024 * 1024), unit: 'MB', color: '#FF9800' };
    return { category: 'gb', value: size / (1024 * 1024 * 1024), unit: 'GB', color: '#F44336' };
  }

  // Format file encryption statistics
  formatEncryptionStats(stats) {
    return {
      totalFiles: stats.files_encrypted || 0,
      totalSizeMB: stats.total_size_mb || 0,
      fekOperations: stats.fek_operations || 0,
      kyberEncapsulations: stats.kyber_encapsulations || 0,
      averageFileSizeMB: stats.average_file_size_mb || 0
    };
  }

  // Get PQC encryption info
  getPQCInfo() {
    return {
      kyberKEM: {
        name: 'CRYSTALS-Kyber-1024',
        description: 'Post-quantum key encapsulation mechanism',
        keySize: '1568 bytes public key',
        securityLevel: 'NIST Level 5 equivalent',
        resistantTo: ['Quantum computers', 'Shor\'s algorithm', 'Grover\'s algorithm']
      },
      fileEncryption: {
        name: 'File Encryption Key (FEK)',
        description: 'AES-256-GCM with quantum-protected key',
        threshold: '10MB+',
        benefit: 'Quantum-safe protection for large files'
      },
      implementation: {
        status: 'Cryptographically secure simulation',
        readiness: 'Production-ready architecture',
        compliance: 'NIST Post-Quantum standards'
      }
    };
  }

  // Generate demo files for testing
  generateDemoFiles() {
    return [
      {
        name: 'small-document.pdf',
        size: 45 * 1024, // 45KB
        type: 'application/pdf',
        description: 'Small PDF - ideal for L1 Quantum OTP',
        isDemoFile: true
      },
      {
        name: 'medium-presentation.pptx',
        size: 8.5 * 1024 * 1024, // 8.5MB
        type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        description: 'Medium file - L2 Quantum-aided AES recommended',
        isDemoFile: true
      },
      {
        name: 'large-video.mp4',
        size: 85 * 1024 * 1024, // 85MB
        type: 'video/mp4',
        description: 'Large file - L3 PQC with Kyber KEM protection',
        isDemoFile: true
      }
    ];
  }

  // Create mock file for demo
  createMockFile(demoFileInfo) {
    // Create a Blob with the specified size filled with demo data
    const chunk = new Array(1024).fill('QuMail PQC Demo Data ').join('');
    const chunks = Math.ceil(demoFileInfo.size / chunk.length);
    const fileContent = new Array(chunks).fill(chunk).join('').substring(0, demoFileInfo.size);
    
    const blob = new Blob([fileContent], { type: demoFileInfo.type });
    
    // Create a File object
    const file = new File([blob], demoFileInfo.name, {
      type: demoFileInfo.type,
      lastModified: Date.now()
    });
    
    // Mark as demo file
    file.isDemoFile = true;
    file.description = demoFileInfo.description;
    
    return file;
  }
}

// Export singleton instance
const fileService = new FileService();
export default fileService;