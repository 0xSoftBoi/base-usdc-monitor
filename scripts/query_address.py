#!/usr/bin/env python3
"""
Query USDC transactions for a specific address
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from dotenv import load_dotenv
from src.usdc_tracker import USDCTracker
from src.rpc_connector import BaseRPCConnector
from tabulate import tabulate

load_dotenv()


async def main():
    print("USDC Address Query Tool")
    print("=" * 50)
    
    # Get address from user
    address = input("\nEnter address to query: ").strip()
    
    if not address.startswith('0x'):
        print("Invalid address format")
        return
    
    # Initialize
    rpc = BaseRPCConnector()
    tracker = USDCTracker(rpc)
    
    print(f"\nQuerying USDC transactions for {address}...")
    print("This may take a moment...\n")
    
    # Get current block
    current_block = await rpc.get_latest_block_number()
    
    # Query from last 10000 blocks (approximately 5.5 hours on Base)
    from_block = max(0, current_block - 10000)
    
    print(f"Scanning blocks {from_block} to {current_block}")
    
    # Get transfers
    transfers = await tracker.track_address(address, from_block=from_block)
    
    if not transfers:
        print("\nNo USDC transfers found in the specified range")
        return
    
    print(f"\nFound {len(transfers)} USDC transfers\n")
    
    # Get current balance
    balance = await tracker.get_balance(address)
    print(f"Current USDC Balance: {balance:,.2f} USDC\n")
    
    # Display transfers
    table_data = []
    for tx in transfers[:20]:  # Show first 20
        direction = "OUT" if tx['from'].lower() == address.lower() else "IN"
        other_party = tx['to'] if direction == "OUT" else tx['from']
        
        table_data.append([
            tx['blockNumber'],
            direction,
            f"{tx['amount']:,.2f}",
            f"{other_party[:10]}...{other_party[-8:]}",
            f"{tx['transactionHash'][:10]}..."
        ])
    
    headers = ["Block", "Direction", "Amount (USDC)", "Other Party", "TX Hash"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    if len(transfers) > 20:
        print(f"\n... and {len(transfers) - 20} more transactions")
    
    # Statistics
    total_in = sum(tx['amount'] for tx in transfers if tx['to'].lower() == address.lower())
    total_out = sum(tx['amount'] for tx in transfers if tx['from'].lower() == address.lower())
    
    print("\n" + "=" * 50)
    print("Statistics:")
    print(f"Total Received: {total_in:,.2f} USDC")
    print(f"Total Sent: {total_out:,.2f} USDC")
    print(f"Net Flow: {total_in - total_out:,.2f} USDC")
    
    await rpc.close()


if __name__ == "__main__":
    asyncio.run(main())