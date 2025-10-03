#!/usr/bin/env python3
"""
Call Module - Audio/Video Calling Interface
Implements audio and video calling functionality with quantum-secured SRTP
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QScrollArea, QListWidget, QListWidgetItem, QSplitter,
    QProgressBar, QSlider, QComboBox, QDialog, QDialogButtonBox,
    QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QPen
from datetime import datetime, timedelta

class CallHistoryItem(QFrame):
    """Individual call history item"""
    
    call_selected = pyqtSignal(str)  # call_id
    
    def __init__(self, call_data: Dict):
        super().__init__()
        self.call_data = call_data
        self.call_id = call_data.get('call_id', '')
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup call history item UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setMinimumHeight(70)
        self.setMaximumHeight(70)
        
        # Style based on call status
        call_type = self.call_data.get('type', 'missed')
        if call_type == 'missed':
            border_color = '#FF4444'
        elif call_type == 'incoming':
            border_color = '#25D366'
        else:  # outgoing
            border_color = '#4285F4'
            
        self.setStyleSheet(f"""
            CallHistoryItem {{
                border: 1px solid #E0E0E0;
                border-left: 4px solid {border_color};
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }}
            CallHistoryItem:hover {{
                background-color: #F8F9FA;
                border-color: {border_color};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Call type icon
        call_icon = "📞" if self.call_data.get('call_type') == 'audio' else "📹"
        icon_label = QLabel(call_icon)
        icon_label.setFixedSize(40, 40)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {border_color};
                color: white;
                border-radius: 20px;
                font-size: 16px;
            }}
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Call info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # Contact and status
        top_line = QHBoxLayout()
        
        contact_label = QLabel(self.call_data.get('contact_name', 'Unknown'))
        contact_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        top_line.addWidget(contact_label)
        
        # Security indicator
        if self.call_data.get('quantum_secured'):
            security_icon = QLabel("Ψ")
            security_icon.setStyleSheet("color: #61FF00; font-weight: bold; font-size: 14px;")
            security_icon.setToolTip("Quantum Secured SRTP")
            top_line.addWidget(security_icon)
            
        top_line.addStretch()
        
        # Duration or status
        duration = self.call_data.get('duration', 0)
        if duration > 0:
            minutes = duration // 60
            seconds = duration % 60
            duration_text = f"{minutes:02d}:{seconds:02d}"
        else:
            duration_text = self.call_data.get('status', 'No answer')
            
        duration_label = QLabel(duration_text)
        duration_label.setStyleSheet("color: #666; font-size: 11px;")
        top_line.addWidget(duration_label)
        
        info_layout.addLayout(top_line)
        
        # Timestamp and type
        bottom_line = QHBoxLayout()
        
        timestamp = self.call_data.get('timestamp', '')
        time_label = QLabel(self._format_time(timestamp))
        time_label.setStyleSheet("color: #666; font-size: 10px;")
        bottom_line.addWidget(time_label)
        
        bottom_line.addStretch()
        
        type_label = QLabel(f"{self.call_data.get('call_type', 'audio').title()}")
        type_label.setStyleSheet("color: #999; font-size: 10px;")
        bottom_line.addWidget(type_label)
        
        info_layout.addLayout(bottom_line)
        layout.addLayout(info_layout)
        
        # Action buttons
        action_layout = QVBoxLayout()
        
        callback_button = QPushButton("📞")
        callback_button.setFixedSize(32, 32)
        callback_button.setStyleSheet("""
            QPushButton {
                background-color: #25D366;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1DA851;
            }
        """)
        callback_button.setToolTip("Call Back")
        callback_button.clicked.connect(lambda: self.call_selected.emit(self.call_data.get('contact_id', '')))
        action_layout.addWidget(callback_button)
        
        layout.addLayout(action_layout)
        
    def _format_time(self, timestamp_str: str) -> str:
        """Format timestamp for display"""
        try:
            if not timestamp_str:
                return "Unknown"
            # Simple formatting - in real implementation would be more sophisticated
            return "2 hours ago"
        except:
            return "Unknown"

