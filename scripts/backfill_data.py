#!/usr/bin/env python3
"""
Backfill historical USDC transaction data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from datetime import datetime
from dotenv import load_dotenv
from src.rpc_connector import BaseRPCConnector
from src.usdc_tracker import USDCTracker
from src.database import SupabaseManager

load_dotenv()


async def backfill_blocks(from_block, to_block, batch_size=1000):
    """Backfill historical data"""
    print(f"Backfilling blocks {from_block} to {to_block}")
    print(f"Batch size: {batch_size}")
    print("=" * 50)
    
    rpc = BaseRPCConnector()
    tracker = USDCTracker(rpc)
    db = SupabaseManager()
    
    total_transfers = 0
    current = from_block
    
    while current <= to_block:
        batch_end = min(current + batch_size, to_block)
        
        print(f"\nProcessing blocks {current} to {batch_end}...")
        
        try:
            # Get transfers
            transfers = await tracker.get_transfers(current, batch_end)
            
            print(f"Found {len(transfers)} transfers")
            
            # Save to database
            for transfer in transfers:
                tx_record = {
                    'tx_hash': transfer['transactionHash'],
                    'block_number': transfer['blockNumber'],
                    'timestamp': datetime.now().isoformat(),
                    'from_address': transfer['from'],
                    'to_address': transfer['to'],
                    'amount': transfer['amount'],
                    'status': 'confirmed',
                    'is_flagged': abs(transfer['amount'] - 100.0) < 0.01,
                    'pattern_score': 0.0
                }
                
                await db.insert_transaction(tx_record)
            
            total_transfers += len(transfers)
            print(f"\u2713 Saved {len(transfers)} transfers to database")
            
        except Exception as e:
            print(f"Error processing batch: {e}")
        
        current = batch_end + 1
        
        # Rate limiting
        await asyncio.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"\u2713 Backfill complete!")
    print(f"Total transfers processed: {total_transfers}")
    
    await rpc.close()
    await db.close()


async def main():
    print("Historical Data Backfill Utility")
    print("=" * 50)
    
    rpc = BaseRPCConnector()
    current_block = await rpc.get_latest_block_number()
    
    print(f"\nCurrent block: {current_block}")
    print("\nBase block times: ~2 seconds")
    print("Blocks per hour: ~1800")
    print("Blocks per day: ~43,200")
    print("Blocks per week: ~302,400")
    
    print("\nOptions:")
    print("1. Last 1 hour (~1,800 blocks)")
    print("2. Last 6 hours (~10,800 blocks)")
    print("3. Last 24 hours (~43,200 blocks)")
    print("4. Last 7 days (~302,400 blocks)")
    print("5. Custom range")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        from_block = current_block - 1800
    elif choice == "2":
        from_block = current_block - 10800
    elif choice == "3":
        from_block = current_block - 43200
    elif choice == "4":
        from_block = current_block - 302400
    elif choice == "5":
        from_block = int(input("From block: "))
    else:
        print("Invalid choice")
        return
    
    confirm = input(f"\nBackfill from block {from_block} to {current_block}? (yes/no): ")
    
    if confirm.lower() != "yes":
        print("Cancelled")
        return
    
    await rpc.close()
    await backfill_blocks(from_block, current_block)


if __name__ == "__main__":
    asyncio.run(main())