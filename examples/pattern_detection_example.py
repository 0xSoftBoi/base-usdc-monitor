#!/usr/bin/env python3
"""
Example: Using pattern detection on transaction data
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from src.pattern_detector import PatternDetector


async def analyze_transactions():
    """
    Example of analyzing transactions for patterns
    """
    # Initialize detector
    detector = PatternDetector()
    
    # Example transaction data
    transactions = [
        {
            'tx_hash': '0x123...',
            'block_number': 10000000,
            'timestamp': datetime.now().isoformat(),
            'from_address': '0xAddress1',
            'to_address': '0xAddress2',
            'amount': 100.0,
            'gas_used': 21000,
            'gas_price': '1000000000',
        },
        {
            'tx_hash': '0x124...',
            'block_number': 10000001,
            'timestamp': datetime.now().isoformat(),
            'from_address': '0xAddress1',
            'to_address': '0xAddress3',
            'amount': 100.0,
            'gas_used': 21000,
            'gas_price': '1000000000',
        },
        {
            'tx_hash': '0x125...',
            'block_number': 10000002,
            'timestamp': datetime.now().isoformat(),
            'from_address': '0xAddress1',
            'to_address': '0xAddress4',
            'amount': 100.0,
            'gas_used': 21000,
            'gas_price': '1000000000',
        },
    ]
    
    print("Analyzing transactions for patterns...\n")
    
    for tx in transactions:
        score = await detector.analyze_transaction(tx)
        
        print(f"Transaction: {tx['tx_hash']}")
        print(f"Amount: {tx['amount']} USDC")
        print(f"Anomaly Score: {score:.4f}")
        
        if score > 0.85:
            print("⚠️  HIGH ANOMALY - Suspicious pattern detected!")
        elif score > 0.6:
            print("⚠️  MEDIUM - Unusual pattern")
        else:
            print("✓ Normal pattern")
        
        print()
    
    # Get statistics
    stats = detector.get_statistics()
    print("\nPattern Detection Statistics:")
    print(f"Total transactions analyzed: {stats['total_transactions_analyzed']}")
    print(f"Unique addresses: {stats['unique_addresses']}")
    print(f"Model trained: {stats['model_trained']}")


if __name__ == "__main__":
    asyncio.run(analyze_transactions())