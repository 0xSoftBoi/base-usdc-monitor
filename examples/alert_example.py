#!/usr/bin/env python3
"""
Example: Sending custom alerts
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
from src.alert_manager import AlertManager

load_dotenv()


async def send_custom_alert():
    """
    Example of sending custom alerts
    """
    # Initialize alert manager
    alert_mgr = AlertManager()
    
    print("Sending example alerts...\n")
    
    # Example 1: Low severity info
    await alert_mgr.send_alert(
        alert_type='info',
        severity='low',
        message='This is an informational alert',
        transaction_id='0x123...'
    )
    print("✓ Sent low severity alert")
    
    # Example 2: Medium severity warning
    await alert_mgr.send_alert(
        alert_type='warning',
        severity='medium',
        message='\u26a0️ Unusual activity detected\nMultiple transactions in short time',
        transaction_id='0x456...'
    )
    print("✓ Sent medium severity alert")
    
    # Example 3: High severity critical
    await alert_mgr.send_alert(
        alert_type='critical',
        severity='high',
        message=(
            '🚨 CRITICAL ALERT\n'
            'Large USDC transfer detected\n'
            'Amount: 50,000 USDC\n'
            'Please review immediately'
        ),
        transaction_id='0x789...'
    )
    print("✓ Sent high severity alert")
    
    print("\nCheck your configured alert channels!")


if __name__ == "__main__":
    asyncio.run(send_custom_alert())