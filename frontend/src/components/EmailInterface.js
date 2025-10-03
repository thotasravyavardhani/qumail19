import React, { useState, useEffect } from 'react';
import emailService from '../services/emailService';
import quantumService from '../services/quantumService';
import toast from 'react-hot-toast';

const EmailInterface = ({ user, quantumStatus, onRefreshStatus, activeFolder = 'Inbox' }) => {
  const [activeView, setActiveView] = useState('inbox'); // inbox, compose
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentFolder, setCurrentFolder] = useState(activeFolder);
  
  const folders = ['Inbox', 'Sent', 'Quantum Vault'];

  // Compose state
  const [composeData, setComposeData] = useState({
    to: '',
    subject: '',
    body: '',
    securityLevel: 'L2'
  });
  const [isSending, setIsSending] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);

  const securityLevels = quantumService.getSecurityLevelInfo();
  const demoTemplates = emailService.getDemoTemplates();
  const demoRecipients = emailService.getDemoRecipients();

  // Load emails on component mount and folder change
  useEffect(() => {
    if (user) {
      loadEmails(currentFolder);
    }
  }, [user, currentFolder]);

  const loadEmails = async (folder = 'Inbox') => {
    try {
      setIsLoading(true);
      const emailList = await emailService.getInbox(folder, 50);
      const formattedEmails = emailList.map(email => emailService.formatEmail(email));
      setEmails(formattedEmails);
    } catch (error) {
      console.error('Failed to load emails:', error);
      toast.error('Failed to load emails');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendEmail = async () => {
    // Validate form
    if (!composeData.to || !composeData.subject || !composeData.body) {
      toast.error('Please fill in all required fields');
      return;
    }

    if (!emailService.validateEmail(composeData.to)) {
      toast.error('Please enter a valid email address');
      return;
    }

    setIsSending(true);

    try {
      // Estimate encryption time for better UX
      const estimatedTime = emailService.estimateEncryptionTime(
        composeData.securityLevel,
        composeData.body.length
      );

      // Show progress toast
      const loadingToast = toast.loading(
        `Encrypting with ${securityLevels[composeData.securityLevel].name}...`,
        { id: 'sending-email' }
      );

      // Send email
      const result = await emailService.sendQuantumEmail(composeData);

      // Success feedback
      toast.success(
        `Email sent with ${composeData.securityLevel} encryption!`,
        { id: 'sending-email' }
      );

      // Check if it's a real external email
      const isExternalEmail = !composeData.to.includes('@qumail.com');
      if (isExternalEmail) {
        toast.success(
          '📧 Check your real email inbox! The quantum-encrypted message was delivered externally.',
          { duration: 6000 }
        );
      }

      // Reset compose form
      setComposeData({
        to: '',
        subject: '',
        body: '',
        securityLevel: 'L2'
      });

      // Switch back to inbox and refresh
      setActiveView('inbox');
      setTimeout(() => {
        loadEmails(currentFolder);
        if (onRefreshStatus) onRefreshStatus();
      }, 1000);

    } catch (error) {
      console.error('Send email error:', error);
      toast.error(error.message || 'Failed to send email', { id: 'sending-email' });
    } finally {
      setIsSending(false);
    }
  };

  const handleEmailClick = async (email) => {
    if (email.isEncrypted) {
      try {
        setIsLoading(true);
        toast.loading('Decrypting quantum message...', { id: 'decrypt' });
        
        const decryptedEmail = await emailService.getEmailDetails(email.id);
        
        setSelectedEmail({
          ...email,
          body: decryptedEmail.body,
          decryptedAt: new Date(decryptedEmail.decrypted_at),
          pqcDetails: decryptedEmail.pqc_details
        });

        toast.success('Message decrypted successfully!', { id: 'decrypt' });
      } catch (error) {
        console.error('Decrypt error:', error);
        toast.error('Failed to decrypt message', { id: 'decrypt' });
      } finally {
        setIsLoading(false);
      }
    } else {
      setSelectedEmail(email);
    }
  };

  const handleTemplateSelect = (template) => {
    setComposeData({
      ...composeData,
      subject: template.subject,
      body: template.body,
      securityLevel: template.securityLevel
    });
    setShowTemplates(false);
    toast.success(`Template loaded: ${template.name}`);
  };

  const handleRecipientSelect = (recipient) => {
    setComposeData({
      ...composeData,
      to: recipient.email
    });
    toast.success(`Recipient set: ${recipient.name}`);
  };

  const renderEmailList = () => (
    <div className="email-list" data-testid="email-list">
      {isLoading ? (
        <div className="loading-center">
          <div className="loading-spinner"></div>
          <p>Loading emails...</p>
        </div>
      ) : emails.length === 0 ? (
        <div className="empty-inbox">
          <div className="empty-icon">📭</div>
          <h3>No emails in {currentFolder}</h3>
          <p>Quantum-encrypted messages will appear here</p>
        </div>
      ) : (
        emails.map(email => {
          const securityInfo = emailService.getEmailSecurityInfo(email.securityLevel);
          return (
            <div 
              key={email.id}
              className={`email-item ${selectedEmail?.id === email.id ? 'selected' : ''}`}
              onClick={() => handleEmailClick(email)}
              data-testid={`email-item-${email.id}`}
            >
              <div className="email-header">
                <div className="email-sender">{email.sender}</div>
                <div className="email-meta">
                  <span className="email-time">
                    {email.receivedAt.toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </span>
                  <span 
                    className="security-badge"
                    style={{ 
                      backgroundColor: `${securityInfo.color}20`,
                      color: securityInfo.color,
                      border: `1px solid ${securityInfo.color}`
                    }}
                  >
                    {securityInfo.icon} {email.securityLevel}
                  </span>
                </div>
              </div>
              <div className="email-subject">{email.subject}</div>
              <div className="email-preview">{email.preview}</div>
              {email.isEncrypted && (
                <div className="encryption-indicator">
                  <span className="encrypt-icon">🔐</span>
                  <span className="encrypt-text">Quantum Encrypted</span>
                </div>
              )}
            </div>
          );
        })
      )}
    </div>
  );

  const renderEmailDetail = () => {
    if (!selectedEmail) return null;

    const securityInfo = emailService.getEmailSecurityInfo(selectedEmail.securityLevel);

    return (
      <div className="email-detail" data-testid="email-detail">
        <div className="email-detail-header">
          <button 
            className="back-button"
            onClick={() => setSelectedEmail(null)}
            data-testid="back-to-list"
          >
            ← Back to {currentFolder}
          </button>
          
          <div className="email-detail-meta">
            <div className="detail-security">
              <span 
                className="security-pill"
                style={{ backgroundColor: securityInfo.color }}
              >
                {securityInfo.icon} {securityInfo.name}
              </span>
              {selectedEmail.decryptedAt && (
                <span className="decrypt-time">
                  Decrypted: {selectedEmail.decryptedAt.toLocaleTimeString()}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="email-detail-content">
          <div className="detail-from">
            <strong>From:</strong> {selectedEmail.sender}
          </div>
          <div className="detail-subject">
            <strong>Subject:</strong> {selectedEmail.subject}
          </div>
          <div className="detail-received">
            <strong>Received:</strong> {selectedEmail.receivedAt.toLocaleString()}
          </div>
          
          {selectedEmail.pqcDetails && (
            <div className="pqc-details">
              <h4>🔮 Post-Quantum Encryption Details</h4>
              <div className="pqc-info">
                <p><strong>Files Encrypted:</strong> {selectedEmail.pqcDetails.attachment_count}</p>
                <p><strong>Total Size:</strong> {selectedEmail.pqcDetails.total_size} bytes</p>
                <p><strong>Kyber KEM:</strong> {selectedEmail.pqcDetails.kyber_kem ? '✅ Active' : '❌ Not Used'}</p>
              </div>
            </div>
          )}

          <div className="detail-body">
            <div className="body-content">
              {selectedEmail.body}
            </div>
          </div>

          {selectedEmail.isEncrypted && (
            <div className="quantum-proof">
              <div className="proof-header">
                <span className="proof-icon">Ψ</span>
                <span className="proof-title">Quantum Decryption Proof</span>
              </div>
              <div className="proof-details">
                This message was successfully decrypted using quantum keys from the KME.
                The original ciphertext was protected with {securityInfo.description}.
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderCompose = () => (
    <div className="compose-interface" data-testid="compose-interface">
      <div className="compose-header">
        <h3>Compose Quantum-Encrypted Email</h3>
        <div className="compose-actions">
          <button
            className="templates-button"
            onClick={() => setShowTemplates(!showTemplates)}
            data-testid="templates-button"
          >
            📝 Templates
          </button>
        </div>
      </div>

      {showTemplates && (
        <div className="templates-panel" data-testid="templates-panel">
          <h4>Demo Templates</h4>
          <div className="templates-grid">
            {demoTemplates.map(template => (
              <button
                key={template.id}
                className="template-button"
                onClick={() => handleTemplateSelect(template)}
                data-testid={`template-${template.id}`}
              >
                <div className="template-name">{template.name}</div>
                <div className="template-category">{template.category}</div>
                <div className="template-security">
                  {securityLevels[template.securityLevel].icon} {template.securityLevel}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="compose-form">
        <div className="form-row">
          <label className="form-label">To:</label>
          <input
            type="email"
            value={composeData.to}
            onChange={(e) => setComposeData({...composeData, to: e.target.value})}
            placeholder="recipient@example.com"
            className="form-input"
            data-testid="compose-to"
          />
        </div>

        <div className="recipient-suggestions">
          <div className="suggestions-header">Quick Recipients:</div>
          <div className="suggestions-list">
            {demoRecipients.map(recipient => (
              <button
                key={recipient.email}
                className="recipient-chip"
                onClick={() => handleRecipientSelect(recipient)}
                data-testid={`recipient-${recipient.email}`}
              >
                {recipient.name} ({recipient.email})
              </button>
            ))}
          </div>
        </div>

        <div className="form-row">
          <label className="form-label">Subject:</label>
          <input
            type="text"
            value={composeData.subject}
            onChange={(e) => setComposeData({...composeData, subject: e.target.value})}
            placeholder="Enter subject"
            className="form-input"
            data-testid="compose-subject"
          />
        </div>

        <div className="form-row">
          <label className="form-label">Security Level:</label>
          <select
            value={composeData.securityLevel}
            onChange={(e) => setComposeData({...composeData, securityLevel: e.target.value})}
            className="form-select"
            data-testid="compose-security"
          >
            <option value="L1">L1 - Quantum OTP (≤50KB)</option>
            <option value="L2">L2 - Quantum-aided AES (Recommended)</option>
            <option value="L3">L3 - Post-Quantum Crypto</option>
            <option value="L4">L4 - Standard TLS</option>
          </select>
        </div>

        <div className="form-row">
          <label className="form-label">Message:</label>
          <textarea
            value={composeData.body}
            onChange={(e) => setComposeData({...composeData, body: e.target.value})}
            placeholder="Enter your quantum-encrypted message..."
            className="form-textarea"
            rows="8"
            data-testid="compose-body"
          />
        </div>

        <div className="compose-footer">
          <div className="encryption-info">
            <span className="encrypt-icon">🔐</span>
            <span className="encrypt-text">
              Will be encrypted with {securityLevels[composeData.securityLevel]?.name}
            </span>
          </div>
          
          <button
            className={`send-button ${isSending ? 'sending' : ''}`}
            onClick={handleSendEmail}
            disabled={isSending || !composeData.to || !composeData.subject || !composeData.body}
            data-testid="send-email-button"
          >
            {isSending ? (
              <>
                <span className="loading-spinner"></span>
                Encrypting & Sending...
              </>
            ) : (
              <>
                <span className="send-icon">🚀</span>
                Send Quantum Email
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="email-interface" data-testid="email-interface">
      {/* Email Header */}
      <div className="email-header">
        <div className="email-title">
          <h2>Quantum Secure Email</h2>
          <div className="email-subtitle">
            Real-world delivery with quantum encryption
          </div>
        </div>

        <div className="email-nav">
          <button
            className={`nav-button ${activeView === 'inbox' ? 'active' : ''}`}
            onClick={() => setActiveView('inbox')}
            data-testid="inbox-tab"
          >
            📧 Inbox
          </button>
          <button
            className={`nav-button ${activeView === 'compose' ? 'active' : ''}`}
            onClick={() => setActiveView('compose')}
            data-testid="compose-tab"
          >
            ✍️ Compose
          </button>
        </div>
      </div>

      <div className="email-body">
        {activeView === 'inbox' && (
          <>
            {/* Folder Sidebar */}
            <div className="email-sidebar">
              <h4>Folders</h4>
              {folders.map(folder => (
                <button
                  key={folder}
                  className={`folder-button ${currentFolder === folder ? 'active' : ''}`}
                  onClick={() => setCurrentFolder(folder)}
                  data-testid={`folder-${folder.toLowerCase()}`}
                >
                  {folder === 'Inbox' && '📥'}
                  {folder === 'Sent' && '📤'} 
                  {folder === 'Quantum Vault' && '🔐'}
                  {folder}
                </button>
              ))}
              
              <button 
                className="refresh-button"
                onClick={() => loadEmails(currentFolder)}
                disabled={isLoading}
                data-testid="refresh-emails"
              >
                🔄 Refresh
              </button>
            </div>

            {/* Email Content */}
            <div className="email-content">
              {selectedEmail ? renderEmailDetail() : renderEmailList()}
            </div>
          </>
        )}

        {activeView === 'compose' && renderCompose()}
      </div>

      <style jsx>{`
        .email-interface {
          background: white;
          border-radius: 12px;
          box-shadow: var(--shadow-medium);
          overflow: hidden;
          height: 600px;
          display: flex;
          flex-direction: column;
        }

        .email-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px 24px;
          background: linear-gradient(135deg, var(--primary-blue) 0%, var(--quantum-cyan) 100%);
          color: white;
        }

        .email-title h2 {
          margin: 0;
          font-size: 20px;
          font-weight: 600;
        }

        .email-subtitle {
          font-size: 14px;
          opacity: 0.9;
          margin-top: 2px;
        }

        .email-nav {
          display: flex;
          gap: 8px;
        }

        .nav-button {
          background: rgba(255, 255, 255, 0.2);
          color: white;
          border: none;
          border-radius: 8px;
          padding: 8px 16px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .nav-button:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .nav-button.active {
          background: white;
          color: var(--primary-blue);
        }

        .email-body {
          flex: 1;
          display: flex;
          min-height: 0;
        }

        .email-sidebar {
          width: 200px;
          background: var(--background-secondary);
          border-right: 1px solid var(--border-light);
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .email-sidebar h4 {
          margin: 0 0 8px 0;
          font-size: 14px;
          color: var(--text-secondary);
          text-transform: uppercase;
          font-weight: 600;
        }

        .folder-button {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 12px;
          background: transparent;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          color: var(--text-primary);
          text-align: left;
          transition: all 0.2s ease;
        }

        .folder-button:hover {
          background: var(--primary-blue-light);
        }

        .folder-button.active {
          background: var(--primary-blue);
          color: white;
        }

        .refresh-button {
          margin-top: 16px;
          padding: 8px 12px;
          background: var(--primary-blue);
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 12px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .refresh-button:hover:not(:disabled) {
          background: var(--primary-blue-dark);
        }

        .refresh-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .email-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-width: 0;
        }

        .email-list {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
        }

        .loading-center {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 200px;
          color: var(--text-secondary);
        }

        .empty-inbox {
          text-align: center;
          padding: 60px 20px;
          color: var(--text-secondary);
        }

        .empty-icon {
          font-size: 48px;
          margin-bottom: 16px;
        }

        .empty-inbox h3 {
          margin: 0 0 8px 0;
          color: var(--text-primary);
        }

        .email-item {
          border: 1px solid var(--border-light);
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 12px;
          cursor: pointer;
          transition: all 0.2s ease;
          background: white;
        }

        .email-item:hover {
          border-color: var(--primary-blue);
          box-shadow: var(--shadow-light);
        }

        .email-item.selected {
          border-color: var(--primary-blue);
          background: var(--primary-blue-light);
        }

        .email-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .email-sender {
          font-size: 14px;
          font-weight: 600;
          color: var(--text-primary);
        }

        .email-meta {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .email-time {
          font-size: 12px;
          color: var(--text-secondary);
        }

        .security-badge {
          padding: 2px 6px;
          border-radius: 6px;
          font-size: 11px;
          font-weight: 600;
        }

        .email-subject {
          font-size: 15px;
          font-weight: 500;
          color: var(--text-primary);
          margin-bottom: 4px;
        }

        .email-preview {
          font-size: 13px;
          color: var(--text-secondary);
          line-height: 1.4;
          margin-bottom: 8px;
        }

        .encryption-indicator {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 11px;
          color: var(--quantum-cyan);
        }

        .email-detail {
          flex: 1;
          display: flex;
          flex-direction: column;
          background: white;
        }

        .email-detail-header {
          padding: 16px 20px;
          border-bottom: 1px solid var(--border-light);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .back-button {
          background: var(--primary-blue);
          color: white;
          border: none;
          border-radius: 6px;
          padding: 8px 12px;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .back-button:hover {
          background: var(--primary-blue-dark);
        }

        .security-pill {
          padding: 4px 12px;
          border-radius: 12px;
          color: white;
          font-size: 12px;
          font-weight: 600;
        }

        .decrypt-time {
          font-size: 11px;
          color: var(--text-secondary);
          margin-left: 8px;
        }

        .email-detail-content {
          flex: 1;
          padding: 20px;
          overflow-y: auto;
        }

        .detail-from, .detail-subject, .detail-received {
          margin-bottom: 12px;
          font-size: 14px;
        }

        .pqc-details {
          background: var(--secondary-green-light);
          border: 1px solid var(--secondary-green);
          border-radius: 8px;
          padding: 12px;
          margin: 16px 0;
        }

        .pqc-details h4 {
          margin: 0 0 8px 0;
          color: var(--secondary-green-dark);
        }

        .pqc-info p {
          margin: 4px 0;
          font-size: 13px;
          color: var(--secondary-green-dark);
        }

        .detail-body {
          background: var(--background-tertiary);
          border-radius: 8px;
          padding: 16px;
          margin: 16px 0;
        }

        .body-content {
          font-size: 14px;
          line-height: 1.6;
          color: var(--text-primary);
          white-space: pre-wrap;
        }

        .quantum-proof {
          background: var(--quantum-cyan-light);
          border: 1px solid var(--quantum-cyan);
          border-radius: 8px;
          padding: 12px;
          margin-top: 16px;
        }

        .proof-header {
          display: flex;
          align-items: center;
          gap: 6px;
          margin-bottom: 6px;
          font-weight: 600;
          color: var(--quantum-cyan-dark);
        }

        .proof-details {
          font-size: 12px;
          color: var(--quantum-cyan-dark);
          line-height: 1.4;
        }

        .compose-interface {
          flex: 1;
          display: flex;
          flex-direction: column;
          padding: 20px;
        }

        .compose-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .compose-header h3 {
          margin: 0;
          color: var(--text-primary);
        }

        .templates-button {
          background: var(--secondary-green);
          color: white;
          border: none;
          border-radius: 6px;
          padding: 8px 12px;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .templates-button:hover {
          background: var(--secondary-green-dark);
        }

        .templates-panel {
          background: var(--background-secondary);
          border: 1px solid var(--border-light);
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 16px;
        }

        .templates-panel h4 {
          margin: 0 0 12px 0;
          color: var(--text-primary);
        }

        .templates-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 8px;
        }

        .template-button {
          background: white;
          border: 1px solid var(--border-light);
          border-radius: 6px;
          padding: 12px;
          cursor: pointer;
          text-align: left;
          transition: all 0.2s ease;
        }

        .template-button:hover {
          border-color: var(--primary-blue);
          background: var(--primary-blue-light);
        }

        .template-name {
          font-size: 13px;
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 4px;
        }

        .template-category {
          font-size: 11px;
          color: var(--text-secondary);
          text-transform: uppercase;
          margin-bottom: 4px;
        }

        .template-security {
          font-size: 11px;
          color: var(--primary-blue);
        }

        .compose-form {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .form-row {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .form-label {
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary);
        }

        .form-input, .form-select, .form-textarea {
          padding: 12px;
          border: 2px solid var(--border-light);
          border-radius: 6px;
          font-size: 14px;
          font-family: inherit;
          transition: border-color 0.2s ease;
        }

        .form-input:focus, .form-select:focus, .form-textarea:focus {
          outline: none;
          border-color: var(--primary-blue);
        }

        .form-textarea {
          resize: vertical;
          min-height: 120px;
        }

        .recipient-suggestions {
          margin-bottom: 8px;
        }

        .suggestions-header {
          font-size: 12px;
          color: var(--text-secondary);
          margin-bottom: 6px;
        }

        .suggestions-list {
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
        }

        .recipient-chip {
          background: var(--primary-blue-light);
          color: var(--primary-blue-dark);
          border: 1px solid var(--primary-blue);
          border-radius: 12px;
          padding: 4px 8px;
          font-size: 11px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .recipient-chip:hover {
          background: var(--primary-blue);
          color: white;
        }

        .compose-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 16px;
          padding-top: 16px;
          border-top: 1px solid var(--border-light);
        }

        .encryption-info {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: var(--text-secondary);
        }

        .send-button {
          background: linear-gradient(135deg, var(--primary-blue) 0%, var(--quantum-cyan) 100%);
          color: white;
          border: none;
          border-radius: 8px;
          padding: 12px 24px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 8px;
          transition: all 0.2s ease;
        }

        .send-button:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: var(--shadow-medium);
        }

        .send-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .send-button.sending {
          animation: pulse 2s infinite;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .email-header {
            flex-direction: column;
            gap: 12px;
            align-items: stretch;
          }

          .email-body {
            flex-direction: column;
          }

          .email-sidebar {
            width: 100%;
            flex-direction: row;
            gap: 8px;
            overflow-x: auto;
          }

          .templates-grid {
            grid-template-columns: 1fr;
          }

          .compose-footer {
            flex-direction: column;
            gap: 12px;
            align-items: stretch;
          }
        }
      `}</style>
    </div>
  );
};

export default EmailInterface;
