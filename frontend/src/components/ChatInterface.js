import React, { useState, useEffect, useRef } from 'react';
import chatService from '../services/chatService';
import quantumService from '../services/quantumService';
import toast from 'react-hot-toast';

const ChatInterface = ({ user, quantumStatus }) => {
  const [contacts, setContacts] = useState([]);
  const [activeContact, setActiveContact] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [securityLevel, setSecurityLevel] = useState('L2');
  const [isConnected, setIsConnected] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef(null);

  const securityLevels = quantumService.getSecurityLevelInfo();

  // Initialize chat service and load demo contacts
  useEffect(() => {
    if (user) {
      initializeChat();
      loadDemoContacts();
    }

    return () => {
      chatService.disconnect();
    };
  }, [user]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeChat = async () => {
    try {
      // Connect to WebSocket
      await chatService.connect(user.email);
      setIsConnected(true);

      // Set up message handlers
      chatService.onMessage('encrypted_chat_message', handleIncomingMessage);
      chatService.onMessage('message_sent', handleMessageSent);
      chatService.onMessage('connection_error', handleConnectionError);

      toast.success('Connected to quantum chat network');
    } catch (error) {
      console.error('Chat initialization failed:', error);
      toast.error('Failed to connect to chat network');
      setIsConnected(false);
    }
  };

  const loadDemoContacts = () => {
    const demoContacts = chatService.getDemoContacts();
    // Filter out current user
    const filteredContacts = demoContacts.filter(contact => contact.email !== user.email);
    setContacts(filteredContacts);
    
    // Set first contact as active by default
    if (filteredContacts.length > 0) {
      setActiveContact(filteredContacts[0]);
    }
  };

  const handleIncomingMessage = (messageData) => {
    console.log('Incoming message:', messageData);
    
    const newMsg = {
      id: `msg_${Date.now()}`,
      sender: messageData.sender,
      content: messageData.message,
      timestamp: new Date(messageData.timestamp),
      securityLevel: messageData.security_level,
      type: 'received',
      encrypted: messageData.encrypted
    };

    setMessages(prev => [...prev, newMsg]);
    
    // Show toast notification if message is from non-active contact
    if (activeContact && messageData.sender !== activeContact.id) {
      toast.success(`New quantum message from ${messageData.sender}`);
    }
  };

  const handleMessageSent = (data) => {
    console.log('Message sent confirmation:', data);
    // Message already added to UI optimistically
  };

  const handleConnectionError = (error) => {
    console.error('Chat connection error:', error);
    setIsConnected(false);
    toast.error('Chat connection lost. Attempting to reconnect...');
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !activeContact || !isConnected || isSending) {
      return;
    }

    setIsSending(true);

    try {
      // Add message to UI optimistically
      const optimisticMessage = {
        id: `msg_${Date.now()}`,
        sender: user.email,
        content: newMessage.trim(),
        timestamp: new Date(),
        securityLevel: securityLevel,
        type: 'sent',
        encrypted: securityLevel !== 'L4',
        status: 'sending'
      };

      setMessages(prev => [...prev, optimisticMessage]);
      
      // Send via WebSocket
      await chatService.sendMessage(activeContact.id, newMessage.trim(), securityLevel);
      
      // Update message status
      setMessages(prev => prev.map(msg => 
        msg.id === optimisticMessage.id 
          ? { ...msg, status: 'sent' }
          : msg
      ));

      setNewMessage('');
      
      // Success feedback
      toast.success(`Message encrypted with ${securityLevel} and sent`);

    } catch (error) {
      console.error('Send message error:', error);
      toast.error('Failed to send message');
      
      // Remove failed message from UI
      setMessages(prev => prev.filter(msg => msg.status !== 'sending'));
    } finally {
      setIsSending(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const renderMessage = (message) => {
    const levelInfo = securityLevels[message.securityLevel] || securityLevels.L2;
    const isOwnMessage = message.sender === user.email;

    return (
      <div 
        key={message.id} 
        className={`message ${isOwnMessage ? 'own-message' : 'other-message'}`}
        data-testid={`chat-message-${message.id}`}
      >
        <div className="message-content">
          <div className="message-header">
            {!isOwnMessage && (
              <span className="message-sender">
                {contacts.find(c => c.id === message.sender)?.name || message.sender}
              </span>
            )}
            <div className="message-meta">
              {message.encrypted && (
                <span 
                  className={`security-badge level-${message.securityLevel.toLowerCase()}`}
                  title={`${levelInfo.name}: ${levelInfo.description}`}
                >
                  {levelInfo.icon} {message.securityLevel}
                </span>
              )}
              <span className="message-time">
                {formatTimestamp(message.timestamp)}
              </span>
              {message.status === 'sending' && (
                <span className="message-status">⏳</span>
              )}
              {message.status === 'sent' && (
                <span className="message-status">✓</span>
              )}
            </div>
          </div>
          <div className="message-text">{message.content}</div>
          {message.encrypted && (
            <div className="encryption-indicator">
              <span className="encryption-icon">🔐</span>
              <span className="encryption-text">
                Quantum encrypted via KME
              </span>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="chat-interface" data-testid="chat-interface">
      {/* Chat Header */}
      <div className="chat-header">
        <div className="chat-title">
          <h2>Quantum Secure Chat</h2>
          <div className="connection-status">
            <div className={`connection-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
              <span className="status-dot"></span>
              <span className="status-text">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>

        {/* Security Level Selector for Chat */}
        <div className="chat-security-selector">
          <label className="security-label">Chat Security:</label>
          <select 
            value={securityLevel} 
            onChange={(e) => setSecurityLevel(e.target.value)}
            className="security-select"
            data-testid="chat-security-selector"
          >
            <option value="L1">L1 - Quantum OTP</option>
            <option value="L2">L2 - Quantum AES (Recommended)</option>
            <option value="L3">L3 - Post-Quantum</option>
            <option value="L4">L4 - Standard TLS</option>
          </select>
        </div>
      </div>

      <div className="chat-body">
        {/* Contact List */}
        <div className="contact-list">
          <h3>Contacts</h3>
          {contacts.map(contact => (
            <div 
              key={contact.id}
              className={`contact-item ${activeContact?.id === contact.id ? 'active' : ''}`}
              onClick={() => setActiveContact(contact)}
              data-testid={`contact-${contact.email}`}
            >
              <div className="contact-avatar">{contact.avatar}</div>
              <div className="contact-info">
                <div className="contact-name">{contact.name}</div>
                <div className="contact-status">{contact.status}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Messages Area */}
        <div className="messages-container">
          {activeContact ? (
            <>
              <div className="messages-header">
                <h3>Chat with {activeContact.name}</h3>
                <div className="encryption-info">
                  <span className="quantum-indicator">Ψ</span>
                  Quantum Encrypted Communication
                </div>
              </div>
              
              <div className="messages-list" data-testid="messages-list">
                {messages.length === 0 ? (
                  <div className="empty-messages">
                    <div className="empty-icon">💬</div>
                    <p>Start a quantum-secure conversation</p>
                    <small>Messages are encrypted with {securityLevels[securityLevel]?.name}</small>
                  </div>
                ) : (
                  messages.map(renderMessage)
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="message-input-container">
                <div className="message-input-wrapper">
                  <textarea
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={`Send a ${securityLevels[securityLevel]?.name} encrypted message...`}
                    className="message-input"
                    data-testid="message-input"
                    disabled={!isConnected || isSending}
                    rows="1"
                  />
                  <button
                    onClick={sendMessage}
                    className={`send-button ${(!newMessage.trim() || !isConnected || isSending) ? 'disabled' : ''}`}
                    disabled={!newMessage.trim() || !isConnected || isSending}
                    data-testid="send-message-button"
                  >
                    {isSending ? '⏳' : '🚀'}
                  </button>
                </div>
                <div className="input-info">
                  <span className="encryption-level">
                    🔐 {securityLevels[securityLevel]?.name}
                  </span>
                  <span className="key-consumption">
                    Key: {securityLevels[securityLevel]?.keyConsumption}
                  </span>
                </div>
              </div>
            </>
          ) : (
            <div className="no-contact-selected">
              <div className="no-contact-icon">👥</div>
              <h3>Select a Contact</h3>
              <p>Choose a contact from the list to start a quantum-secure conversation</p>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .chat-interface {
          background: white;
          border-radius: 12px;
          box-shadow: var(--shadow-medium);
          overflow: hidden;
          height: 600px;
          display: flex;
          flex-direction: column;
        }

        .chat-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          background: linear-gradient(135deg, var(--primary-blue) 0%, var(--quantum-cyan) 100%);
          color: white;
        }

        .chat-title h2 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
        }

        .connection-status {
          margin-top: 4px;
        }

        .connection-indicator {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }

        .connection-indicator.connected .status-dot {
          background-color: var(--success-green);
          animation: pulse 2s infinite;
        }

        .connection-indicator.disconnected .status-dot {
          background-color: var(--error-red);
        }

        .chat-security-selector {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .security-label {
          font-size: 14px;
          font-weight: 500;
        }

        .security-select {
          background: white;
          color: var(--text-primary);
          border: none;
          border-radius: 8px;
          padding: 6px 12px;
          font-size: 13px;
          cursor: pointer;
        }

        .chat-body {
          flex: 1;
          display: flex;
          min-height: 0;
        }

        .contact-list {
          width: 250px;
          background: var(--background-secondary);
          border-right: 1px solid var(--border-light);
          padding: 16px;
          overflow-y: auto;
        }

        .contact-list h3 {
          margin: 0 0 12px 0;
          font-size: 14px;
          color: var(--text-secondary);
          text-transform: uppercase;
          font-weight: 600;
        }

        .contact-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
          margin-bottom: 8px;
        }

        .contact-item:hover {
          background: var(--primary-blue-light);
        }

        .contact-item.active {
          background: var(--primary-blue);
          color: white;
        }

        .contact-avatar {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: var(--quantum-cyan);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 14px;
        }

        .contact-info {
          flex: 1;
        }

        .contact-name {
          font-size: 14px;
          font-weight: 500;
          margin-bottom: 2px;
        }

        .contact-status {
          font-size: 12px;
          opacity: 0.8;
        }

        .messages-container {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-width: 0;
        }

        .messages-header {
          padding: 16px 20px;
          border-bottom: 1px solid var(--border-light);
          background: white;
        }

        .messages-header h3 {
          margin: 0 0 4px 0;
          font-size: 16px;
          color: var(--text-primary);
        }

        .encryption-info {
          font-size: 12px;
          color: var(--quantum-cyan);
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .quantum-indicator {
          font-weight: bold;
          font-size: 14px;
        }

        .messages-list {
          flex: 1;
          overflow-y: auto;
          padding: 16px 20px;
          background: var(--background-tertiary);
        }

        .message {
          margin-bottom: 16px;
        }

        .message.own-message {
          display: flex;
          justify-content: flex-end;
        }

        .message.other-message {
          display: flex;
          justify-content: flex-start;
        }

        .message-content {
          max-width: 70%;
          background: white;
          border-radius: 12px;
          padding: 12px 16px;
          box-shadow: var(--shadow-light);
        }

        .own-message .message-content {
          background: var(--primary-blue);
          color: white;
        }

        .message-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 6px;
        }

        .message-sender {
          font-size: 12px;
          font-weight: 600;
          color: var(--text-secondary);
        }

        .own-message .message-sender {
          color: rgba(255, 255, 255, 0.8);
        }

        .message-meta {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 11px;
        }

        .security-badge {
          padding: 2px 6px;
          border-radius: 6px;
          font-size: 10px;
          font-weight: 600;
        }

        .security-badge.level-l1 {
          background: var(--quantum-cyan-light);
          color: var(--quantum-cyan-dark);
        }

        .security-badge.level-l2 {
          background: var(--primary-blue-light);
          color: var(--primary-blue-dark);
        }

        .security-badge.level-l3 {
          background: var(--secondary-green-light);
          color: var(--secondary-green-dark);
        }

        .message-time {
          color: var(--text-hint);
        }

        .own-message .message-time {
          color: rgba(255, 255, 255, 0.7);
        }

        .message-status {
          color: var(--success-green);
        }

        .message-text {
          font-size: 14px;
          line-height: 1.4;
          word-wrap: break-word;
        }

        .encryption-indicator {
          display: flex;
          align-items: center;
          gap: 4px;
          margin-top: 6px;
          padding-top: 6px;
          border-top: 1px solid rgba(0,0,0,0.1);
          font-size: 11px;
          opacity: 0.8;
        }

        .own-message .encryption-indicator {
          border-top-color: rgba(255,255,255,0.2);
        }

        .empty-messages, .no-contact-selected {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          color: var(--text-secondary);
        }

        .empty-icon, .no-contact-icon {
          font-size: 48px;
          margin-bottom: 16px;
        }

        .message-input-container {
          padding: 16px 20px;
          background: white;
          border-top: 1px solid var(--border-light);
        }

        .message-input-wrapper {
          display: flex;
          gap: 12px;
          align-items: flex-end;
        }

        .message-input {
          flex: 1;
          border: 2px solid var(--border-light);
          border-radius: 20px;
          padding: 12px 16px;
          font-size: 14px;
          font-family: inherit;
          resize: none;
          max-height: 100px;
          min-height: 20px;
          outline: none;
          transition: border-color 0.2s ease;
        }

        .message-input:focus {
          border-color: var(--primary-blue);
        }

        .send-button {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          border: none;
          background: var(--primary-blue);
          color: white;
          cursor: pointer;
          font-size: 16px;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .send-button:hover:not(.disabled) {
          background: var(--primary-blue-dark);
          transform: scale(1.05);
        }

        .send-button.disabled {
          background: var(--text-hint);
          cursor: not-allowed;
          transform: none;
        }

        .input-info {
          display: flex;
          justify-content: space-between;
          margin-top: 8px;
          font-size: 11px;
          color: var(--text-secondary);
        }

        .encryption-level {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .chat-interface {
            height: 500px;
          }

          .chat-header {
            flex-direction: column;
            gap: 8px;
            align-items: stretch;
          }

          .contact-list {
            width: 200px;
          }

          .message-content {
            max-width: 85%;
          }
        }
      `}</style>
    </div>
  );
};

export default ChatInterface;
