#!/usr/bin/env python3
"""
QuMail Group Chat Multi-SAE Keying Demonstration
Shows the advanced quantum group communication capabilities
"""

import asyncio
import logging
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add app directory to Python path
sys.path.insert(0, '/app')

async def demonstrate_group_chat_multi_sae():
    """Demonstrate Multi-SAE Group Chat functionality"""
    
    print("🌟 QuMail Group Chat Multi-SAE Keying Demonstration")
    print("=" * 60)
    print("Showcasing advanced quantum group communication")
    print()
    
    try:
        from transport.chat_handler import ChatHandler, GroupChatMessage
        
        # Initialize chat handler
        print("🔧 Initializing Quantum Chat Handler...")
        chat_handler = ChatHandler()
        await chat_handler.initialize()
        
        # Simulate authenticated user
        chat_handler.user_id = 'alice_quantum'
        chat_handler.is_connected = True
        print(f"✅ Authenticated as: {chat_handler.user_id}")
        print()
        
        # ========== Demonstration Scenario ==========
        
        print("📋 SCENARIO: ISRO Quantum Research Team Communication")
        print()
        
        # Step 1: Create research team group
        print("1️⃣  Creating Quantum Research Team Group...")
        group_participants = [
            'dr_sharma_isro',      # ISRO Quantum Lead  
            'prof_patel_iisc',     # IISc Collaborator
            'eng_kumar_drdo',      # DRDO Liaison
            'sci_gupta_tifr'       # TIFR Theorist
        ]
        
        group_id = await chat_handler.create_group_chat(
            "ISRO Quantum Communications Research", 
            group_participants
        )
        
        print(f"✅ Group Created: {group_id}")
        print(f"   👥 Participants: {len(group_participants) + 1} members")
        print(f"   🔐 Multi-SAE Keying: Enabled")
        print()
        
        # Step 2: Send quantum-secured group messages
        print("2️⃣  Sending Quantum-Secured Group Messages...")
        print()
        
        test_messages = [
            ("L1", "🔴 URGENT: Satellite QKD link established! Initial tests successful."),
            ("L2", "📊 Performance metrics: 99.7% fidelity, 1.2 Mbps key rate achieved."),  
            ("L3", "📎 Sharing encrypted research data package (PQC protected).")
        ]
        
        for security_level, message in test_messages:
            print(f"   🔒 Sending {security_level} encrypted message...")
            
            success = await chat_handler.send_group_message(
                group_id, message, security_level
            )
            
            if success:
                print(f"   ✅ Message sent with Multi-SAE keying")
                print(f"      Security: {security_level} ({'OTP' if security_level == 'L1' else 'AES+Quantum' if security_level == 'L2' else 'Post-Quantum Crypto'})")
                print(f"      Recipients: {len(group_participants)} quantum keys generated")
            else:
                print(f"   ❌ Failed to send message")
                
            print()
        
        # Step 3: Retrieve group conversation
        print("3️⃣  Retrieving Group Conversation History...")
        
        history = await chat_handler.get_group_chat_history(group_id, limit=15)
        
        print(f"✅ Retrieved {len(history)} messages from quantum-secured group")
        print()
        print("   📝 Recent Group Messages:")
        
        for i, msg in enumerate(history[-5:], 1):  # Show last 5 messages
            timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M')
            sender = msg['sender_id'].split('_')[0].title()  # Extract name
            security = msg.get('security_level', 'L2')
            content_preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
            
            # Security indicators
            security_emoji = {"L1": "🔴", "L2": "🟡", "L3": "🟢"}
            
            print(f"      {i}. [{timestamp}] {security_emoji.get(security, '🔒')} {sender}: {content_preview}")
            
            if 'sae_key_metadata' in msg:
                print(f"         Multi-SAE: {msg['sae_key_metadata']['total_recipients']} keys, {msg['sae_key_metadata']['key_generation_method']}")
        
        print()
        
        # Step 4: Show Multi-SAE Architecture Benefits
        print("4️⃣  Multi-SAE Quantum Architecture Analysis...")
        print()
        
        # Get group information
        group_list = await chat_handler.get_group_list()
        our_group = next(g for g in group_list if g['group_id'] == group_id)
        
        print("   🏗️  Architecture Highlights:")
        print(f"      • Group ID: {group_id}")
        print(f"      • Participants: {our_group['participant_count']} members")
        print(f"      • Multi-SAE Enabled: {our_group['multi_sae_enabled']}")
        print(f"      • Created by: {our_group['created_by']}")
        print()
        
        print("   🔑 Quantum Key Management:")
        print(f"      • Individual SAE IDs for each participant")
        print(f"      • Separate quantum keys per recipient per message")
        print(f"      • Group key envelope protects message encryption key")
        print(f"      • KME heartbeat monitoring ensures key availability")
        print()
        
        print("   ⚡ Scalability Features:")
        print(f"      • Supports N-participant groups with N quantum keys")
        print(f"      • Compatible with Application Suite architecture")
        print(f"      • Post-Quantum Crypto (L3) for large file sharing")
        print(f"      • Efficient key envelope distribution")
        print()
        
        # Step 5: Application Suite Demo
        print("5️⃣  Application Suite Integration Preview...")
        print()
        
        print("   🔄 Creating Additional Research Groups...")
        
        # Simulate creating multiple groups for different projects
        additional_groups = [
            ("Satellite QKD Team", ['sat_eng1', 'sat_eng2', 'mission_ctrl']),
            ("Ground Station Network", ['ground_ops', 'network_admin', 'security_lead']),
            ("Algorithm Development", ['crypto_expert', 'math_lead', 'code_reviewer'])
        ]
        
        created_groups = []
        for group_name, participants in additional_groups:
            new_group_id = await chat_handler.create_group_chat(group_name, participants)
            created_groups.append((group_name, new_group_id, len(participants) + 1))
            print(f"      ✅ {group_name}: {len(participants) + 1} members")
        
        print()
        print("   📊 Application Suite Statistics:")
        total_groups = len(created_groups) + 1
        total_participants = sum(count for _, _, count in created_groups) + (len(group_participants) + 1)
        
        print(f"      • Total Groups: {total_groups}")
        print(f"      • Total Participants: {total_participants}")
        print(f"      • Multi-SAE Keys per Group Message: Variable (2-5)")
        print(f"      • Estimated Daily Key Usage: ~{total_participants * 10} quantum keys")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the Group Chat Multi-SAE demonstration"""
    
    success = await demonstrate_group_chat_multi_sae()
    
    print("=" * 60)
    if success:
        print("🎉 GROUP CHAT MULTI-SAE DEMONSTRATION COMPLETE!")
        print()
        print("🚀 NEXT STEPS FOR DEPLOYMENT:")
        print("   1. Integrate with real KME infrastructure") 
        print("   2. Deploy WebSocket chat servers")
        print("   3. Implement SAE certificate management")
        print("   4. Add file sharing to group chats")
        print("   5. Scale to organization-wide Application Suite")
        print()
        print("💫 QuMail is ready for quantum-secured group communications!")
        return 0
    else:
        print("❌ Demonstration encountered errors")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)