class VideoCallWidget(QWidget):
    """Video call display widget with PiP capability"""
    
    call_ended = pyqtSignal()
    
    def __init__(self, contact_name: str, is_pip: bool = False):
        super().__init__()
        self.contact_name = contact_name
        self.is_pip = is_pip
        self.call_duration = 0
        self.call_timer = QTimer()
        self.call_timer.timeout.connect(self.update_duration)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup video call UI"""
        if self.is_pip:
            self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
            self.setWindowTitle("QuMail Call - PiP")
            self.resize(320, 240)
        else:
            self.resize(800, 600)
            
        layout = QVBoxLayout(self)
        
        # Video area
        video_frame = QFrame()
        video_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-radius: 8px;
            }
        """)
        video_layout = QVBoxLayout(video_frame)
        
        # Main video (remote)
        main_video = QLabel("📹 Video Call Active")
        main_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_video.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                background-color: #333;
                border-radius: 8px;
                padding: 40px;
            }
        """)
        video_layout.addWidget(main_video)
        
        # Self video (small overlay)
        if not self.is_pip:
            self_video = QLabel("You")
            self_video.setFixedSize(120, 90)
            self_video.setStyleSheet("""
                QLabel {
                    background-color: #555;
                    color: white;
                    border: 2px solid white;
                    border-radius: 8px;
                    font-size: 12px;
                }
            """)
            self_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Position self video in corner
            overlay_layout = QHBoxLayout()
            overlay_layout.addStretch()
            overlay_layout.addWidget(self_video)
            overlay_layout.setContentsMargins(0, 0, 16, 16)
            video_layout.addLayout(overlay_layout)
            
        layout.addWidget(video_frame, 1)
        
        # Call info bar
        info_bar = QFrame()
        info_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(7, 94, 84, 0.9);
                border-radius: 6px;
                padding: 8px;
            }
        """)
        info_layout = QHBoxLayout(info_bar)
        
        # Contact name
        name_label = QLabel(f"📞 {self.contact_name}")
        name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        info_layout.addWidget(name_label)
        
        # Security indicator
        security_label = QLabel("🔒 SRTP Quantum Secured Ψ")
        security_label.setStyleSheet("""
            QLabel {
                color: #61FF00;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        info_layout.addWidget(security_label)
        
        info_layout.addStretch()
        
        # Duration
        self.duration_label = QLabel("00:00")
        self.duration_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        info_layout.addWidget(self.duration_label)
        
        layout.addWidget(info_bar)
        
        # Controls
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Mute button
        self.mute_button = QPushButton("🎤")
        self.mute_button.setFixedSize(50, 50)
        self.mute_button.setCheckable(True)
        self.mute_button.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 18px;
            }
            QPushButton:checked {
                background-color: #FF4444;
            }
        """)
        self.mute_button.setToolTip("Mute/Unmute")
        controls_layout.addWidget(self.mute_button)
        
        # Video toggle
        if not self.is_pip:
            self.video_button = QPushButton("📹")
            self.video_button.setFixedSize(50, 50)
            self.video_button.setCheckable(True)
            self.video_button.setChecked(True)
            self.video_button.setStyleSheet("""
                QPushButton {
                    background-color: #4285F4;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-size: 16px;
                }
                QPushButton:checked {
                    background-color: #FF4444;
                }
            """)
            self.video_button.setToolTip("Camera On/Off")
            controls_layout.addWidget(self.video_button)
        
        # End call button
        end_button = QPushButton("📞")
        end_button.setFixedSize(60, 60)
        end_button.setStyleSheet("""
            QPushButton {
                background-color: #FF4444;
                color: white;
                border: none;
                border-radius: 30px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #CC3333;
            }
        """)
        end_button.setToolTip("End Call")
        end_button.clicked.connect(self.end_call)
        controls_layout.addWidget(end_button)
        
        # PiP toggle (for main window)
        if not self.is_pip:
            pip_button = QPushButton("📌")
            pip_button.setFixedSize(40, 40)
            pip_button.setStyleSheet("""
                QPushButton {
                    background-color: #666;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-size: 14px;
                }
            """)
            pip_button.setToolTip("Picture in Picture")
            pip_button.clicked.connect(self.toggle_pip)
            controls_layout.addWidget(pip_button)
        
        layout.addWidget(controls_frame)
        
    def start_call(self):
        """Start the call timer"""
        self.call_timer.start(1000)
        
    def update_duration(self):
        """Update call duration"""
        self.call_duration += 1
        minutes = self.call_duration // 60
        seconds = self.call_duration % 60
        self.duration_label.setText(f"{minutes:02d}:{seconds:02d}")
        
    def toggle_pip(self):
        """Toggle picture-in-picture mode"""
        # Create PiP window
        pip_widget = VideoCallWidget(self.contact_name, is_pip=True)
        pip_widget.call_duration = self.call_duration
        pip_widget.call_timer.start(1000)
        pip_widget.show()
        
        # Hide main window
        self.hide()
        
    def end_call(self):
        """End the call"""
        self.call_timer.stop()
        self.call_ended.emit()
        self.close()

