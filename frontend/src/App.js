import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import toast, { Toaster } from 'react-hot-toast';

// Import components
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import QuantumStatusBar from './components/QuantumStatusBar';
import LoadingScreen from './components/LoadingScreen';

// Import services
import authService from './services/authService';
import quantumService from './services/quantumService';

import './App.css';

function App() {
  // Authentication State
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  // Quantum Status State
  const [quantumStatus, setQuantumStatus] = useState({
    status: 'initializing',
    kme_connected: false,
    security_level: 'L2',
    heartbeat_enabled: false,
    success_rate: 0,
    uptime_seconds: 0
  });

  // Initialize app and check authentication
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      setIsLoading(true);
      
      // Check if user is already logged in (token in localStorage)
      const token = localStorage.getItem('qumail_token');
      if (token) {
        // Validate token and get user info
        try {
          authService.setToken(token);
          // In a real app, you'd validate the token with the server
          // For demo, we'll extract user info from token
          const userEmail = token; // Simple demo token is just the email
          setUser({ 
            email: userEmail, 
            display_name: userEmail.split('@')[0],
            sae_id: `qumail_${userEmail.replace('@', '_').replace('.', '_')}`
          });
          setIsAuthenticated(true);
          
          // Start quantum status monitoring
          startQuantumMonitoring();
          
        } catch (error) {
          console.error('Token validation failed:', error);
          localStorage.removeItem('qumail_token');
          authService.clearToken();
        }
      }
    } catch (error) {
      console.error('App initialization error:', error);
      toast.error('Failed to initialize application');
    } finally {
      setIsLoading(false);
    }
  };

  const startQuantumMonitoring = () => {
    // Initial status fetch
    fetchQuantumStatus();
    
    // Poll quantum status every 5 seconds
    const interval = setInterval(fetchQuantumStatus, 5000);
    
    // Cleanup interval on unmount
    return () => clearInterval(interval);
  };

  const fetchQuantumStatus = async () => {
    try {
      const status = await quantumService.getQuantumStatus();
      setQuantumStatus(status);
    } catch (error) {
      console.error('Failed to fetch quantum status:', error);
      // Update status to show error state
      setQuantumStatus(prev => ({
        ...prev,
        status: 'error',
        kme_connected: false
      }));
    }
  };

  const handleLogin = async (email, password) => {
    try {
      setIsLoading(true);
      
      const result = await authService.login(email, password);
      
      if (result.access_token) {
        // Store token and user info
        localStorage.setItem('qumail_token', result.access_token);
        authService.setToken(result.access_token);
        
        setUser(result.user);
        setIsAuthenticated(true);
        
        // Start quantum monitoring
        startQuantumMonitoring();
        
        toast.success(`Welcome back, ${result.user.display_name}!`);
      }
    } catch (error) {
      console.error('Login error:', error);
      toast.error(error.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      setIsLoading(true);
      
      // Call logout endpoint
      await authService.logout();
      
      // Clear local state
      localStorage.removeItem('qumail_token');
      authService.clearToken();
      
      setUser(null);
      setIsAuthenticated(false);
      setQuantumStatus({
        status: 'disconnected',
        kme_connected: false,
        security_level: 'L2',
        heartbeat_enabled: false,
        success_rate: 0,
        uptime_seconds: 0
      });
      
      toast.success('Logged out successfully');
      
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Logout failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSecurityLevelChange = async (newLevel) => {
    try {
      await quantumService.setSecurityLevel(newLevel);
      
      // Update local state
      setQuantumStatus(prev => ({
        ...prev,
        security_level: newLevel
      }));
      
      toast.success(`Security level changed to ${newLevel}`);
      
      // Fetch updated status
      setTimeout(fetchQuantumStatus, 1000);
      
    } catch (error) {
      console.error('Security level change error:', error);
      toast.error('Failed to change security level');
    }
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <Router>
      <div className="App">
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
              borderRadius: '8px',
            },
          }}
        />
        
        {/* Quantum Status Bar - Always visible when authenticated */}
        {isAuthenticated && (
          <QuantumStatusBar 
            status={quantumStatus}
            onSecurityLevelChange={handleSecurityLevelChange}
            user={user}
            onLogout={handleLogout}
          />
        )}
        
        <Routes>
          <Route 
            path="/login" 
            element={
              !isAuthenticated ? (
                <LoginPage onLogin={handleLogin} />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            } 
          />
          
          <Route 
            path="/dashboard" 
            element={
              isAuthenticated ? (
                <Dashboard 
                  user={user}
                  quantumStatus={quantumStatus}
                  onRefreshStatus={fetchQuantumStatus}
                />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          
          <Route 
            path="/" 
            element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;