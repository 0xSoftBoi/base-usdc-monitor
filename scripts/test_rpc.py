#!/usr/bin/env python3
"""
Test RPC Connection to Base Network
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from dotenv import load_dotenv
from src.rpc_connector import BaseRPCConnector

load_dotenv()

async def main():
    print("Testing Base RPC Connection...")
    print("=" * 50)
    
    try:
        # Initialize RPC connector
        rpc = BaseRPCConnector()
        
        # Test 1: Get latest block
        print("\n[Test 1] Getting latest block number...")
        block_number = await rpc.get_latest_block_number()
        print(f"\u2713 Latest block: {block_number}")
        
        # Test 2: Get block details
        print("\n[Test 2] Getting block details...")
        block = await rpc.get_block(block_number)
        print(f"\u2713 Block hash: {block.get('hash').hex() if block.get('hash') else 'N/A'}")
        print(f"\u2713 Timestamp: {block.get('timestamp')}")
        print(f"\u2713 Transactions: {len(block.get('transactions', []))}")
        
        # Test 3: Get USDC balance
        print("\n[Test 3] Testing USDC balance query...")
        usdc_address = os.getenv('USDC_CONTRACT_ADDRESS')
        test_address = "0x0000000000000000000000000000000000000000"
        balance = rpc.get_token_balance(usdc_address, test_address, decimals=6)
        print(f"\u2713 USDC balance query successful: {balance} USDC")
        
        print("\n" + "=" * 50)
        print("✓ All RPC tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)