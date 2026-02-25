#!/usr/bin/env python3
"""
Simple example: Monitor USDC transfers for a specific address
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
from src.rpc_connector import BaseRPCConnector
from src.usdc_tracker import USDCTracker

load_dotenv()


async def monitor_address(address: str):
    """
    Simple monitor for a single address
    """
    print(f"Monitoring USDC transfers for: {address}")
    print("Press Ctrl+C to stop\n")
    
    # Initialize
    rpc = BaseRPCConnector()
    tracker = USDCTracker(rpc)
    
    last_block = await rpc.get_latest_block_number()
    
    try:
        while True:
            # Get latest block
            current_block = await rpc.get_latest_block_number()
            
            if current_block > last_block:
                # Check for new transfers
                transfers = await tracker.get_transfers(
                    from_block=last_block + 1,
                    to_block=current_block,
                    addresses=[address]
                )
                
                # Print any new transfers
                for tx in transfers:
                    direction = "received" if tx['to'].lower() == address.lower() else "sent"
                    print(f"\n✓ New transfer {direction}:")
                    print(f"  Amount: {tx['amount']} USDC")
                    print(f"  Block: {tx['blockNumber']}")
                    print(f"  TX: {tx['transactionHash']}")
                
                last_block = current_block
            
            # Wait 12 seconds (Base block time is ~2 seconds)
            await asyncio.sleep(12)
    
    except KeyboardInterrupt:
        print("\n\nStopping monitor...")
    finally:
        await rpc.close()


if __name__ == "__main__":
    # Example: Monitor your own address
    my_address = input("Enter address to monitor: ").strip()
    
    if not my_address.startswith('0x'):
        print("Invalid address")
        sys.exit(1)
    
    asyncio.run(monitor_address(my_address))