class HybridSRTPKeyManager:
    """Manages SRTP key derivation from hybrid PQC material"""
    
    def __init__(self, core):
        self.core = core
        # Import hybrid KEM client
        try:
            from ..crypto.pqc_hybrid_kem import HybridKEMClient
            self.hybrid_kem = HybridKEMClient()
        except ImportError:
            logging.error("Failed to import HybridKEMClient")
            self.hybrid_kem = None
        
    async def initiate_hybrid_handshake(self, contact_id: str, call_id: str) -> Optional[Dict]:
        """Initiate hybrid PQC handshake as caller (Client A)"""
        try:
            if not self.hybrid_kem:
                return None
                
            # Step 1: Generate our ephemeral hybrid keypair
            our_keypair = self.hybrid_kem.generate_hybrid_keypair()
            
            logging.info(f"Generated hybrid keypair for call {call_id}")
            
            return {
                'keypair_id': our_keypair['keypair_id'],
                'x25519_public_key': our_keypair['x25519_public_key'],
                'kyber_public_key': our_keypair['kyber_public_key'],
                'x25519_private_key': our_keypair['x25519_private_key'],
                'kyber_secret_key': our_keypair['kyber_secret_key'],
                'algorithm': our_keypair['algorithm'],
                'security_level': our_keypair['security_level']
            }
            
        except Exception as e:
            logging.error(f"Failed to initiate hybrid handshake: {e}")
            return None
    
    async def process_responder_keys(self, responder_keys: Dict, our_keypair: Dict, call_id: str) -> Optional[Dict]:
        """Process responder keys and perform hybrid encapsulation (Client A)"""
        try:
            if not self.hybrid_kem:
                return None
                
            # Extract responder's public keys
            remote_hybrid_public_key = {
                'x25519_public_key': responder_keys['classic_pub_key'],
                'kyber_public_key': responder_keys['pqc_pub_key']
            }
            
            # Perform hybrid encapsulation
            encapsulation_result = self.hybrid_kem.hybrid_encapsulate(remote_hybrid_public_key)
            
            # Derive SRTP keys from session key
            session_key = encapsulation_result['session_key']
            srtp_keys = self.hybrid_kem.derive_srtp_keys(session_key, call_id)
            
            logging.info(f"Hybrid encapsulation completed for call {call_id}")
            
            return {
                'encapsulation_id': encapsulation_result['encapsulation_id'],
                'pqc_ciphertext': encapsulation_result['kyber_ciphertext'],
                'classic_key_share': encapsulation_result['x25519_public_key'],
                'srtp_keys': srtp_keys,
                'session_key': session_key,
                'algorithm': encapsulation_result['algorithm']
            }
            
        except Exception as e:
            logging.error(f"Failed to process responder keys: {e}")
            return None
    
    async def process_caller_ciphertext(self, ciphertext_data: Dict, our_keypair: Dict, call_id: str) -> Optional[Dict]:
        """Process caller's ciphertext and derive session key (Client B)"""
        try:
            if not self.hybrid_kem:
                return None
                
            # Reconstruct encapsulated data format
            encapsulated_data = {
                'x25519_public_key': ciphertext_data['classic_key_share'],
                'kyber_ciphertext': ciphertext_data['pqc_ciphertext'],
                'kyber_auth_tag': 'simulated_auth_tag'  # In real implementation, this would be included
            }
            
            # Perform hybrid decapsulation
            session_key = self.hybrid_kem.hybrid_decapsulate(encapsulated_data, our_keypair)
            
            # Derive SRTP keys from session key
            srtp_keys = self.hybrid_kem.derive_srtp_keys(session_key, call_id)
            
            logging.info(f"Hybrid decapsulation completed for call {call_id}")
            
            return {
                'session_key': session_key,
                'srtp_keys': srtp_keys,
                'algorithm': 'Kyber-768+X25519-HKDF'
            }
            
        except Exception as e:
            logging.error(f"Failed to process caller ciphertext: {e}")
            return None

