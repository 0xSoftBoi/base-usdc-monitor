#!/usr/bin/env python3
"""
Main USDC Monitor Script
Continuously monitors USDC transfers on Base network
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
import os

from rpc_connector import BaseRPCConnector
from usdc_tracker import USDCTracker
from pattern_detector import PatternDetector
from alert_manager import AlertManager
from database import SupabaseManager
from basescan_api import BasescanAPI
from bitquery_api import BitqueryAPI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'logs/monitor.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class USDCMonitor:
    """
    Main monitoring class that orchestrates all components
    """
    
    def __init__(self):
        logger.info("Initializing USDC Monitor...")
        
        # Initialize components
        self.rpc = BaseRPCConnector()
        self.tracker = USDCTracker(self.rpc)
        self.pattern_detector = PatternDetector()
        self.alert_manager = AlertManager()
        self.db = SupabaseManager()
        self.basescan = BasescanAPI()
        self.bitquery = BitqueryAPI()
        
        # Configuration
        self.target_amount = float(os.getenv('TARGET_AMOUNT', '100'))
        self.poll_interval = int(os.getenv('POLL_INTERVAL', '12'))
        self.monitor_addresses = os.getenv('MONITOR_ADDRESSES', '').split(',')
        self.monitor_addresses = [addr.strip() for addr in self.monitor_addresses if addr.strip()]
        
        # State
        self.is_running = False
        self.last_block = None
        self.transaction_cache = set()
        
        logger.info(f"Monitor initialized. Tracking {len(self.monitor_addresses)} addresses")
        logger.info(f"Target amount: {self.target_amount} USDC")
    
    async def start(self):
        """Start the monitoring loop"""
        logger.info("Starting USDC Monitor...")
        self.is_running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Get initial block
            self.last_block = await self.rpc.get_latest_block_number()
            logger.info(f"Starting from block: {self.last_block}")
            
            # Start monitoring loop
            await self._monitor_loop()
            
        except Exception as e:
            logger.error(f"Fatal error in monitor: {e}", exc_info=True)
            await self.stop()
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Entering monitoring loop...")
        
        while self.is_running:
            try:
                # Get latest block
                current_block = await self.rpc.get_latest_block_number()
                
                if current_block > self.last_block:
                    logger.info(f"Processing blocks {self.last_block + 1} to {current_block}")
                    
                    # Process new blocks
                    await self._process_blocks(self.last_block + 1, current_block)
                    
                    self.last_block = current_block
                
                # Wait before next poll
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)
    
    async def _process_blocks(self, from_block: int, to_block: int):
        """Process a range of blocks for USDC transfers"""
        try:
            # Get USDC transfers in block range
            transfers = await self.tracker.get_transfers(
                from_block=from_block,
                to_block=to_block,
                addresses=self.monitor_addresses if self.monitor_addresses else None
            )
            
            logger.info(f"Found {len(transfers)} USDC transfers")
            
            for transfer in transfers:
                await self._process_transfer(transfer)
            
        except Exception as e:
            logger.error(f"Error processing blocks: {e}", exc_info=True)
    
    async def _process_transfer(self, transfer: Dict):
        """Process a single USDC transfer"""
        try:
            tx_hash = transfer['transactionHash']
            
            # Skip if already processed
            if tx_hash in self.transaction_cache:
                return
            
            self.transaction_cache.add(tx_hash)
            
            # Parse transfer details
            from_address = transfer['from']
            to_address = transfer['to']
            amount = transfer['amount']
            block_number = transfer['blockNumber']
            
            logger.info(f"Processing transfer: {amount} USDC from {from_address[:10]}... to {to_address[:10]}...")
            
            # Check for target amount (100 USDC)
            is_target_amount = abs(amount - self.target_amount) < 0.01
            
            # Get additional transaction details
            tx_details = await self.rpc.get_transaction(tx_hash)
            
            # Enrich with Basescan data
            basescan_data = await self.basescan.get_transaction_details(tx_hash)
            
            # Prepare transaction record
            tx_record = {
                'tx_hash': tx_hash,
                'block_number': block_number,
                'timestamp': datetime.now().isoformat(),
                'from_address': from_address,
                'to_address': to_address,
                'amount': amount,
                'gas_used': tx_details.get('gas'),
                'gas_price': tx_details.get('gasPrice'),
                'status': 'confirmed',
                'is_flagged': is_target_amount,
                'pattern_score': 0.0
            }
            
            # Detect patterns
            if os.getenv('PATTERN_DETECTION_ENABLED', 'true').lower() == 'true':
                pattern_score = await self.pattern_detector.analyze_transaction(tx_record)
                tx_record['pattern_score'] = pattern_score
                
                if pattern_score > float(os.getenv('ANOMALY_THRESHOLD', '0.85')):
                    tx_record['is_flagged'] = True
            
            # Save to database
            db_record = await self.db.insert_transaction(tx_record)
            
            # Send alerts
            await self._send_alerts(tx_record, is_target_amount)
            
        except Exception as e:
            logger.error(f"Error processing transfer: {e}", exc_info=True)
    
    async def _send_alerts(self, tx_record: Dict, is_target_amount: bool):
        """Send appropriate alerts based on transaction"""
        try:
            alerts = []
            
            # 100 USDC alert
            if is_target_amount:
                alert_msg = (
                    f"🎯 **100 USDC TRANSACTION DETECTED**\n"
                    f"From: `{tx_record['from_address']}`\n"
                    f"To: `{tx_record['to_address']}`\n"
                    f"Amount: {tx_record['amount']} USDC\n"
                    f"Block: {tx_record['block_number']}\n"
                    f"TX: `{tx_record['tx_hash']}`"
                )
                alerts.append(('target_amount', 'high', alert_msg))
            
            # Pattern anomaly alert
            if tx_record.get('is_flagged') and tx_record.get('pattern_score', 0) > 0.85:
                alert_msg = (
                    f"⚠️ **UNUSUAL PATTERN DETECTED**\n"
                    f"Score: {tx_record['pattern_score']:.2f}\n"
                    f"Amount: {tx_record['amount']} USDC\n"
                    f"From: `{tx_record['from_address']}`\n"
                    f"To: `{tx_record['to_address']}`\n"
                    f"TX: `{tx_record['tx_hash']}`"
                )
                alerts.append(('pattern_anomaly', 'medium', alert_msg))
            
            # Large transfer alert
            if tx_record['amount'] > 10000:
                alert_msg = (
                    f"💰 **LARGE TRANSFER DETECTED**\n"
                    f"Amount: {tx_record['amount']:,.2f} USDC\n"
                    f"From: `{tx_record['from_address']}`\n"
                    f"To: `{tx_record['to_address']}`\n"
                    f"TX: `{tx_record['tx_hash']}`"
                )
                alerts.append(('large_transfer', 'high', alert_msg))
            
            # Send all alerts
            for alert_type, severity, message in alerts:
                await self.alert_manager.send_alert(
                    alert_type=alert_type,
                    severity=severity,
                    message=message,
                    transaction_id=tx_record['tx_hash']
                )
                
                # Save alert to database
                await self.db.insert_alert({
                    'transaction_id': tx_record['tx_hash'],
                    'alert_type': alert_type,
                    'severity': severity,
                    'message': message
                })
            
        except Exception as e:
            logger.error(f"Error sending alerts: {e}", exc_info=True)
    
    async def stop(self):
        """Stop the monitor gracefully"""
        logger.info("Stopping USDC Monitor...")
        self.is_running = False
        
        # Cleanup
        await self.db.close()
        await self.rpc.close()
        
        logger.info("Monitor stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}")
        asyncio.create_task(self.stop())


async def main():
    """Main entry point"""
    logger.info("="*50)
    logger.info("Base USDC Monitor Starting")
    logger.info("="*50)
    
    monitor = USDCMonitor()
    await monitor.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Monitor interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)