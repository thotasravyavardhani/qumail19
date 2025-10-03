import React, { useState } from 'react';
import toast from 'react-hot-toast';

const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const demoAccounts = [
    { email: 'alice@qumail.com', password: 'quantum123', name: 'Alice Smith' },
    { email: 'bob@qumail.com', password: 'secure456', name: 'Bob Johnson' }, 
    { email: 'demo@qumail.com', password: 'demo123', name: 'Demo User' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error('Please enter both email and password');
      return;
    }

    setIsLoading(true);
    try {
      await onLogin(email, password);
    } catch (error) {
      // Error handling is done in parent component
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = (account) => {
    setEmail(account.email);
    setPassword(account.password);
    // Auto-submit after brief delay
    setTimeout(() => {
      onLogin(account.email, account.password);
    }, 100);
  };

  return (
    <div className="login-page" data-testid="login-page">
      <div className="login-container">
        {/* Quantum Branding */}
        <div className="login-header">
          <div className="quantum-logo-large">
            <span className="logo-symbol">Ψ</span>
            <span className="logo-text">QuMail</span>
          </div>
          <h1 className="login-title">Quantum Secure Communications</h1>
          <p className="login-subtitle">
            ISRO-Grade encryption with KME quantum key distribution
          </p>
        </div>

        {/* Login Form */}
        <div className="login-form-container">
          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="form-input"
                placeholder="Enter your email"
                data-testid="email-input"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="form-input"
                placeholder="Enter your password"
                data-testid="password-input"
                required
              />
            </div>

            <button
              type="submit"
              className={`login-button ${isLoading ? 'loading' : ''}`}
              disabled={isLoading || !email || !password}
              data-testid="login-button"
            >
              {isLoading ? (
                <>
                  <span className="loading-spinner"></span>
                  Authenticating...
                </>
              ) : (
                <>
                  <span className="login-icon">🔐</span>
                  Enter Quantum Network
                </>
              )}
            </button>
          </form>

          {/* Demo Accounts Section */}
          <div className="demo-section">
            <div className="demo-divider">
              <span className="divider-text">Hackathon Demo Accounts</span>
            </div>
            
            <div className="demo-accounts">
              {demoAccounts.map((account, index) => (
                <button
                  key={account.email}
                  className="demo-account-button"
                  onClick={() => handleDemoLogin(account)}
                  data-testid={`demo-login-${account.email}`}
                >
                  <div className="demo-avatar">
                    {account.name.charAt(0)}
                  </div>
                  <div className="demo-info">
                    <div className="demo-name">{account.name}</div>
                    <div className="demo-email">{account.email}</div>
                  </div>
                  <div className="demo-arrow">→</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Features Preview */}
        <div className="features-preview">
          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-icon">⚛️</div>
              <div className="feature-title">Quantum OTP</div>
              <div className="feature-desc">Perfect secrecy encryption</div>
            </div>
            <div className="feature-item">
              <div className="feature-icon">🔮</div>
              <div className="feature-title">Post-Quantum</div>
              <div className="feature-desc">Kyber KEM protection</div>
            </div>
            <div className="feature-item">
              <div className="feature-icon">💬</div>
              <div className="feature-title">Real-time Chat</div>
              <div className="feature-desc">WebSocket quantum keys</div>
            </div>
            <div className="feature-item">
              <div className="feature-icon">📧</div>
              <div className="feature-title">Secure Email</div>
              <div className="feature-desc">Gmail integration</div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="login-footer">
          <p>Smart India Hackathon 2024 • ISRO Quantum Communications Project</p>
        </div>
      </div>

      <style jsx>{`
        .login-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 20px;
        }

        .login-container {
          background: white;
          border-radius: 24px;
          box-shadow: 0 20px 40px rgba(0,0,0,0.1);
          padding: 40px;
          width: 100%;
          max-width: 480px;
          text-align: center;
        }

        .login-header {
          margin-bottom: 32px;
        }

        .quantum-logo-large {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          margin-bottom: 16px;
        }

        .logo-symbol {
          font-size: 48px;
          font-weight: bold;
          background: linear-gradient(135deg, var(--quantum-cyan) 0%, var(--primary-blue) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .logo-text {
          font-size: 36px;
          font-weight: 700;
          color: var(--primary-blue);
        }

        .login-title {
          font-size: 24px;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 8px 0;
        }

        .login-subtitle {
          font-size: 16px;
          color: var(--text-secondary);
          margin: 0;
          line-height: 1.4;
        }

        .login-form-container {
          margin-bottom: 32px;
        }

        .login-form {
          display: flex;
          flex-direction: column;
          gap: 20px;
          margin-bottom: 24px;
        }

        .form-group {
          text-align: left;
        }

        .form-label {
          display: block;
          margin-bottom: 8px;
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary);
        }

        .form-input {
          width: 100%;
          padding: 16px;
          border: 2px solid var(--border-light);
          border-radius: 12px;
          font-size: 16px;
          font-family: inherit;
          transition: all 0.2s ease;
          background: white;
        }

        .form-input:focus {
          outline: none;
          border-color: var(--primary-blue);
          box-shadow: 0 0 0 3px var(--primary-blue-light);
        }

        .login-button {
          width: 100%;
          padding: 16px 24px;
          background: linear-gradient(135deg, var(--primary-blue) 0%, var(--quantum-cyan) 100%);
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 16px;
          font-weight: 600;
          font-family: inherit;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          min-height: 56px;
        }

        .login-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(30, 136, 229, 0.3);
        }

        .login-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .login-icon {
          font-size: 18px;
        }

        .loading-spinner {
          width: 18px;
          height: 18px;
          border: 2px solid rgba(255,255,255,0.3);
          border-top: 2px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        .demo-section {
          margin-top: 24px;
        }

        .demo-divider {
          position: relative;
          text-align: center;
          margin: 24px 0;
        }

        .demo-divider::before {
          content: '';
          position: absolute;
          top: 50%;
          left: 0;
          right: 0;
          height: 1px;
          background: var(--border-light);
        }

        .divider-text {
          background: white;
          padding: 0 16px;
          font-size: 12px;
          color: var(--text-secondary);
          text-transform: uppercase;
          font-weight: 500;
        }

        .demo-accounts {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .demo-account-button {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          background: var(--background-secondary);
          border: 1px solid var(--border-light);
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.2s ease;
          text-align: left;
        }

        .demo-account-button:hover {
          background: var(--primary-blue-light);
          border-color: var(--primary-blue);
          transform: translateX(4px);
        }

        .demo-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: var(--primary-blue);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 14px;
        }

        .demo-info {
          flex: 1;
        }

        .demo-name {
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary);
          margin-bottom: 2px;
        }

        .demo-email {
          font-size: 12px;
          color: var(--text-secondary);
        }

        .demo-arrow {
          font-size: 16px;
          color: var(--text-hint);
        }

        .features-preview {
          margin-bottom: 24px;
        }

        .features-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
        }

        .feature-item {
          text-align: center;
          padding: 16px;
          background: var(--background-secondary);
          border-radius: 12px;
          border: 1px solid var(--border-light);
        }

        .feature-icon {
          font-size: 24px;
          margin-bottom: 8px;
        }

        .feature-title {
          font-size: 12px;
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 4px;
        }

        .feature-desc {
          font-size: 11px;
          color: var(--text-secondary);
          line-height: 1.3;
        }

        .login-footer {
          font-size: 12px;
          color: var(--text-hint);
          padding-top: 20px;
          border-top: 1px solid var(--border-light);
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .login-page {
            padding: 16px;
          }

          .login-container {
            padding: 24px;
          }

          .quantum-logo-large {
            gap: 8px;
          }

          .logo-symbol {
            font-size: 36px;
          }

          .logo-text {
            font-size: 28px;
          }

          .login-title {
            font-size: 20px;
          }

          .features-grid {
            grid-template-columns: 1fr;
            gap: 12px;
          }
        }

        /* Animations */
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .login-container {
          animation: slideUp 0.5s ease-out;
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default LoginPage;