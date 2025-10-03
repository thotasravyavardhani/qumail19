import React, { useState } from 'react';
import quantumService from '../services/quantumService';

const QuantumStatusBar = ({ status, onSecurityLevelChange, user, onLogout }) => {
  const [isChangingLevel, setIsChangingLevel] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const securityLevels = quantumService.getSecurityLevelInfo();
  const currentLevelInfo = securityLevels[status.security_level] || securityLevels.L2;
  const statusInfo = quantumService.formatQuantumStatus(status.status);
  const successRateInfo = quantumService.formatSuccessRate(status.success_rate);
  const uptime = quantumService.formatUptime(status.uptime_seconds);

  const handleSecurityChange = async (newLevel) => {
    if (newLevel === status.security_level) return;
    
    setIsChangingLevel(true);
    try {
      await onSecurityLevelChange(newLevel);
    } finally {
      setIsChangingLevel(false);
    }
  };

  const renderSecuritySelector = () => (
    <div className="security-selector">
      <label className="security-label">Security Level:</label>
      <div className="security-levels">
        {Object.entries(securityLevels).map(([level, info]) => (
          <button
            key={level}
            data-testid={`security-level-${level.toLowerCase()}`}
            className={`security-pill level-${level.toLowerCase()} ${
              status.security_level === level ? 'active' : ''
            } ${isChangingLevel ? 'disabled' : ''}`}
            onClick={() => handleSecurityChange(level)}
            disabled={isChangingLevel}
            title={`${info.name}: ${info.description}`}
          >
            <span className="level-icon">{info.icon}</span>
            <span className="level-text">{level}</span>
            {status.security_level === level && (
              <span className="level-active">✓</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );

  const renderKMEStatus = () => (
    <div className="kme-status-container">
      <div className={`quantum-status ${status.kme_connected ? 'connected' : 'error'}`}>
        <div className={`status-indicator ${statusInfo.pulse ? 'pulse' : ''}`}>
          <span 
            className="status-icon" 
            style={{ color: statusInfo.color }}
          >
            {statusInfo.icon}
          </span>
        </div>
        <div className="status-details">
          <div className="status-primary">{statusInfo.label}</div>
          <div className="status-secondary">
            {status.kme_connected ? (
              <span className={`success-rate ${successRateInfo.level}`}>
                {status.success_rate.toFixed(1)}% • {uptime}
              </span>
            ) : (
              'Not Connected'
            )}
          </div>
        </div>
      </div>
      
      {status.heartbeat_enabled && (
        <div className="heartbeat-indicator" data-testid="heartbeat-indicator">
          <span className="heartbeat">♥</span>
          <span className="heartbeat-text">Live</span>
        </div>
      )}
    </div>
  );

  const renderPQCStats = () => {
    if (!status.pqc_stats || status.pqc_stats.files_encrypted === 0) return null;
    
    return (
      <div className="pqc-stats" data-testid="pqc-stats">
        <span className="pqc-badge">PQC</span>
        <span className="pqc-text">
          {status.pqc_stats.files_encrypted} files • 
          {status.pqc_stats.total_size_mb?.toFixed(1)}MB
        </span>
      </div>
    );
  };

  const renderUserMenu = () => (
    <div className="user-menu-container">
      <button 
        className="user-button"
        onClick={() => setShowUserMenu(!showUserMenu)}
        data-testid="user-menu-button"
      >
        <div className="user-avatar">
          {user?.display_name?.charAt(0)?.toUpperCase() || '?'}
        </div>
        <span className="user-name">{user?.display_name || 'User'}</span>
        <span className="user-dropdown">▼</span>
      </button>
      
      {showUserMenu && (
        <div className="user-dropdown-menu" data-testid="user-dropdown-menu">
          <div className="user-info">
            <div className="user-email">{user?.email}</div>
            <div className="user-sae">SAE ID: {user?.sae_id}</div>
          </div>
          <hr className="menu-separator" />
          <button 
            className="logout-button"
            onClick={onLogout}
            data-testid="logout-button"
          >
            <span className="logout-icon">🚪</span>
            Logout
          </button>
        </div>
      )}
    </div>
  );

  return (
    <div className="quantum-status-bar" data-testid="quantum-status-bar">
      {/* Brand Logo */}
      <div className="quantum-brand-section">
        <div className="quantum-logo">
          <span className="logo-text">QuMail</span>
        </div>
      </div>

      {/* Security Level Selector */}
      <div className="security-section">
        {renderSecuritySelector()}
      </div>

      {/* KME Status & Monitoring */}
      <div className="status-section">
        {renderKMEStatus()}
        {renderPQCStats()}
      </div>

      {/* User Menu */}
      <div className="user-section">
        {renderUserMenu()}
      </div>

      <style jsx>{`
        .quantum-status-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
          border-bottom: 1px solid var(--border-light);
          padding: 8px 16px;
          box-shadow: var(--shadow-light);
          min-height: 60px;
          position: sticky;
          top: 0;
          z-index: 100;
        }

        .quantum-brand-section {
          flex-shrink: 0;
        }

        .quantum-logo {
          font-size: 20px;
          font-weight: 700;
          background: linear-gradient(135deg, var(--quantum-cyan) 0%, var(--primary-blue) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .security-section {
          flex-grow: 1;
          display: flex;
          justify-content: center;
          max-width: 600px;
        }

        .security-selector {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .security-label {
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary);
          margin-right: 8px;
        }

        .security-levels {
          display: flex;
          gap: 8px;
        }

        .security-pill {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 6px 12px;
          border: 2px solid;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          background: white;
        }

        .security-pill:hover:not(.disabled) {
          transform: translateY(-1px);
          box-shadow: var(--shadow-medium);
        }

        .security-pill.disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .security-pill.active {
          transform: scale(1.05);
          box-shadow: var(--shadow-medium);
        }

        .level-icon {
          font-size: 14px;
        }

        .level-active {
          color: var(--success-green);
          font-weight: 700;
        }

        .status-section {
          display: flex;
          align-items: center;
          gap: 16px;
          flex-shrink: 0;
        }

        .kme-status-container {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .quantum-status {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 6px 12px;
          border-radius: 16px;
          background: white;
          border: 1px solid var(--border-light);
        }

        .status-indicator {
          display: flex;
          align-items: center;
        }

        .status-icon {
          font-size: 16px;
          font-weight: bold;
        }

        .status-details {
          display: flex;
          flex-direction: column;
          line-height: 1.2;
        }

        .status-primary {
          font-size: 12px;
          font-weight: 600;
          color: var(--text-primary);
        }

        .status-secondary {
          font-size: 11px;
          color: var(--text-secondary);
        }

        .heartbeat-indicator {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 11px;
          color: var(--success-green);
        }

        .heartbeat {
          animation: heartbeat 1.5s infinite;
        }

        .pqc-stats {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 11px;
        }

        .pqc-badge {
          background: linear-gradient(135deg, #9C27B0 0%, #673AB7 100%);
          color: white;
          padding: 2px 6px;
          border-radius: 6px;
          font-weight: 600;
        }

        .user-section {
          flex-shrink: 0;
        }

        .user-menu-container {
          position: relative;
        }

        .user-button {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 6px 12px;
          background: white;
          border: 1px solid var(--border-light);
          border-radius: 20px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .user-button:hover {
          background: var(--background-secondary);
          box-shadow: var(--shadow-light);
        }

        .user-avatar {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background: var(--primary-blue);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          font-weight: 600;
        }

        .user-name {
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary);
        }

        .user-dropdown {
          font-size: 10px;
          color: var(--text-secondary);
        }

        .user-dropdown-menu {
          position: absolute;
          top: 100%;
          right: 0;
          margin-top: 4px;
          background: white;
          border: 1px solid var(--border-light);
          border-radius: 8px;
          box-shadow: var(--shadow-medium);
          min-width: 200px;
          z-index: 1000;
          animation: slideDown 0.2s ease-out;
        }

        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-8px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .user-info {
          padding: 12px 16px;
        }

        .user-email {
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary);
        }

        .user-sae {
          font-size: 12px;
          color: var(--text-secondary);
          margin-top: 2px;
        }

        .menu-separator {
          border: 0;
          border-top: 1px solid var(--border-light);
          margin: 0;
        }

        .logout-button {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 16px;
          background: none;
          border: none;
          text-align: left;
          cursor: pointer;
          font-size: 14px;
          color: var(--text-primary);
          transition: background-color 0.2s ease;
        }

        .logout-button:hover {
          background: var(--background-secondary);
        }

        .logout-icon {
          font-size: 16px;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .quantum-status-bar {
            flex-wrap: wrap;
            min-height: auto;
            padding: 8px 12px;
          }

          .security-section {
            order: 3;
            flex-basis: 100%;
            margin-top: 8px;
            justify-content: flex-start;
          }

          .security-levels {
            gap: 4px;
          }

          .security-pill {
            padding: 4px 8px;
            font-size: 11px;
          }

          .status-section {
            gap: 8px;
          }

          .user-name {
            display: none;
          }
        }
      `}</style>
    </div>
  );
};

export default QuantumStatusBar;