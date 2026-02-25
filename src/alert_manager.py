#!/usr/bin/env python3
"""
Alert Manager
Handles sending alerts through multiple channels (Telegram, Email, Discord, Webhooks)
"""

import asyncio
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import aiohttp
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class AlertManager:
    """
    Manages multi-channel alert delivery
    """
    
    def __init__(self):
        # Telegram configuration
        self.telegram_enabled = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Email configuration
        self.email_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
        self.smtp_server = os.getenv('EMAIL_SMTP_SERVER')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_to = os.getenv('EMAIL_TO', '').split(',')
        
        # Discord configuration
        self.discord_enabled = os.getenv('DISCORD_ENABLED', 'false').lower() == 'true'
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        
        # Custom webhook configuration
        self.webhook_enabled = os.getenv('WEBHOOK_ENABLED', 'false').lower() == 'true'
        self.webhook_url = os.getenv('WEBHOOK_URL')
        self.webhook_secret = os.getenv('WEBHOOK_SECRET')
        
        logger.info(f"Alert Manager initialized - Telegram: {self.telegram_enabled}, Email: {self.email_enabled}, Discord: {self.discord_enabled}")
    
    async def send_alert(self, alert_type: str, severity: str, message: str, 
                        transaction_id: str = None):
        """
        Send alert through all enabled channels
        
        Args:
            alert_type: Type of alert (target_amount, pattern_anomaly, large_transfer, etc.)
            severity: Alert severity (low, medium, high, critical)
            message: Alert message
            transaction_id: Optional transaction hash
        """
        try:
            tasks = []
            
            if self.telegram_enabled:
                tasks.append(self._send_telegram(message, severity))
            
            if self.email_enabled:
                tasks.append(self._send_email(alert_type, message, severity, transaction_id))
            
            if self.discord_enabled:
                tasks.append(self._send_discord(message, severity, alert_type))
            
            if self.webhook_enabled:
                tasks.append(self._send_webhook(alert_type, message, severity, transaction_id))
            
            # Send all alerts concurrently
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}", exc_info=True)
    
    async def _send_telegram(self, message: str, severity: str):
        """Send alert via Telegram"""
        try:
            if not self.telegram_token or not self.telegram_chat_id:
                logger.warning("Telegram credentials not configured")
                return
            
            # Add severity emoji
            emoji_map = {
                'low': '🔵',
                'medium': '🟡',
                'high': '🔴',
                'critical': '🔴‼️'
            }
            emoji = emoji_map.get(severity, '🔔')
            
            formatted_message = f"{emoji} {message}"
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={
                    'chat_id': self.telegram_chat_id,
                    'text': formatted_message,
                    'parse_mode': 'Markdown',
                    'disable_web_page_preview': True
                }) as response:
                    if response.status == 200:
                        logger.info("✓ Telegram alert sent")
                    else:
                        logger.error(f"Telegram API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")
    
    async def _send_email(self, subject: str, message: str, severity: str, transaction_id: str = None):
        """Send alert via Email"""
        try:
            if not all([self.smtp_server, self.email_from, self.email_password]):
                logger.warning("Email credentials not configured")
                return
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{severity.upper()}] Base USDC Monitor: {subject}"
            msg['From'] = self.email_from
            msg['To'] = ', '.join(self.email_to)
            
            # Create HTML content
            html_message = f"""
            <html>
              <head></head>
              <body>
                <h2 style="color: {'red' if severity == 'high' else 'orange' if severity == 'medium' else 'blue'};">Base USDC Monitor Alert</h2>
                <p><strong>Severity:</strong> {severity.upper()}</p>
                <p><strong>Alert Type:</strong> {subject}</p>
                <hr>
                <pre style="background-color: #f4f4f4; padding: 10px; border-radius: 5px;">{message}</pre>
                {f'<p><strong>Transaction:</strong> <a href="https://basescan.org/tx/{transaction_id}">{transaction_id}</a></p>' if transaction_id else ''}
                <hr>
                <p><em>Sent by Base USDC Monitor</em></p>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(message, 'plain'))
            msg.attach(MIMEText(html_message, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
            
            logger.info("✓ Email alert sent")
        
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
    
    async def _send_discord(self, message: str, severity: str, alert_type: str):
        """Send alert via Discord webhook"""
        try:
            if not self.discord_webhook:
                logger.warning("Discord webhook not configured")
                return
            
            # Color based on severity
            color_map = {
                'low': 3447003,      # Blue
                'medium': 16776960,  # Yellow
                'high': 16711680,    # Red
                'critical': 10038562 # Dark red
            }
            
            embed = {
                'title': f'Base USDC Monitor Alert: {alert_type}',
                'description': message,
                'color': color_map.get(severity, 3447003),
                'timestamp': asyncio.get_event_loop().time(),
                'footer': {'text': 'Base USDC Monitor'}
            }
            
            payload = {
                'embeds': [embed]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.discord_webhook, json=payload) as response:
                    if response.status in [200, 204]:
                        logger.info("✓ Discord alert sent")
                    else:
                        logger.error(f"Discord webhook error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error sending Discord alert: {e}")
    
    async def _send_webhook(self, alert_type: str, message: str, severity: str, transaction_id: str = None):
        """Send alert to custom webhook"""
        try:
            if not self.webhook_url:
                logger.warning("Custom webhook not configured")
                return
            
            payload = {
                'alert_type': alert_type,
                'severity': severity,
                'message': message,
                'transaction_id': transaction_id,
                'timestamp': asyncio.get_event_loop().time()
            }
            
            headers = {}
            if self.webhook_secret:
                headers['X-Webhook-Secret'] = self.webhook_secret
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        logger.info("✓ Custom webhook alert sent")
                    else:
                        logger.error(f"Webhook error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error sending webhook alert: {e}")
    
    async def test_alerts(self):
        """Test all configured alert channels"""
        logger.info("Testing alert channels...")
        
        test_message = "This is a test alert from Base USDC Monitor. If you receive this, your alert system is working correctly!"
        
        await self.send_alert(
            alert_type='test',
            severity='low',
            message=test_message,
            transaction_id=None
        )
        
        logger.info("Test alerts sent")