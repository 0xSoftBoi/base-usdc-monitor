#!/usr/bin/env python3
"""
Test Supabase Database Connection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from datetime import datetime
from dotenv import load_dotenv
from src.database import SupabaseManager

load_dotenv()

async def main():
    print("Testing Supabase Database Connection...")
    print("=" * 50)
    
    try:
        # Initialize database manager
        db = SupabaseManager()
        print("\u2713 Database connection established")
        
        # Test 1: Insert test transaction
        print("\n[Test 1] Inserting test transaction...")
        test_tx = {
            'tx_hash': f"0xtest_{datetime.now().timestamp()}",
            'block_number': 12345678,
            'timestamp': datetime.now().isoformat(),
            'from_address': '0x0000000000000000000000000000000000000001',
            'to_address': '0x0000000000000000000000000000000000000002',
            'amount': 100.0,
            'gas_used': 21000,
            'gas_price': '1000000000',
            'status': 'confirmed',
            'is_flagged': True,
            'pattern_score': 0.95
        }
        
        result = await db.insert_transaction(test_tx)
        if result:
            print(f"\u2713 Test transaction inserted: {result.get('id')}")
        
        # Test 2: Get recent transactions
        print("\n[Test 2] Retrieving recent transactions...")
        recent = await db.get_recent_transactions(limit=5)
        print(f"\u2713 Retrieved {len(recent)} transactions")
        
        # Test 3: Get statistics
        print("\n[Test 3] Getting database statistics...")
        stats = await db.get_statistics()
        print(f"\u2713 Total transactions: {stats.get('total_transactions', 0)}")
        print(f"\u2713 Flagged transactions: {stats.get('flagged_transactions', 0)}")
        print(f"\u2713 Total alerts: {stats.get('total_alerts', 0)}")
        
        # Test 4: Insert test alert
        print("\n[Test 4] Inserting test alert...")
        test_alert = {
            'transaction_id': test_tx['tx_hash'],
            'alert_type': 'test',
            'severity': 'low',
            'message': 'Test alert message',
            'channels': ['telegram', 'email']
        }
        
        alert_result = await db.insert_alert(test_alert)
        if alert_result:
            print(f"\u2713 Test alert inserted: {alert_result.get('id')}")
        
        print("\n" + "=" * 50)
        print("✓ All database tests passed!")
        
        await db.close()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)