import React, { useState, useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import fileService from '../services/fileService';
import quantumService from '../services/quantumService';
import toast from 'react-hot-toast';

const PQCFileDemo = ({ user, quantumStatus, onStatsUpdate }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileValidation, setFileValidation] = useState(null);
  const [securityLevel, setSecurityLevel] = useState('L3');
  const [isEncrypting, setIsEncrypting] = useState(false);
  const [encryptionResults, setEncryptionResults] = useState([]);
  const [showKyberDetails, setShowKyberDetails] = useState(false);
  const fileInputRef = useRef(null);

  const securityLevels = quantumService.getSecurityLevelInfo();
  const pqcInfo = fileService.getPQCInfo();

  // File drop handling
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      handleFileSelection(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    maxSize: 500 * 1024 * 1024, // 500MB
    accept: {
      'application/*': [],
      'text/*': [],
      'image/*': [],
      'video/*': [],
      'audio/*': []
    }
  });

  const handleFileSelection = (file) => {
    setSelectedFile(file);
    const validation = fileService.validateFile(file);
    setFileValidation(validation);
    
    // Auto-set recommended security level
    if (validation.recommendations.securityLevel) {
      setSecurityLevel(validation.recommendations.securityLevel);
    }
    
    toast.success(`File selected: ${file.name}`);
  };

  const handleDemoFileSelect = (demoFileInfo) => {
    const mockFile = fileService.createMockFile(demoFileInfo);
    handleFileSelection(mockFile);
  };

  const handleEncryptFile = async () => {
    if (!selectedFile) {
      toast.error('Please select a file first');
      return;
    }

    setIsEncrypting(true);
    
    try {
      // Show encryption progress
      toast.loading('Encrypting with Post-Quantum Cryptography...', { id: 'encryption' });
      
      const result = await fileService.encryptFile(selectedFile, securityLevel);
      
      // Create result entry
      const encryptionResult = {
        id: Date.now(),
        fileName: selectedFile.name,
        originalSize: selectedFile.size,
        securityLevel: securityLevel,
        encryptedAt: new Date(),
        kyberKemUsed: result.kyber_kem_used,
        pqcStats: result.pqc_stats,
        sizeMB: result.size_mb
      };

      setEncryptionResults(prev => [encryptionResult, ...prev]);
      
      // Update parent component stats
      if (onStatsUpdate && result.pqc_stats) {
        onStatsUpdate(result.pqc_stats);
      }

      // Success feedback
      toast.success(
        `File encrypted with ${securityLevel}! ${result.kyber_kem_used ? 'Kyber KEM protection activated.' : ''}`,
        { id: 'encryption' }
      );

      // Show Kyber details if used
      if (result.kyber_kem_used) {
        setShowKyberDetails(true);
        setTimeout(() => setShowKyberDetails(false), 5000);
      }

      // Reset selection for next file
      setSelectedFile(null);
      setFileValidation(null);

    } catch (error) {
      console.error('Encryption error:', error);
      toast.error(error.message || 'Encryption failed', { id: 'encryption' });
    } finally {
      setIsEncrypting(false);
    }
  };

  const renderFileInfo = () => {
    if (!selectedFile) return null;

    const sizeInfo = fileService.getFileSizeCategory(selectedFile.size);
    const levelInfo = securityLevels[securityLevel];

    return (
      <div className="file-info-card" data-testid="file-info">
        <div className="file-header">
          <div className="file-icon">📄</div>
          <div className="file-details">
            <div className="file-name">{selectedFile.name}</div>
            <div className="file-meta">
              <span className="file-size" style={{ color: sizeInfo.color }}>
                {sizeInfo.value.toFixed(1)} {sizeInfo.unit}
              </span>
              {selectedFile.isDemoFile && (
                <span className="demo-badge">DEMO FILE</span>
              )}
            </div>
          </div>
        </div>

        {fileValidation && (
          <div className="validation-info">
            {fileValidation.recommendations.securityLevel && (
              <div className="recommendation">
                <span className="recommendation-icon">💡</span>
                <span className="recommendation-text">
                  Recommended: {levelInfo.name} - {fileValidation.recommendations.reason}
                </span>
              </div>
            )}
            
            {fileValidation.warnings.map((warning, index) => (
              <div key={index} className="warning">
                <span className="warning-icon">⚠️</span>
                <span className="warning-text">{warning}</span>
              </div>
            ))}
          </div>
        )}

        <div className="encryption-preview">
          <div className="security-selector">
            <label>Security Level:</label>
            <select 
              value={securityLevel} 
              onChange={(e) => setSecurityLevel(e.target.value)}
              className="security-select"
              data-testid="pqc-security-selector"
            >
              <option value="L1">L1 - Quantum OTP (≤50KB)</option>
              <option value="L2">L2 - Quantum-aided AES</option>
              <option value="L3">L3 - Post-Quantum Crypto</option>
              <option value="L4">L4 - Standard TLS</option>
            </select>
          </div>

          {securityLevel === 'L3' && selectedFile.size > 10 * 1024 * 1024 && (
            <div className="kyber-info">
              <div className="kyber-badge">
                <span className="kyber-icon">🔮</span>
                <span className="kyber-text">Kyber KEM Protection Enabled</span>
              </div>
              <div className="kyber-details">
                Large file detected - File Encryption Key will be protected using {pqcInfo.kyberKEM.name}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderDemoFiles = () => {
    const demoFiles = fileService.generateDemoFiles();

    return (
      <div className="demo-files-section">
        <h3>Try Demo Files</h3>
        <div className="demo-files-grid">
          {demoFiles.map((file, index) => {
            const sizeInfo = fileService.getFileSizeCategory(file.size);
            return (
              <button
                key={index}
                className="demo-file-button"
                onClick={() => handleDemoFileSelect(file)}
                data-testid={`demo-file-${index}`}
              >
                <div className="demo-file-icon">
                  {file.type.includes('pdf') ? '📄' : 
                   file.type.includes('presentation') ? '📊' : 
                   file.type.includes('video') ? '🎥' : '📁'}
                </div>
                <div className="demo-file-info">
                  <div className="demo-file-name">{file.name}</div>
                  <div className="demo-file-size" style={{ color: sizeInfo.color }}>
                    {sizeInfo.value.toFixed(1)} {sizeInfo.unit}
                  </div>
                  <div className="demo-file-desc">{file.description}</div>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  const renderEncryptionResults = () => {
    if (encryptionResults.length === 0) return null;

    return (
      <div className="encryption-results" data-testid="encryption-results">
        <h3>Encryption History</h3>
        <div className="results-list">
          {encryptionResults.map((result) => {
            const sizeInfo = fileService.getFileSizeCategory(result.originalSize);
            const levelInfo = securityLevels[result.securityLevel];
            
            return (
              <div key={result.id} className="result-item">
                <div className="result-header">
                  <div className="result-file">
                    <span className="result-icon">🔒</span>
                    <span className="result-name">{result.fileName}</span>
                  </div>
                  <div className="result-meta">
                    <span className="result-time">
                      {result.encryptedAt.toLocaleTimeString()}
                    </span>
                    <span className={`result-level level-${result.securityLevel.toLowerCase()}`}>
                      {levelInfo.icon} {result.securityLevel}
                    </span>
                  </div>
                </div>
                
                <div className="result-details">
                  <div className="result-stat">
                    <span className="stat-label">Size:</span>
                    <span className="stat-value" style={{ color: sizeInfo.color }}>
                      {sizeInfo.value.toFixed(1)} {sizeInfo.unit}
                    </span>
                  </div>
                  
                  {result.kyberKemUsed && (
                    <div className="result-stat">
                      <span className="stat-label">PQC:</span>
                      <span className="stat-value kyber-used">
                        🔮 Kyber KEM Protection
                      </span>
                    </div>
                  )}
                  
                  <div className="result-stat">
                    <span className="stat-label">Status:</span>
                    <span className="stat-value success">
                      ✅ Encrypted Successfully
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="pqc-file-demo" data-testid="pqc-file-demo">
      <div className="demo-header">
        <h2>Post-Quantum File Encryption</h2>
        <p>Demonstrate CRYSTALS-Kyber KEM protection for large files</p>
      </div>

      {/* File Upload Area */}
      <div className="upload-section">
        <div 
          {...getRootProps()} 
          className={`dropzone ${isDragActive ? 'active' : ''} ${selectedFile ? 'has-file' : ''}`}
          data-testid="file-dropzone"
        >
          <input {...getInputProps()} ref={fileInputRef} />
          
          {!selectedFile ? (
            <div className="dropzone-content">
              <div className="dropzone-icon">📁</div>
              <div className="dropzone-text">
                <h3>Drop files here or click to upload</h3>
                <p>Supports all file types up to 500MB</p>
              </div>
              <button 
                className="browse-button"
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
              >
                Browse Files
              </button>
            </div>
          ) : (
            <div className="file-selected">
              {renderFileInfo()}
              
              <div className="file-actions">
                <button
                  className={`encrypt-button ${isEncrypting ? 'encrypting' : ''}`}
                  onClick={handleEncryptFile}
                  disabled={isEncrypting}
                  data-testid="encrypt-file-button"
                >
                  {isEncrypting ? (
                    <>
                      <span className="loading-spinner"></span>
                      Encrypting with {securityLevels[securityLevel].name}...
                    </>
                  ) : (
                    <>
                      <span className="encrypt-icon">🔮</span>
                      Encrypt with {securityLevel}
                    </>
                  )}
                </button>
                
                <button
                  className="clear-button"
                  onClick={() => {
                    setSelectedFile(null);
                    setFileValidation(null);
                  }}
                  disabled={isEncrypting}
                >
                  Clear
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Demo Files */}
      {!selectedFile && renderDemoFiles()}

      {/* Kyber Details Modal */}
      {showKyberDetails && (
        <div className="kyber-modal" data-testid="kyber-modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3>🔮 Post-Quantum Encryption Complete</h3>
              <button 
                className="close-modal"
                onClick={() => setShowKyberDetails(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="kyber-success">
                <div className="success-icon">✅</div>
                <div className="success-text">
                  <h4>CRYSTALS-Kyber KEM Applied</h4>
                  <p>File Encryption Key secured against quantum computers</p>
                </div>
              </div>
              
              <div className="kyber-technical">
                <h4>Technical Details:</h4>
                <ul>
                  <li><strong>Algorithm:</strong> {pqcInfo.kyberKEM.name}</li>
                  <li><strong>Security Level:</strong> {pqcInfo.kyberKEM.securityLevel}</li>
                  <li><strong>Key Size:</strong> {pqcInfo.kyberKEM.keySize}</li>
                  <li><strong>Quantum Resistant:</strong> ✅ Shor's & Grover's algorithms</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Encryption Results */}
      {renderEncryptionResults()}

      <style jsx>{`
        .pqc-file-demo {
          background: white;
          border-radius: 16px;
          box-shadow: var(--shadow-medium);
          overflow: hidden;
        }

        .demo-header {
          background: linear-gradient(135deg, #9C27B0 0%, #673AB7 100%);
          color: white;
          padding: 24px;
          text-align: center;
        }

        .demo-header h2 {
          margin: 0 0 8px 0;
          font-size: 24px;
          font-weight: 600;
        }

        .demo-header p {
          margin: 0;
          font-size: 16px;
          opacity: 0.9;
        }

        .upload-section {
          padding: 24px;
        }

        .dropzone {
          border: 3px dashed var(--border-medium);
          border-radius: 12px;
          padding: 40px 24px;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s ease;
          background: var(--background-tertiary);
        }

        .dropzone:hover, .dropzone.active {
          border-color: var(--primary-blue);
          background: var(--primary-blue-light);
          transform: translateY(-2px);
        }

        .dropzone.has-file {
          border-color: var(--success-green);
          background: white;
          cursor: default;
        }

        .dropzone-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
        }

        .dropzone-icon {
          font-size: 48px;
          opacity: 0.7;
        }

        .dropzone-text h3 {
          margin: 0;
          font-size: 18px;
          color: var(--text-primary);
        }

        .dropzone-text p {
          margin: 4px 0 0 0;
          font-size: 14px;
          color: var(--text-secondary);
        }

        .browse-button {
          background: var(--primary-blue);
          color: white;
          border: none;
          border-radius: 8px;
          padding: 12px 24px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .browse-button:hover {
          background: var(--primary-blue-dark);
          transform: translateY(-1px);
        }

        .file-info-card {
          background: white;
          border: 2px solid var(--success-green);
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 16px;
        }

        .file-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }

        .file-icon {
          font-size: 32px;
        }

        .file-details {
          flex: 1;
        }

        .file-name {
          font-size: 16px;
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 4px;
        }

        .file-meta {
          display: flex;
          gap: 12px;
          align-items: center;
        }

        .file-size {
          font-size: 14px;
          font-weight: 500;
        }

        .demo-badge {
          background: var(--warning-orange);
          color: white;
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 600;
        }

        .validation-info {
          margin-bottom: 16px;
        }

        .recommendation, .warning {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          border-radius: 6px;
          font-size: 13px;
          margin-bottom: 4px;
        }

        .recommendation {
          background: var(--primary-blue-light);
          color: var(--primary-blue-dark);
        }

        .warning {
          background: #FFF3E0;
          color: var(--warning-orange);
        }

        .encryption-preview {
          border-top: 1px solid var(--border-light);
          padding-top: 16px;
        }

        .security-selector {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }

        .security-selector label {
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary);
        }

        .security-select {
          flex: 1;
          padding: 8px 12px;
          border: 2px solid var(--border-light);
          border-radius: 6px;
          font-size: 14px;
          cursor: pointer;
          transition: border-color 0.2s ease;
        }

        .security-select:focus {
          outline: none;
          border-color: var(--primary-blue);
        }

        .kyber-info {
          background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
          border: 2px solid var(--secondary-green);
          border-radius: 8px;
          padding: 12px;
        }

        .kyber-badge {
          display: flex;
          align-items: center;
          gap: 6px;
          font-weight: 600;
          color: var(--secondary-green-dark);
          margin-bottom: 4px;
        }

        .kyber-details {
          font-size: 12px;
          color: var(--secondary-green-dark);
          line-height: 1.4;
        }

        .file-actions {
          display: flex;
          gap: 12px;
          justify-content: center;
          margin-top: 16px;
        }

        .encrypt-button {
          background: linear-gradient(135deg, #9C27B0 0%, #673AB7 100%);
          color: white;
          border: none;
          border-radius: 12px;
          padding: 16px 32px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 8px;
          transition: all 0.3s ease;
          min-width: 200px;
          justify-content: center;
        }

        .encrypt-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(156, 39, 176, 0.3);
        }

        .encrypt-button:disabled {
          opacity: 0.7;
          cursor: not-allowed;
          transform: none;
        }

        .encrypt-button.encrypting {
          animation: pulse 2s infinite;
        }

        .clear-button {
          background: transparent;
          color: var(--text-secondary);
          border: 2px solid var(--border-medium);
          border-radius: 12px;
          padding: 16px 24px;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .clear-button:hover:not(:disabled) {
          background: var(--background-secondary);
          border-color: var(--text-secondary);
        }

        .demo-files-section {
          padding: 0 24px 24px;
        }

        .demo-files-section h3 {
          margin: 0 0 16px 0;
          font-size: 18px;
          color: var(--text-primary);
        }

        .demo-files-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 12px;
        }

        .demo-file-button {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 16px;
          background: var(--background-secondary);
          border: 2px solid var(--border-light);
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.2s ease;
          text-align: center;
        }

        .demo-file-button:hover {
          background: var(--primary-blue-light);
          border-color: var(--primary-blue);
          transform: translateY(-2px);
        }

        .demo-file-icon {
          font-size: 32px;
          margin-bottom: 8px;
        }

        .demo-file-name {
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary);
          margin-bottom: 4px;
        }

        .demo-file-size {
          font-size: 12px;
          font-weight: 600;
          margin-bottom: 4px;
        }

        .demo-file-desc {
          font-size: 11px;
          color: var(--text-secondary);
          line-height: 1.3;
        }

        .encryption-results {
          border-top: 1px solid var(--border-light);
          padding: 24px;
        }

        .encryption-results h3 {
          margin: 0 0 16px 0;
          font-size: 18px;
          color: var(--text-primary);
        }

        .results-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .result-item {
          background: var(--background-secondary);
          border: 1px solid var(--border-light);
          border-radius: 8px;
          padding: 16px;
        }

        .result-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .result-file {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .result-icon {
          font-size: 16px;
        }

        .result-name {
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary);
        }

        .result-meta {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .result-time {
          font-size: 12px;
          color: var(--text-secondary);
        }

        .result-level {
          padding: 2px 8px;
          border-radius: 6px;
          font-size: 11px;
          font-weight: 600;
        }

        .result-level.level-l3 {
          background: var(--secondary-green-light);
          color: var(--secondary-green-dark);
        }

        .result-details {
          display: flex;
          gap: 16px;
          flex-wrap: wrap;
        }

        .result-stat {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
        }

        .stat-label {
          color: var(--text-secondary);
        }

        .stat-value {
          font-weight: 500;
        }

        .stat-value.kyber-used {
          color: #9C27B0;
        }

        .stat-value.success {
          color: var(--success-green);
        }

        .kyber-modal {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          animation: fadeIn 0.3s ease;
        }

        .modal-content {
          background: white;
          border-radius: 16px;
          box-shadow: var(--shadow-heavy);
          max-width: 500px;
          width: 90%;
          max-height: 80vh;
          overflow-y: auto;
          animation: slideUp 0.3s ease;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          border-bottom: 1px solid var(--border-light);
          background: linear-gradient(135deg, #9C27B0 0%, #673AB7 100%);
          color: white;
          border-radius: 16px 16px 0 0;
        }

        .modal-header h3 {
          margin: 0;
          font-size: 18px;
        }

        .close-modal {
          background: none;
          border: none;
          color: white;
          font-size: 24px;
          cursor: pointer;
          padding: 4px;
        }

        .modal-body {
          padding: 20px;
        }

        .kyber-success {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 20px;
          padding: 16px;
          background: var(--secondary-green-light);
          border-radius: 8px;
        }

        .success-icon {
          font-size: 24px;
        }

        .success-text h4 {
          margin: 0 0 4px 0;
          color: var(--secondary-green-dark);
        }

        .success-text p {
          margin: 0;
          font-size: 14px;
          color: var(--secondary-green-dark);
        }

        .kyber-technical {
          background: var(--background-secondary);
          padding: 16px;
          border-radius: 8px;
        }

        .kyber-technical h4 {
          margin: 0 0 12px 0;
          color: var(--text-primary);
        }

        .kyber-technical ul {
          margin: 0;
          padding-left: 16px;
          list-style: none;
        }

        .kyber-technical li {
          margin-bottom: 8px;
          font-size: 13px;
          color: var(--text-primary);
          position: relative;
        }

        .kyber-technical li::before {
          content: '•';
          color: var(--primary-blue);
          font-weight: bold;
          position: absolute;
          left: -12px;
        }

        /* Animations */
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes slideUp {
          from { transform: translateY(30px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .demo-files-grid {
            grid-template-columns: 1fr;
          }

          .file-actions {
            flex-direction: column;
          }

          .encrypt-button {
            min-width: auto;
          }

          .result-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
          }

          .result-meta {
            gap: 8px;
          }
        }
      `}</style>
    </div>
  );
};

export default PQCFileDemo;