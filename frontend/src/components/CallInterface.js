import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Button,
  Badge,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Avatar,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  Call as CallIcon,
  VideoCall as VideoCallIcon,
  CallEnd as CallEndIcon,
  Mic as MicIcon,
  MicOff as MicOffIcon,
  Videocam as VideocamIcon,
  VideocamOff as VideocamOffIcon,
  History as HistoryIcon,
  Person as PersonIcon
} from '@mui/icons-material';

const CallInterface = ({ user, quantumStatus, activeContact }) => {
  const [callHistory, setCallHistory] = useState([]);
  const [activeCall, setActiveCall] = useState(null);
  const [callTimer, setCallTimer] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOn, setIsVideoOn] = useState(true);

  // Demo call history
  useEffect(() => {
    const demoHistory = [
      {
        id: 'call_1',
        contactName: 'Alice Smith',
        contactId: 'alice',
        type: 'outgoing',
        callType: 'video',
        duration: 245,
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
        quantumSecured: true,
        status: 'completed'
      },
      {
        id: 'call_2',
        contactName: 'Bob Johnson',
        contactId: 'bob',
        type: 'incoming',
        callType: 'audio',
        duration: 128,
        timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000),
        quantumSecured: true,
        status: 'completed'
      },
      {
        id: 'call_3',
        contactName: 'Charlie Brown',
        contactId: 'charlie',
        type: 'missed',
        callType: 'audio',
        duration: 0,
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
        quantumSecured: false,
        status: 'missed'
      }
    ];
    setCallHistory(demoHistory);
  }, []);

  // Call timer effect
  useEffect(() => {
    let interval;
    if (activeCall) {
      interval = setInterval(() => {
        setCallTimer(prev => prev + 1);
      }, 1000);
    } else {
      setCallTimer(0);
    }
    return () => clearInterval(interval);
  }, [activeCall]);

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatTimestamp = (date) => {
    const now = new Date();
    const diff = now - date;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  const initiateCall = (contactId, callType) => {
    const contact = activeContact || { id: contactId, name: `Contact ${contactId}` };
    
    setActiveCall({
      contactId: contact.id,
      contactName: contact.name,
      callType,
      startTime: new Date(),
      quantumSecured: quantumStatus.kme_connected
    });

    // Add to history
    const newCall = {
      id: `call_${Date.now()}`,
      contactName: contact.name,
      contactId: contact.id,
      type: 'outgoing',
      callType,
      duration: 0,
      timestamp: new Date(),
      quantumSecured: quantumStatus.kme_connected,
      status: 'active'
    };
    setCallHistory(prev => [newCall, ...prev]);
  };

  const endCall = () => {
    if (activeCall) {
      // Update call history with final duration
      setCallHistory(prev => 
        prev.map(call => 
          call.status === 'active' 
            ? { ...call, duration: callTimer, status: 'completed' }
            : call
        )
      );
    }
    setActiveCall(null);
    setCallTimer(0);
    setIsMuted(false);
    setIsVideoOn(true);
  };

  const renderCallHistory = () => (
    <Paper elevation={1} sx={{ mt: 2 }}>
      <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <HistoryIcon />
          Recent Calls
        </Typography>
      </Box>
      
      <List>
        {callHistory.map((call) => (
          <ListItem key={call.id} divider>
            <ListItemIcon>
              <Avatar sx={{ 
                width: 32, 
                height: 32, 
                backgroundColor: call.type === 'missed' ? '#F44336' : '#25D366' 
              }}>
                {call.callType === 'video' ? <VideoCallIcon fontSize="small" /> : <CallIcon fontSize="small" />}
              </Avatar>
            </ListItemIcon>
            
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" fontWeight={500}>
                    {call.contactName}
                  </Typography>
                  {call.quantumSecured && (
                    <Chip
                      label="Ψ"
                      size="small"
                      sx={{
                        minWidth: 24,
                        height: 20,
                        backgroundColor: '#E0F2F1',
                        color: '#00695C',
                        fontSize: '10px',
                        fontWeight: 'bold'
                      }}
                    />
                  )}
                </Box>
              }
              secondary={
                <Typography variant="caption" color="text.secondary">
                  {call.type} • {formatTimestamp(call.timestamp)}
                  {call.duration > 0 && ` • ${formatDuration(call.duration)}`}
                </Typography>
              }
            />
            
            <IconButton
              onClick={() => initiateCall(call.contactId, call.callType)}
              sx={{ color: '#25D366' }}
            >
              {call.callType === 'video' ? <VideoCallIcon /> : <CallIcon />}
            </IconButton>
          </ListItem>
        ))}
      </List>
    </Paper>
  );

  const renderActiveCall = () => (
    <Dialog
      open={!!activeCall}
      fullScreen
      PaperProps={{
        sx: {
          backgroundColor: '#1a1a1a',
          color: 'white'
        }
      }}
    >
      <DialogContent sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center',
        textAlign: 'center',
        p: 4
      }}>
        {/* Contact Info */}
        <Avatar sx={{ width: 120, height: 120, mb: 3, fontSize: '48px' }}>
          {activeCall?.contactName.charAt(0)}
        </Avatar>
        
        <Typography variant="h4" gutterBottom>
          {activeCall?.contactName}
        </Typography>
        
        {/* Security Status */}
        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          mb: 2,
          px: 3,
          py: 1,
          backgroundColor: activeCall?.quantumSecured ? '#1B5E20' : '#B71C1C',
          borderRadius: '20px'
        }}>
          <Typography variant="body2" fontWeight="bold">
            {activeCall?.quantumSecured ? '🔒 SRTP Quantum Secured Ψ' : '⚠️ Standard Call'}
          </Typography>
        </Box>
        
        {/* Call Duration */}
        <Typography variant="h5" sx={{ mb: 4, fontFamily: 'monospace' }}>
          {formatDuration(callTimer)}
        </Typography>
        
        {/* Video Area */}
        {activeCall?.callType === 'video' && (
          <Box sx={{
            width: '100%',
            maxWidth: 400,
            height: 300,
            backgroundColor: '#333',
            borderRadius: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mb: 4
          }}>
            <Typography variant="h6" color="text.secondary">
              📹 Video Active
            </Typography>
          </Box>
        )}
      </DialogContent>
      
      {/* Call Controls */}
      <DialogActions sx={{ 
        justifyContent: 'center', 
        gap: 3,
        pb: 4 
      }}>
        <IconButton
          onClick={() => setIsMuted(!isMuted)}
          sx={{
            width: 60,
            height: 60,
            backgroundColor: isMuted ? '#F44336' : '#4CAF50',
            color: 'white',
            '&:hover': {
              backgroundColor: isMuted ? '#D32F2F' : '#388E3C'
            }
          }}
        >
          {isMuted ? <MicOffIcon /> : <MicIcon />}
        </IconButton>
        
        {activeCall?.callType === 'video' && (
          <IconButton
            onClick={() => setIsVideoOn(!isVideoOn)}
            sx={{
              width: 60,
              height: 60,
              backgroundColor: isVideoOn ? '#4CAF50' : '#F44336',
              color: 'white',
              '&:hover': {
                backgroundColor: isVideoOn ? '#388E3C' : '#D32F2F'
              }
            }}
          >
            {isVideoOn ? <VideocamIcon /> : <VideocamOffIcon />}
          </IconButton>
        )}
        
        <IconButton
          onClick={endCall}
          sx={{
            width: 70,
            height: 70,
            backgroundColor: '#F44336',
            color: 'white',
            '&:hover': {
              backgroundColor: '#D32F2F'
            }
          }}
        >
          <CallEndIcon />
        </IconButton>
      </DialogActions>
    </Dialog>
  );

  const renderQuickCallPanel = () => (
    <Paper elevation={1} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <CallIcon />
        Quick Call
      </Typography>
      
      {activeContact ? (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Avatar sx={{ backgroundColor: '#25D366' }}>
                {activeContact.name.charAt(0)}
              </Avatar>
              <Box>
                <Typography variant="subtitle1" fontWeight={500}>
                  {activeContact.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  QKD Status: {quantumStatus.kme_connected ? 'Active Ψ' : 'Not Connected'}
                </Typography>
              </Box>
            </Box>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<CallIcon />}
                  onClick={() => initiateCall(activeContact.id, 'audio')}
                  sx={{ backgroundColor: '#25D366', '&:hover': { backgroundColor: '#1DA851' } }}
                >
                  Audio Call
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<VideoCallIcon />}
                  onClick={() => initiateCall(activeContact.id, 'video')}
                  sx={{ backgroundColor: '#4285F4', '&:hover': { backgroundColor: '#3367D6' } }}
                >
                  Video Call
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      ) : (
        <Typography color="text.secondary" textAlign="center" py={2}>
          Select a contact from the sidebar to make a call
        </Typography>
      )}
    </Paper>
  );

  return (
    <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      {/* Quantum Status Info */}
      <Paper elevation={1} sx={{ p: 2, mb: 3, backgroundColor: '#f8f9fa' }}>
        <Typography variant="h6" gutterBottom>
          📡 Quantum Call Status
        </Typography>
        <Box sx={{ display: 'flex', gap: 3 }}>
          <Chip
            label={quantumStatus.kme_connected ? 'KME Connected' : 'KME Disconnected'}
            color={quantumStatus.kme_connected ? 'success' : 'error'}
            variant="outlined"
          />
          <Chip
            label={`Security: ${quantumStatus.security_level}`}
            color="primary"
            variant="outlined"
          />
          <Chip
            label="SRTP Ready"
            color="info"
            variant="outlined"
          />
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
          Calls are secured with quantum-derived SRTP keys when KME is connected
        </Typography>
      </Paper>

      {/* Quick Call Panel */}
      {renderQuickCallPanel()}

      {/* Call History */}
      {renderCallHistory()}

      {/* Active Call Dialog */}
      {renderActiveCall()}
    </Box>
  );
};

export default CallInterface;