class CallModule(QWidget):
    """Main call module implementing audio/video calling with hybrid PQC SRTP"""
    
    status_message = pyqtSignal(str)
    
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.call_history = []
        self.active_call = None
        self.hybrid_srtp_manager = HybridSRTPKeyManager(core)
        
        # Store active handshake state
        self.active_handshakes = {}  # call_id -> handshake_state
        
        self.setup_ui()
        self.load_call_history()
        
        logging.info("Call Module initialized with hybrid PQC SRTP support")
        
    def _submit_async_call(self, call_type: str, contact_id: str = None):
        """Synchronous wrapper to safely submit async call to the running asyncio loop."""
        try:
            # CRITICAL FIX: Explicitly get the current loop and submit the task to it.
            loop = asyncio.get_event_loop()
            loop.create_task(self.start_call(call_type, contact_id))
            
        except Exception as e:
            logging.error(f"Error submitting async call: {e}") 
            QMessageBox.critical(self, "Core Error", 
                                 f"Call system initialization error: {e}")
        
    def setup_ui(self):
        """Setup the call module UI"""
        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - call history and contacts
        self.setup_call_list_panel(main_splitter)
        
        # Right panel - call controls and status
        self.setup_call_control_panel(main_splitter)
        
        # Set splitter proportions
        main_splitter.setSizes([400, 400])
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_splitter)
        
    def setup_call_list_panel(self, parent_splitter):
        """Setup call history and contacts panel"""
        list_frame = QFrame()
        list_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        list_layout = QVBoxLayout(list_frame)
        
        # Header with tabs
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("📞 Calls & Contacts")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #25D366; padding: 12px;")
        header_layout.addWidget(title_label)
        
        # Tab buttons
        tab_layout = QHBoxLayout()
        
        self.history_tab = QPushButton("Recent")
        self.history_tab.setCheckable(True)
        self.history_tab.setChecked(True)
        self.history_tab.clicked.connect(lambda: self.switch_tab('history'))
        
        self.contacts_tab = QPushButton("Contacts")
        self.contacts_tab.setCheckable(True)
        self.contacts_tab.clicked.connect(lambda: self.switch_tab('contacts'))
        
        tab_style = """
            QPushButton {
                padding: 8px 16px;
                border: none;
                background-color: #F0F2F5;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #25D366;
                color: white;
            }
        """
        
        self.history_tab.setStyleSheet(tab_style)
        self.contacts_tab.setStyleSheet(tab_style)
        
        tab_layout.addWidget(self.history_tab)
        tab_layout.addWidget(self.contacts_tab)
        tab_layout.addStretch()
        
        header_layout.addLayout(tab_layout)
        list_layout.addWidget(header_frame)
        
        # Scrollable list
        self.call_list_widget = QScrollArea()
        self.call_list_widget.setWidgetResizable(True)
        self.call_list_widget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        
        self.call_list_container = QWidget()
        self.call_list_layout = QVBoxLayout(self.call_list_container)
        self.call_list_layout.setSpacing(2)
        
        self.call_list_widget.setWidget(self.call_list_container)
        list_layout.addWidget(self.call_list_widget)
        
        parent_splitter.addWidget(list_frame)
        
    def setup_call_control_panel(self, parent_splitter):
        """Setup call controls and status panel"""
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        control_layout = QVBoxLayout(control_frame)
        
        # Status display
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        status_layout = QVBoxLayout(status_frame)
        
        # Connection status
        connection_label = QLabel("📡 WebRTC Connection Status")
        connection_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        status_layout.addWidget(connection_label)
        
        self.webrtc_status = QLabel("Ready for calls")
        self.webrtc_status.setStyleSheet("color: #25D366; font-size: 12px;")
        status_layout.addWidget(self.webrtc_status)
        
        # Quantum security status
        security_label = QLabel("🔒 Quantum SRTP Security")
        security_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        status_layout.addWidget(security_label)
        
        self.srtp_status = QLabel("Hybrid PQC ready - Kyber-768 + X25519 Ψ")
        self.srtp_status.setStyleSheet("color: #61FF00; font-size: 12px; font-weight: bold;")
        status_layout.addWidget(self.srtp_status)
        
        # Add PQC handshake status
        pqc_handshake_label = QLabel("🔐 PQC Handshake Status")
        pqc_handshake_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        status_layout.addWidget(pqc_handshake_label)
        
        self.pqc_handshake_status = QLabel("Ready for hybrid key exchange")
        self.pqc_handshake_status.setStyleSheet("color: #4285F4; font-size: 12px;")
        status_layout.addWidget(self.pqc_handshake_status)
        
        # Timer to update PQC status
        self.pqc_status_timer = QTimer()
        self.pqc_status_timer.timeout.connect(self.update_pqc_call_status)
        self.pqc_status_timer.start(2000)  # Update every 2 seconds
        
        control_layout.addWidget(status_frame)
        
        # Quick call section
        quick_call_frame = QFrame()
        quick_call_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        quick_call_layout = QVBoxLayout(quick_call_frame)
        
        quick_label = QLabel("Quick Call")
        quick_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        quick_call_layout.addWidget(quick_label)
        
        # Contact selector
        self.contact_selector = QComboBox()
        self.contact_selector.addItems([
            "Alice Smith (QKD Active Ψ)",
            "Bob Johnson (QKD Active Ψ)",
            "Charlie Brown (Standard)"
        ])
        self.contact_selector.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        quick_call_layout.addWidget(self.contact_selector)
        
        # Call buttons
        call_buttons_layout = QHBoxLayout()
        
        audio_call_button = QPushButton("📞 Audio Call")
        audio_call_button.setStyleSheet("""
            QPushButton {
                background-color: #25D366;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1DA851;
            }
        """)
        # FIXED: Use synchronous wrapper to safely submit async call
        audio_call_button.clicked.connect(lambda: self._submit_async_call('audio'))
        call_buttons_layout.addWidget(audio_call_button)
        
        video_call_button = QPushButton("📹 Video Call")
        video_call_button.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367D6;
            }
        """)
        # FIXED: Use synchronous wrapper to safely submit async call
        video_call_button.clicked.connect(lambda: self._submit_async_call('video'))
        call_buttons_layout.addWidget(video_call_button)
        
        quick_call_layout.addLayout(call_buttons_layout)
        control_layout.addWidget(quick_call_frame)
        
        # SRTP Key info
        key_info_frame = QFrame()
        key_info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(97, 255, 0, 0.1);
                border: 1px solid #61FF00;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        key_info_layout = QVBoxLayout(key_info_frame)
        
        key_title = QLabel("🔐 Quantum Key Pool Status")
        key_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        key_title.setStyleSheet("color: #61FF00;")
        key_info_layout.addWidget(key_title)
        
        self.key_pool_bar = QProgressBar()
        self.key_pool_bar.setMaximum(100)
        self.key_pool_bar.setValue(87)
        self.key_pool_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #61FF00;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #61FF00;
            }
        """)
        key_info_layout.addWidget(self.key_pool_bar)
        
        key_status_label = QLabel("Available keys: 234 | Used today: 12 | Quality: Excellent")
        key_status_label.setStyleSheet("color: #333; font-size: 10px;")
        key_info_layout.addWidget(key_status_label)
        
        control_layout.addWidget(key_info_frame)
        
        control_layout.addStretch()
        
        parent_splitter.addWidget(control_frame)
        
    def switch_tab(self, tab_name: str):
        """Switch between history and contacts tabs"""
        if tab_name == 'history':
            self.history_tab.setChecked(True)
            self.contacts_tab.setChecked(False)
            self.load_call_history()
        else:
            self.history_tab.setChecked(False)
            self.contacts_tab.setChecked(True)
            self.load_contacts()
            
    def load_call_history(self):
        """Load and display call history"""
        # Clear existing items
        while self.call_list_layout.count():
            child = self.call_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Sample call history
        sample_calls = [
            {
                'call_id': 'call_1',
                'contact_id': 'alice',
                'contact_name': 'Alice Smith',
                'type': 'outgoing',
                'call_type': 'video',
                'duration': 245,  # seconds
                'timestamp': datetime.utcnow().isoformat(),
                'quantum_secured': True,
                'status': 'completed'
            },
            {
                'call_id': 'call_2',
                'contact_id': 'bob',
                'contact_name': 'Bob Johnson',
                'type': 'incoming',
                'call_type': 'audio',
                'duration': 128,
                'timestamp': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                'quantum_secured': True,
                'status': 'completed'
            },
            {
                'call_id': 'call_3',
                'contact_id': 'charlie',
                'contact_name': 'Charlie Brown',
                'type': 'missed',
                'call_type': 'audio',
                'duration': 0,
                'timestamp': (datetime.utcnow() - timedelta(hours=3)).isoformat(),
                'quantum_secured': False,
                'status': 'missed'
            }
        ]
        
        for call_data in sample_calls:
            call_item = CallHistoryItem(call_data)
            call_item.call_selected.connect(self.initiate_callback)
            self.call_list_layout.addWidget(call_item)
            
        self.call_list_layout.addStretch()
        self.call_history = sample_calls
        
    def load_contacts(self):
        """Load and display contacts for calling"""
        # Clear existing items
        while self.call_list_layout.count():
            child = self.call_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # This would integrate with chat module contacts
        contacts_label = QLabel("Contact integration with Chat module")
        contacts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contacts_label.setStyleSheet("color: #666; padding: 20px;")
        self.call_list_layout.addWidget(contacts_label)
        
        self.call_list_layout.addStretch()
        
    async def start_call(self, call_type: str, contact_id: str = None):
        """Start a new call with hybrid PQC SRTP - Phase I + III Implementation"""
        try:
            if not contact_id:
                # Get contact from quick selector
                selected_text = self.contact_selector.currentText()
                contact_name = selected_text.split(' (')[0]
                contact_id = contact_name.lower().replace(' ', '_')
            else:
                # Infer name from ID (used for history callback)
                contact_name = contact_id.replace('_', ' ').title()

            logging.info(f"Starting hybrid PQC {call_type} call to {contact_name}")
            self.status_message.emit(f"Starting hybrid PQC {call_type} call...")
            
            # Step 1: Initiate call via backend API
            import aiohttp
            import json
            backend_url = "http://127.0.0.1:8001"  # Use environment variable in production
            
            # Get auth token (simplified for demo)
            auth_token = self.core.current_user.email if self.core and self.core.current_user else "demo@qumail.com"
            
            async with aiohttp.ClientSession() as session:
                # Initiate hybrid call
                async with session.post(
                    f"{backend_url}/api/v1/calls/initiate",
                    json={"contact_id": contact_id, "call_type": call_type},
                    headers={"Authorization": f"Bearer {auth_token}"}
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Call initiation failed: {await response.text()}")
                    
                    call_data = await response.json()
                    call_id = call_data['call_id']
                    
            # Step 2: Generate our hybrid keypair (as caller)
            self.status_message.emit(f"Generating hybrid keys (Kyber-768 + X25519)...")
            
            our_keypair = await self.hybrid_srtp_manager.initiate_hybrid_handshake(contact_id, call_id)
            if not our_keypair:
                QMessageBox.warning(
                    self, "Call Failed", 
                    "Could not generate hybrid PQC keys. Try again."
                )
                return
            
            # Store handshake state
            self.active_handshakes[call_id] = {
                'call_id': call_id,
                'contact_id': contact_id,
                'contact_name': contact_name,
                'call_type': call_type,
                'role': 'caller',
                'our_keypair': our_keypair,
                'status': 'WAITING_FOR_RESPONDER_KEYS',
                'initiated_at': datetime.utcnow().isoformat()
            }
            
            self.status_message.emit(f"Hybrid keys generated - waiting for {contact_name} to respond...")
            
            # Show pre-call dialog with handshake status
            self.show_hybrid_handshake_dialog(call_id, contact_name, call_type)
            
            logging.info(f"Hybrid PQC call initiated: {call_id}")
            
        except Exception as e:
            logging.error(f"Failed to start hybrid PQC call: {e}")
            QMessageBox.critical(self, "Hybrid Call Error", f"Failed to start hybrid PQC call: {str(e)}")
    
    def show_hybrid_handshake_dialog(self, call_id: str, contact_name: str, call_type: str):
        """Show dialog during hybrid PQC handshake process"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Hybrid PQC Call - {contact_name}")
        dialog.setModal(False)  # Allow user to continue using app
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"🔐 Hybrid PQC {call_type.title()} Call")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #4285F4; padding: 10px;")
        layout.addWidget(header_label)
        
        contact_label = QLabel(f"Calling: {contact_name}")
        contact_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contact_label.setFont(QFont("Arial", 14))
        contact_label.setStyleSheet("color: #333; padding: 5px;")
        layout.addWidget(contact_label)
        
        # Security info
        security_frame = QFrame()
        security_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(97, 255, 0, 0.1);
                border: 2px solid #61FF00;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        security_layout = QVBoxLayout(security_frame)
        
        security_title = QLabel("🛡️ Quantum Security Level: Hybrid PQC")
        security_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        security_title.setStyleSheet("color: #61FF00;")
        security_layout.addWidget(security_title)
        
        security_details = QLabel("• CRYSTALS-Kyber-768 (Post-Quantum)\n• X25519 (Classical ECDH)\n• HKDF Session Key Derivation\n• Quantum-Safe SRTP Media")
        security_details.setStyleSheet("color: #333; font-size: 11px;")
        security_layout.addWidget(security_details)
        
        layout.addWidget(security_frame)
        
        # Handshake status
        self.handshake_status_label = QLabel("⏳ Establishing Quantum-Secure Channel...")
        self.handshake_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.handshake_status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.handshake_status_label.setStyleSheet("color: #FF9800; padding: 10px;")
        layout.addWidget(self.handshake_status_label)
        
        # Progress steps
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        
        self.step_labels = []
        steps = [
            "1. ✅ Hybrid keypair generated (Kyber-768 + X25519)",
            "2. ⏳ Waiting for responder key generation...",
            "3. ⏳ Performing hybrid encapsulation...",
            "4. ⏳ Establishing secure media channel..."
        ]
        
        for step in steps:
            step_label = QLabel(step)
            step_label.setStyleSheet("font-size: 10px; color: #666; padding: 2px;")
            progress_layout.addWidget(step_label)
            self.step_labels.append(step_label)
        
        layout.addWidget(progress_frame)
        
        layout.addStretch()
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel Call")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #FF4444;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        cancel_button.clicked.connect(lambda: self.cancel_hybrid_call(call_id, dialog))
        button_layout.addWidget(cancel_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Store dialog reference for updates
        self.active_handshakes[call_id]['dialog'] = dialog
        
        # Show dialog
        dialog.show()
    
    def cancel_hybrid_call(self, call_id: str, dialog: QDialog):
        """Cancel active hybrid call"""
        try:
            if call_id in self.active_handshakes:
                del self.active_handshakes[call_id]
            dialog.close()
            self.status_message.emit("Hybrid PQC call cancelled")
            logging.info(f"Hybrid call cancelled: {call_id}")
        except Exception as e:
            logging.error(f"Error cancelling call: {e}")
    
    def update_handshake_progress(self, call_id: str, step: int, message: str):
        """Update handshake progress in dialog"""
        try:
            if call_id in self.active_handshakes and 'dialog' in self.active_handshakes[call_id]:
                handshake = self.active_handshakes[call_id]
                dialog = handshake['dialog']
                
                # Update status label
                if hasattr(self, 'handshake_status_label'):
                    self.handshake_status_label.setText(message)
                    
                # Update step indicators
                if hasattr(self, 'step_labels') and step < len(self.step_labels):
                    for i, label in enumerate(self.step_labels):
                        if i <= step:
                            text = label.text().replace("⏳", "✅").replace("❌", "✅")
                            label.setText(text)
                            label.setStyleSheet("font-size: 10px; color: #25D366; padding: 2px; font-weight: bold;")
                        
        except Exception as e:
            logging.error(f"Error updating handshake progress: {e}")
            
    def show_audio_call_dialog(self, contact_name: str, call_id: str):
        """Show audio call dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Audio Call - {contact_name}")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Call info
        info_label = QLabel(f"📞 Audio call with {contact_name}")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(info_label)
        
        # Security status
        security_label = QLabel("🔒 Quantum Secured SRTP Ψ")
        security_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        security_label.setStyleSheet("color: #61FF00; font-weight: bold; font-size: 14px;")
        layout.addWidget(security_label)
        
        # Duration
        duration_label = QLabel("00:00")
        duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        duration_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        duration_label.setStyleSheet("color: #25D366;")
        layout.addWidget(duration_label)
        
        layout.addStretch()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        mute_button = QPushButton("🎤 Mute")
        mute_button.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        controls_layout.addWidget(mute_button)
        
        end_button = QPushButton("📞 End Call")
        end_button.setStyleSheet("""
            QPushButton {
                background-color: #FF4444;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        end_button.clicked.connect(dialog.accept)
        controls_layout.addWidget(end_button)
        
        layout.addLayout(controls_layout)
        
        # Start call timer
        call_duration = 0
        call_timer = QTimer()
        
        def update_duration():
            nonlocal call_duration
            call_duration += 1
            minutes = call_duration // 60
            seconds = call_duration % 60
            duration_label.setText(f"{minutes:02d}:{seconds:02d}")
            
        call_timer.timeout.connect(update_duration)
        call_timer.start(1000)
        
        # Show dialog
        dialog.exec()
        call_timer.stop()
        
        # Update call history with actual duration
        for call in self.call_history:
            if call['call_id'] == call_id:
                call['duration'] = call_duration
                call['status'] = 'completed'
                break
                
        self.load_call_history()  # Refresh display
        
    def initiate_callback(self, contact_id: str):
        """Initiate callback to contact - now starts an async task"""
        logging.info(f"Initiating callback to: {contact_id}")
        self.status_message.emit(f"Calling {contact_id}...")
        
        # Use the synchronous wrapper
        self._submit_async_call('audio', contact_id)
        
    def on_call_ended(self):
        """Handle call end"""
        self.active_call = None
        self.status_message.emit("Call ended")
        self.load_call_history()  # Refresh history
        
    def get_sidebar_widget(self) -> Optional[QWidget]:
        """Call module uses its own layout"""
        return None
        
    def handle_search(self, search_text: str):
        """Handle search functionality"""
        # Filter call history based on search
        pass
        
    def update_pqc_call_status(self):
        """Update PQC call status indicators"""
        try:
            if self.active_handshakes:
                # Show active handshakes status
                active_count = len(self.active_handshakes)
                if active_count == 1:
                    call_id = list(self.active_handshakes.keys())[0]
                    handshake = self.active_handshakes[call_id]
                    status = handshake.get('status', 'UNKNOWN')
                    contact_name = handshake.get('contact_name', 'Unknown')
                    
                    if status == 'WAITING_FOR_RESPONDER_KEYS':
                        self.pqc_handshake_status.setText(f"⏳ Waiting for {contact_name} to generate keys...")
                        self.pqc_handshake_status.setStyleSheet("color: #FF9800; font-size: 12px; font-weight: bold;")
                    elif status == 'READY_FOR_ENCAPSULATION':
                        self.pqc_handshake_status.setText(f"🔄 Performing hybrid encapsulation...")
                        self.pqc_handshake_status.setStyleSheet("color: #2196F3; font-size: 12px; font-weight: bold;")
                    elif status == 'HANDSHAKE_COMPLETE':
                        self.pqc_handshake_status.setText(f"✅ Secure channel established with {contact_name}")
                        self.pqc_handshake_status.setStyleSheet("color: #4CAF50; font-size: 12px; font-weight: bold;")
                else:
                    self.pqc_handshake_status.setText(f"🔄 {active_count} active PQC handshakes")
                    self.pqc_handshake_status.setStyleSheet("color: #FF9800; font-size: 12px; font-weight: bold;")
            else:
                # No active handshakes
                if hasattr(self, 'hybrid_srtp_manager') and self.hybrid_srtp_manager.hybrid_kem:
                    self.pqc_handshake_status.setText("✅ Hybrid PQC ready (Kyber-768 + X25519)")
                    self.pqc_handshake_status.setStyleSheet("color: #61FF00; font-size: 12px; font-weight: bold;")
                else:
                    self.pqc_handshake_status.setText("❌ Hybrid PQC unavailable")
                    self.pqc_handshake_status.setStyleSheet("color: #FF5722; font-size: 12px;")
                    
        except Exception as e:
            logging.debug(f"PQC status update error: {e}")
            self.pqc_handshake_status.setText("PQC status: Unknown")
            self.pqc_handshake_status.setStyleSheet("color: #999; font-size: 12px;")
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'pqc_status_timer'):
            self.pqc_status_timer.stop()
        if self.active_call:
            self.active_call.close()
        # Clear active handshakes
        self.active_handshakes.clear()
        logging.info("Call Module cleanup")
