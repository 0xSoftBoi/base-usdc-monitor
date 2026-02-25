#!/usr/bin/env python3
"""
Export data from database to CSV/JSON
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
import json
import csv
from datetime import datetime
from dotenv import load_dotenv
from src.database import SupabaseManager

load_dotenv()


async def export_to_csv(data, filename):
    """Export data to CSV file"""
    if not data:
        print("No data to export")
        return
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"\u2713 Exported to {filename}")


async def export_to_json(data, filename):
    """Export data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"\u2713 Exported to {filename}")


async def main():
    print("Data Export Utility")
    print("=" * 50)
    
    db = SupabaseManager()
    
    # Export options
    print("\nExport options:")
    print("1. Recent transactions (100)")
    print("2. Flagged transactions")
    print("3. All transactions by amount (100 USDC)")
    print("4. Recent alerts")
    
    choice = input("\nSelect export (1-4): ")
    format_choice = input("Format (csv/json): ").lower()
    
    data = []
    filename = ""
    
    if choice == "1":
        data = await db.get_recent_transactions(limit=100)
        filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    elif choice == "2":
        data = await db.get_flagged_transactions(limit=100)
        filename = f"flagged_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    elif choice == "3":
        data = await db.get_transactions_by_amount(100.0, tolerance=0.01, limit=100)
        filename = f"100usdc_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    elif choice == "4":
        data = await db.get_alerts(limit=100)
        filename = f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    else:
        print("Invalid choice")
        return
    
    if format_choice == "csv":
        await export_to_csv(data, f"data/{filename}.csv")
    elif format_choice == "json":
        await export_to_json(data, f"data/{filename}.json")
    else:
        print("Invalid format")
        return
    
    print(f"\nExported {len(data)} records")
    await db.close()


if __name__ == "__main__":
    # Create data directory if not exists
    os.makedirs('data', exist_ok=True)
    asyncio.run(main())