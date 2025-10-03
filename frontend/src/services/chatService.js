// Chat Service for QuMail Web
// Handles WebSocket connections and real-time messaging

import authService from './authService';

class ChatService {
  constructor() {
    this.wsURL = process.env.REACT_APP_WS_URL || 'ws://localhost:8001';
    this.websocket = null;
    this.isConnected = false;
    this.messageHandlers = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // Start with 1 second
  }

  // Connect to WebSocket
  connect(userId) {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${this.wsURL}/api/ws/chat/${encodeURIComponent(userId)}`;
        console.log('Connecting to WebSocket:', wsUrl);
        
        this.websocket = new WebSocket(wsUrl);

        this.websocket.onopen = () => {
          console.log('WebSocket connected successfully');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
          resolve();
        };

        this.websocket.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.websocket.onclose = (event) => {
          console.log('WebSocket connection closed:', event.code, event.reason);
          this.isConnected = false;
          
          // Attempt to reconnect if not manually closed
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect(userId);
          }
        };

        this.websocket.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        // Timeout for connection
        setTimeout(() => {
          if (!this.isConnected) {
            reject(new Error('WebSocket connection timeout'));
          }
        }, 10000);

      } catch (error) {
        console.error('WebSocket connection error:', error);
        reject(error);
      }
    });
  }

  // Attempt to reconnect
  attemptReconnect(userId) {
    this.reconnectAttempts++;
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

    setTimeout(() => {
      this.connect(userId).catch(error => {
        console.error('Reconnection failed:', error);
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          console.error('Max reconnection attempts reached');
          this.notifyConnectionError();
        }
      });
    }, this.reconnectDelay);

    // Exponential backoff
    this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
  }

  // Disconnect WebSocket
  disconnect() {
    if (this.websocket) {
      console.log('Disconnecting WebSocket...');
      this.websocket.close(1000, 'User disconnect');
      this.websocket = null;
      this.isConnected = false;
    }
  }

  // Handle incoming messages
  handleMessage(message) {
    console.log('Received WebSocket message:', message);

    // Notify registered handlers
    this.messageHandlers.forEach((handler, type) => {
      if (message.type === type || type === 'all') {
        try {
          handler(message);
        } catch (error) {
          console.error(`Handler error for message type ${type}:`, error);
        }
      }
    });
  }

  // Register message handler
  onMessage(type, handler) {
    this.messageHandlers.set(type, handler);
  }

  // Remove message handler
  offMessage(type) {
    this.messageHandlers.delete(type);
  }

  // Send chat message
  async sendMessage(contactId, message, securityLevel = 'L2') {
    if (!this.isConnected || !this.websocket) {
      throw new Error('WebSocket not connected');
    }

    const messageData = {
      type: 'chat_message',
      data: {
        contact_id: contactId,
        message: message,
        security_level: securityLevel
      }
    };

    try {
      this.websocket.send(JSON.stringify(messageData));
      console.log('Message sent:', messageData);
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  }

  // Request quantum status update
  requestQuantumStatus() {
    if (!this.isConnected || !this.websocket) {
      console.warn('Cannot request quantum status - WebSocket not connected');
      return;
    }

    const request = {
      type: 'request_quantum_status'
    };

    try {
      this.websocket.send(JSON.stringify(request));
    } catch (error) {
      console.error('Failed to request quantum status:', error);
    }
  }

  // Get connection status
  getConnectionStatus() {
    return {
      connected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      websocket: !!this.websocket
    };
  }

  // Notify connection error to handlers
  notifyConnectionError() {
    this.messageHandlers.forEach((handler, type) => {
      if (type === 'connection_error' || type === 'all') {
        try {
          handler({
            type: 'connection_error',
            message: 'Failed to establish WebSocket connection'
          });
        } catch (error) {
          console.error('Connection error handler failed:', error);
        }
      }
    });
  }

  // Demo contacts for hackathon
  getDemoContacts() {
    return [
      {
        id: 'alice@qumail.com',
        name: 'Alice Smith',
        email: 'alice@qumail.com',
        status: 'online',
        lastSeen: new Date(),
        avatar: 'A'
      },
      {
        id: 'bob@qumail.com', 
        name: 'Bob Johnson',
        email: 'bob@qumail.com',
        status: 'online',
        lastSeen: new Date(),
        avatar: 'B'
      },
      {
        id: 'demo@qumail.com',
        name: 'Demo User',
        email: 'demo@qumail.com', 
        status: 'online',
        lastSeen: new Date(),
        avatar: 'D'
      }
    ];
  }
}

// Export singleton instance
const chatService = new ChatService();
export default chatService;