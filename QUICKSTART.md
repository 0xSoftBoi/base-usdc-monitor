# 🚀 Quick Start Guide

Get your Base USDC monitor running in 5 minutes!

## ⚡ Fast Setup

### 1. Clone & Install (2 minutes)

```bash
git clone https://github.com/0xSoftBoi/base-usdc-monitor.git
cd base-usdc-monitor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure (2 minutes)

```bash
cp .env.example .env
```

Edit `.env` with your details:

```env
# Minimum required:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Optional but recommended:
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

### 3. Setup Database (1 minute)

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. SQL Editor → New Query
3. Copy & paste from `scripts/database_schema.sql`
4. Run it ✓

### 4. Test & Run

```bash
# Test connection
python scripts/test_rpc.py

# Start monitoring!
python src/monitor.py
```

## 🎯 What You Get

✅ **Real-time USDC monitoring** on Base network  
✅ **100 USDC transaction alerts** (special focus)  
✅ **Pattern detection** for suspicious activity  
✅ **Multi-channel alerts** (Telegram, Email, Discord)  
✅ **Supabase database** for transaction history  
✅ **Basescan & Bitquery** API integration  

## 📱 Quick Alert Setup

### Telegram (Recommended)

1. Message [@BotFather](https://t.me/botfather)
2. Send: `/newbot`
3. Copy token → Add to `.env`
4. Message [@userinfobot](https://t.me/userinfobot) for chat ID

### Email (Gmail)

1. Enable 2FA in Google Account
2. Generate App Password (Security → App passwords)
3. Add to `.env`:
   ```env
   EMAIL_FROM=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   EMAIL_TO=recipient@email.com
   ```

## 🔍 Monitor Specific Addresses

```env
# Monitor specific wallets
MONITOR_ADDRESSES=0xAddress1,0xAddress2,0xAddress3

# Or leave empty to monitor ALL Base USDC transactions
MONITOR_ADDRESSES=
```

## 📊 View Your Data

**Supabase Dashboard:**
- Tables → `transactions` (all transfers)
- Tables → `alerts` (all notifications)
- Filter by `is_flagged = true` for suspicious activity

## 🛠️ Useful Commands

```bash
# Query specific address
python scripts/query_address.py

# Export data
python scripts/export_data.py

# Test alerts
python scripts/test_alerts.py

# Backfill historical data
python scripts/backfill_data.py
```

## 🐳 Docker (Optional)

```bash
docker-compose up -d
docker-compose logs -f monitor
```

## 📖 Full Documentation

- [Complete Setup Guide](SETUP_GUIDE.md)
- [Main README](README.md)
- [Examples](examples/)

## ⚡ Pro Tips

1. **Use Alchemy/Infura RPC** for better reliability:
   ```env
   BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/YOUR-KEY
   ```

2. **Enable pattern detection** for advanced anomaly detection
   ```env
   PATTERN_DETECTION_ENABLED=true
   ```

3. **Monitor 100 USDC transactions specifically**:
   ```env
   TARGET_AMOUNT=100
   ```

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| RPC not connecting | Try backup RPC: `https://base.llamarpc.com` |
| Supabase error | Check URL and key, verify tables exist |
| No alerts | Run `python scripts/test_alerts.py` |
| High CPU usage | Increase `POLL_INTERVAL` to 30+ |

## 🎉 You're Ready!

Your Base USDC monitor is now running and will:
- ✓ Track all USDC transfers on Base
- ✓ Alert you about 100 USDC transactions
- ✓ Detect unusual patterns
- ✓ Store everything in Supabase
- ✓ Send notifications to your channels

## 🌟 Next Steps

- [ ] Set up backup alerts (Email + Telegram)
- [ ] Configure specific addresses to monitor
- [ ] Explore pattern detection features
- [ ] Set up systemd service for auto-start
- [ ] Add custom alert rules

---

**Built by [0xSoftBoi](https://github.com/0xSoftBoi)** | ⭐ Star if useful!
