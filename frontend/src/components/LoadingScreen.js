import React from 'react';

const LoadingScreen = () => {
  return (
    <div className="loading-screen" data-testid="loading-screen">
      <div className="loading-content">
        <div className="quantum-logo-loading">
          <span className="logo-symbol pulse">Ψ</span>
          <span className="logo-text">QuMail</span>
        </div>
        
        <div className="loading-animation">
          <div className="quantum-spinner">
            <div className="spinner-ring"></div>
            <div className="spinner-ring"></div>
            <div className="spinner-ring"></div>
          </div>
        </div>
        
        <div className="loading-text">
          <h2>Initializing Quantum Network</h2>
          <p>Establishing secure KME connection...</p>
        </div>
        
        <div className="loading-steps">
          <div className="step active">
            <span className="step-icon">🔐</span>
            <span className="step-text">Authentication</span>
          </div>
          <div className="step">
            <span className="step-icon">⚛️</span>
            <span className="step-text">KME Handshake</span>
          </div>
          <div className="step">
            <span className="step-icon">🌐</span>
            <span className="step-text">Quantum Ready</span>
          </div>
        </div>
      </div>

      <style jsx>{`
        .loading-screen {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 9999;
        }

        .loading-content {
          text-align: center;
          color: white;
          max-width: 400px;
          padding: 40px;
        }

        .quantum-logo-loading {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 16px;
          margin-bottom: 40px;
        }

        .logo-symbol {
          font-size: 64px;
          font-weight: bold;
          background: linear-gradient(135deg, var(--quantum-cyan) 0%, #ffffff 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .logo-text {
          font-size: 48px;
          font-weight: 700;
          color: white;
        }

        .pulse {
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }

        .loading-animation {
          margin: 40px 0;
        }

        .quantum-spinner {
          position: relative;
          width: 80px;
          height: 80px;
          margin: 0 auto;
        }

        .spinner-ring {
          position: absolute;
          border: 3px solid rgba(255, 255, 255, 0.2);
          border-top: 3px solid white;
          border-radius: 50%;
          animation: spin 1.5s linear infinite;
        }

        .spinner-ring:nth-child(1) {
          width: 80px;
          height: 80px;
          animation-duration: 1.5s;
        }

        .spinner-ring:nth-child(2) {
          width: 60px;
          height: 60px;
          top: 10px;
          left: 10px;
          animation-duration: 2s;
          animation-direction: reverse;
        }

        .spinner-ring:nth-child(3) {
          width: 40px;
          height: 40px;
          top: 20px;
          left: 20px;
          animation-duration: 1s;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .loading-text {
          margin-bottom: 40px;
        }

        .loading-text h2 {
          font-size: 24px;
          font-weight: 600;
          margin: 0 0 8px 0;
        }

        .loading-text p {
          font-size: 16px;
          margin: 0;
          opacity: 0.9;
        }

        .loading-steps {
          display: flex;
          justify-content: center;
          gap: 24px;
        }

        .step {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
          opacity: 0.5;
          transition: opacity 0.3s ease;
        }

        .step.active {
          opacity: 1;
          animation: stepPulse 2s infinite;
        }

        @keyframes stepPulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }

        .step-icon {
          font-size: 24px;
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.2);
          display: flex;
          align-items: center;
          justify-content: center;
          border: 2px solid rgba(255, 255, 255, 0.3);
        }

        .step.active .step-icon {
          background: rgba(255, 255, 255, 0.3);
          border-color: white;
          box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
        }

        .step-text {
          font-size: 12px;
          font-weight: 500;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .loading-content {
            padding: 20px;
          }

          .quantum-logo-loading {
            gap: 12px;
            margin-bottom: 30px;
          }

          .logo-symbol {
            font-size: 48px;
          }

          .logo-text {
            font-size: 36px;
          }

          .loading-text h2 {
            font-size: 20px;
          }

          .loading-text p {
            font-size: 14px;
          }

          .loading-steps {
            gap: 16px;
          }

          .step-icon {
            font-size: 20px;
            width: 40px;
            height: 40px;
          }

          .step-text {
            font-size: 11px;
          }
        }

        /* Accessibility */
        @media (prefers-reduced-motion: reduce) {
          .pulse,
          .spinner-ring,
          .stepPulse {
            animation: none;
          }
        }
      `}</style>
    </div>
  );
};

export default LoadingScreen;