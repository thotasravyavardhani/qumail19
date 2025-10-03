import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Tab, 
  Tabs, 
  Paper, 
  Drawer, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText,
  Typography,
  IconButton,
  Badge,
  Tooltip,
  Fab,
  Slide,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Email as EmailIcon,
  Chat as ChatIcon,
  Call as CallIcon,
  Inbox as InboxIcon,
  Send as SendIcon,
  Security as SecurityIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Menu as MenuIcon,
  Close as CloseIcon
} from '@mui/icons-material';

// Import the existing components
import EmailInterface from './EmailInterface';
import ChatInterface from './ChatInterface';
import CallInterface from './CallInterface';
import PQCFileDemo from './PQCFileDemo';

const Dashboard = ({ user, quantumStatus, onRefreshStatus }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeFolder, setActiveFolder] = useState('Inbox');
  const [activeContact, setActiveContact] = useState(null);
  const [showFloatingAction, setShowFloatingAction] = useState(false);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // Auto-close sidebar on mobile
  useEffect(() => {
    setSidebarOpen(!isMobile);
  }, [isMobile]);

  // Tab configuration with Gmail/WhatsApp theming
  const tabs = [
    {
      label: 'Email',
      icon: <EmailIcon />,
      color: '#4285F4', // Gmail Blue
      component: EmailInterface,
      folders: ['Inbox', 'Sent', 'Drafts', 'Quantum Vault', 'Spam', 'Trash']
    },
    {
      label: 'Chats',
      icon: <ChatIcon />,
      color: '#25D366', // WhatsApp Green
      component: ChatInterface,
      contacts: true
    },
    {
      label: 'Calls',
      icon: <CallIcon />,
      color: '#25D366', // WhatsApp Green  
      component: CallInterface,
      contacts: true
    }
  ];

  const currentTab = tabs[activeTab];

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    // Reset sidebar state when switching tabs
    if (newValue === 0) { // Email
      setActiveFolder('Inbox');
    } else { // Chat/Calls
      setActiveContact(null);
    }
  };

  const renderSidebar = () => {
    if (activeTab === 0) {
      // Email Folders (Gmail style)
      return (
        <List sx={{ p: 0 }}>
          <ListItem sx={{ py: 2, px: 3, borderBottom: '1px solid #e0e0e0' }}>
            <Typography variant="h6" sx={{ color: currentTab.color, fontWeight: 600 }}>
              📧 Email Folders
            </Typography>
          </ListItem>
          
          {currentTab.folders.map((folder) => (
            <ListItemButton
              key={folder}
              selected={activeFolder === folder}
              onClick={() => setActiveFolder(folder)}
              sx={{
                py: 1.5,
                px: 3,
                '&.Mui-selected': {
                  backgroundColor: `${currentTab.color}15`,
                  borderRight: `3px solid ${currentTab.color}`,
                  '& .MuiListItemText-primary': {
                    color: currentTab.color,
                    fontWeight: 600
                  }
                }
              }}
            >
              <ListItemIcon sx={{ minWidth: 32 }}>
                {folder === 'Inbox' && <InboxIcon />}
                {folder === 'Sent' && <SendIcon />}
                {folder === 'Drafts' && '📝'}
                {folder === 'Quantum Vault' && <SecurityIcon />}
                {folder === 'Spam' && '🚫'}
                {folder === 'Trash' && '🗑️'}
              </ListItemIcon>
              <ListItemText 
                primary={folder}
                primaryTypographyProps={{
                  fontSize: '14px',
                  fontWeight: activeFolder === folder ? 600 : 400
                }}
              />
              {folder === 'Inbox' && (
                <Badge badgeContent={3} color="primary" variant="dot" />
              )}
            </ListItemButton>
          ))}

          {/* Refresh Button */}
          <ListItem sx={{ px: 3, pt: 2 }}>
            <IconButton
              onClick={onRefreshStatus}
              size="small"
              sx={{ 
                backgroundColor: `${currentTab.color}10`,
                color: currentTab.color,
                '&:hover': { backgroundColor: `${currentTab.color}20` }
              }}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
            <Typography variant="caption" sx={{ ml: 1, color: 'text.secondary' }}>
              Refresh
            </Typography>
          </ListItem>
        </List>
      );
    } else {
      // Contacts List (WhatsApp style)
      const demoContacts = [
        { id: 'alice', name: 'Alice Smith', status: 'QKD Active Ψ', avatar: '👩', unread: 2 },
        { id: 'bob', name: 'Bob Johnson', status: 'Online', avatar: '👨', unread: 0 },
        { id: 'charlie', name: 'Charlie Brown', status: 'Last seen 1h ago', avatar: '🧑', unread: 1 },
        { id: 'diana', name: 'Diana Prince', status: 'QKD Active Ψ', avatar: '👩‍💼', unread: 0 },
      ];

      return (
        <List sx={{ p: 0 }}>
          <ListItem sx={{ py: 2, px: 3, borderBottom: '1px solid #e0e0e0' }}>
            <Typography variant="h6" sx={{ color: currentTab.color, fontWeight: 600 }}>
              {activeTab === 1 ? '💬 Contacts' : '📞 Contacts'}
            </Typography>
          </ListItem>
          
          {demoContacts.map((contact) => (
            <ListItemButton
              key={contact.id}
              selected={activeContact?.id === contact.id}
              onClick={() => setActiveContact(contact)}
              sx={{
                py: 2,
                px: 3,
                '&.Mui-selected': {
                  backgroundColor: `${currentTab.color}15`,
                  borderRight: `3px solid ${currentTab.color}`
                }
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                <Box
                  sx={{
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    backgroundColor: currentTab.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '16px'
                  }}
                >
                  {contact.avatar}
                </Box>
              </ListItemIcon>
              <ListItemText
                primary={contact.name}
                secondary={contact.status}
                primaryTypographyProps={{
                  fontSize: '14px',
                  fontWeight: 500
                }}
                secondaryTypographyProps={{
                  fontSize: '12px',
                  color: contact.status.includes('QKD') ? '#00BCD4' : 'text.secondary'
                }}
              />
              {contact.unread > 0 && (
                <Badge badgeContent={contact.unread} color="primary" />
              )}
            </ListItemButton>
          ))}
        </List>
      );
    }
  };

  const renderMainContent = () => {
    const ComponentToRender = currentTab.component;
    
    return (
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        {/* Content Header */}
        <Paper 
          elevation={1}
          sx={{ 
            p: 2, 
            backgroundColor: 'white',
            borderRadius: 0,
            borderBottom: '1px solid #e0e0e0'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {isMobile && (
              <IconButton onClick={() => setSidebarOpen(true)}>
                <MenuIcon />
              </IconButton>
            )}
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {React.cloneElement(currentTab.icon, { 
                sx: { color: currentTab.color, fontSize: '20px' } 
              })}
              <Typography variant="h6" sx={{ color: currentTab.color, fontWeight: 600 }}>
                {currentTab.label}
              </Typography>
            </Box>

            {/* Quantum Security Indicator */}
            <Box sx={{ 
              ml: 'auto',
              display: 'flex', 
              alignItems: 'center', 
              gap: 1,
              backgroundColor: quantumStatus.kme_connected ? '#E0F2F1' : '#FFEBEE',
              color: quantumStatus.kme_connected ? '#00695C' : '#C62828',
              px: 2,
              py: 0.5,
              borderRadius: '16px',
              fontSize: '12px',
              fontWeight: 600
            }}>
              <span style={{ fontSize: '14px' }}>
                {quantumStatus.kme_connected ? 'Ψ' : '⚠️'}
              </span>
              {quantumStatus.kme_connected ? 'Quantum Secured' : 'Not Secured'}
            </Box>
          </Box>
        </Paper>

        {/* Main Content Area */}
        <Box sx={{ flex: 1, overflow: 'hidden' }}>
          <ComponentToRender
            user={user}
            quantumStatus={quantumStatus}
            onRefreshStatus={onRefreshStatus}
            activeFolder={activeFolder}
            activeContact={activeContact}
          />
        </Box>
      </Box>
    );
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Main Tab Navigation */}
      <Paper 
        elevation={2}
        sx={{ 
          backgroundColor: 'white',
          borderRadius: 0,
          zIndex: 1
        }}
      >
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            '& .MuiTab-root': {
              minHeight: 64,
              fontSize: '14px',
              fontWeight: 600,
              textTransform: 'none'
            },
            '& .MuiTabs-indicator': {
              height: 3,
              backgroundColor: currentTab.color
            }
          }}
        >
          {tabs.map((tab, index) => (
            <Tab
              key={index}
              icon={React.cloneElement(tab.icon, { 
                sx: { 
                  fontSize: '20px',
                  color: activeTab === index ? tab.color : 'text.secondary'
                } 
              })}
              label={tab.label}
              sx={{
                color: activeTab === index ? tab.color : 'text.secondary',
                '&.Mui-selected': {
                  color: tab.color
                }
              }}
            />
          ))}
        </Tabs>
      </Paper>

      {/* Main Content Area */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Sidebar */}
        <Drawer
          variant={isMobile ? 'temporary' : 'persistent'}
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          sx={{
            width: 280,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: 280,
              boxSizing: 'border-box',
              position: 'relative',
              backgroundColor: '#f8f9fa',
              borderRight: '1px solid #e0e0e0'
            }
          }}
        >
          {isMobile && (
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'flex-end' }}>
              <IconButton onClick={() => setSidebarOpen(false)}>
                <CloseIcon />
              </IconButton>
            </Box>
          )}
          {renderSidebar()}
        </Drawer>

        {/* Main Content */}
        {renderMainContent()}
      </Box>

      {/* Floating Action Button */}
      <Slide direction="up" in={showFloatingAction} mountOnEnter unmountOnExit>
        <Fab
          color="primary"
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            backgroundColor: currentTab.color,
            '&:hover': {
              backgroundColor: currentTab.color,
              filter: 'brightness(0.9)'
            }
          }}
        >
          <AddIcon />
        </Fab>
      </Slide>

      {/* PQC Demo Panel (can be toggled) */}
      {quantumStatus.security_level === 'L3' && (
        <Box sx={{ 
          position: 'fixed', 
          bottom: 24, 
          left: 24,
          zIndex: 1000
        }}>
          <PQCFileDemo />
        </Box>
      )}
    </Box>
  );
};

export default Dashboard;
