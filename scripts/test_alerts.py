#!/usr/bin/env python3
"""
Test Alert System
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from dotenv import load_dotenv
from src.alert_manager import AlertManager

load_dotenv()

async def main():
    print("Testing Alert System...")
    print("=" * 50)
    
    try:
        # Initialize alert manager
        alert_mgr = AlertManager()
        
        print("\n[Test] Sending test alerts to all configured channels...")
        print(f"Telegram: {alert_mgr.telegram_enabled}")
        print(f"Email: {alert_mgr.email_enabled}")
        print(f"Discord: {alert_mgr.discord_enabled}")
        print(f"Webhook: {alert_mgr.webhook_enabled}")
        
        # Send test alert
        await alert_mgr.test_alerts()
        
        print("\n" + "=" * 50)
        print("✓ Alert test completed!")
        print("Check your configured channels for test messages.")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)