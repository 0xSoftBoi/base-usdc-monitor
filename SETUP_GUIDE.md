# Setup Guide for Base USDC Monitor

Complete step-by-step guide to get your monitoring system running.

## Prerequisites

### Required

1. **Python 3.9+**
   ```bash
   python --version
   ```

2. **Git**
   ```bash
   git --version
   ```

3. **Supabase Account**
   - Sign up at [supabase.com](https://supabase.com)
   - Create a new project
   - Save your project URL and anon key

### Optional (for alerts)

4. **Telegram Bot** (recommended)
   - Message [@BotFather](https://t.me/botfather)
   - Create a new bot: `/newbot`
   - Save the bot token
   - Get your chat ID: message [@userinfobot](https://t.me/userinfobot)

5. **Email Account** (Gmail recommended)
   - Enable 2FA
   - Generate app-specific password

6. **API Keys**
   - Basescan: [basescan.org/apis](https://basescan.org/apis)
   - Bitquery: [bitquery.io](https://bitquery.io)

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/0xSoftBoi/base-usdc-monitor.git
cd base-usdc-monitor
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit with your values
nano .env  # or use your preferred editor
```

**Minimum required configuration:**

```env
# Base Network
BASE_RPC_URL=https://mainnet.base.org

# USDC Contract
USDC_CONTRACT_ADDRESS=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

# Supabase (REQUIRED)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# Monitoring
MONITOR_ADDRESSES=  # Leave empty to monitor all, or add comma-separated addresses
TARGET_AMOUNT=100
```

### Step 5: Setup Database

1. Go to your Supabase dashboard
2. Navigate to SQL Editor
3. Copy the contents of `scripts/database_schema.sql`
4. Paste and run in SQL Editor
5. Verify tables were created in Table Editor

### Step 6: Test Connections

```bash
# Test RPC connection
python scripts/test_rpc.py

# Test database connection
python scripts/test_database.py

# Test alerts (if configured)
python scripts/test_alerts.py
```

## Configuration Details

### Base Network RPC

**Free Options:**
- Public RPC: `https://mainnet.base.org`
- Llama RPC: `https://base.llamarpc.com`

**Premium Options (recommended for production):**
- Alchemy: Get API key at [alchemy.com](https://alchemy.com)
  - URL: `https://base-mainnet.g.alchemy.com/v2/YOUR-API-KEY`
- Infura: Get API key at [infura.io](https://infura.io)
  - URL: `https://base-mainnet.infura.io/v3/YOUR-API-KEY`

### Alert Configuration

#### Telegram Setup

1. **Create Bot:**
   ```
   1. Message @BotFather
   2. Send: /newbot
   3. Choose name and username
   4. Copy token
   ```

2. **Get Chat ID:**
   ```
   1. Message @userinfobot
   2. Copy your ID
   ```

3. **For Group Alerts:**
   ```
   1. Add bot to group
   2. Make bot admin
   3. Get group ID using @RawDataBot
   ```

4. **Configure:**
   ```env
   TELEGRAM_ENABLED=true
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   ```

#### Email Setup (Gmail)

1. **Enable 2FA:**
   - Go to Google Account settings
   - Security → 2-Step Verification

2. **Generate App Password:**
   - Security → App passwords
   - Select "Mail" and your device
   - Copy 16-character password

3. **Configure:**
   ```env
   EMAIL_ENABLED=true
   EMAIL_SMTP_SERVER=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   EMAIL_FROM=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password-here
   EMAIL_TO=recipient@email.com
   ```

#### Discord Webhook

1. **Create Webhook:**
   - Server Settings → Integrations → Webhooks
   - Create webhook
   - Copy webhook URL

2. **Configure:**
   ```env
   DISCORD_ENABLED=true
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```

### Monitoring Specific Addresses

**Option 1: Environment Variable**
```env
MONITOR_ADDRESSES=0xAddress1,0xAddress2,0xAddress3
```

**Option 2: Config File**
Edit `config/config.yaml`:
```yaml
monitoring:
  watch_addresses:
    - "0xYourWalletAddress1"
    - "0xYourWalletAddress2"
```

## Running the Monitor

### Basic Usage

```bash
# Start monitoring
python src/monitor.py
```

### Using Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f monitor

# Stop
docker-compose down
```

### Running as System Service (Linux)

Create `/etc/systemd/system/base-usdc-monitor.service`:

```ini
[Unit]
Description=Base USDC Monitor
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/base-usdc-monitor
Environment="PATH=/path/to/base-usdc-monitor/venv/bin"
ExecStart=/path/to/base-usdc-monitor/venv/bin/python src/monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable base-usdc-monitor
sudo systemctl start base-usdc-monitor
sudo systemctl status base-usdc-monitor
```

## Monitoring Dashboard

View your transactions in Supabase:

1. Go to Supabase Dashboard
2. Navigate to Table Editor
3. Select `transactions` table
4. Filter by `is_flagged = true` for suspicious transactions

## Troubleshooting

### RPC Connection Issues

**Error: Cannot connect to Base RPC**

Solution:
```bash
# Try backup RPC
BASE_RPC_URL=https://base.llamarpc.com

# Or use premium RPC (Alchemy/Infura)
```

### Database Connection Issues

**Error: Supabase connection failed**

Solution:
1. Verify URL and key in `.env`
2. Check Supabase project is active
3. Ensure IP is not blocked (if using RLS)
4. Run schema again: `scripts/database_schema.sql`

### Alert Issues

**Telegram alerts not working:**
```bash
# Test manually
curl -X POST https://api.telegram.org/bot<TOKEN>/sendMessage \
  -d chat_id=<CHAT_ID> \
  -d text="Test"
```

**Email alerts not working:**
- Verify app password (not regular password)
- Check Gmail security settings
- Try different SMTP server

### Performance Issues

**High CPU/Memory usage:**
```env
# Reduce polling frequency
POLL_INTERVAL=30

# Reduce worker threads
WORKER_THREADS=2

# Disable pattern detection temporarily
PATTERN_DETECTION_ENABLED=false
```

## Updating

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart monitor
# If using systemd:
sudo systemctl restart base-usdc-monitor
# If using Docker:
docker-compose restart
```

## Security Best Practices

1. **Never commit `.env` file**
   ```bash
   # Verify it's in .gitignore
   cat .gitignore | grep .env
   ```

2. **Use environment-specific configs**
   - `.env.development`
   - `.env.production`

3. **Restrict Supabase RLS**
   - Enable Row Level Security
   - Create appropriate policies

4. **Rotate API keys regularly**
   - Especially after any exposure

5. **Use read-only RPC when possible**
   - Monitor doesn't need write access

## Next Steps

- [ ] Configure alerts for your needs
- [ ] Set up monitoring dashboard
- [ ] Add custom pattern detection rules
- [ ] Set up backup alerts
- [ ] Configure log rotation
- [ ] Set up monitoring metrics

## Support

- GitHub Issues: [Report a bug](https://github.com/0xSoftBoi/base-usdc-monitor/issues)
- Discussions: [Ask questions](https://github.com/0xSoftBoi/base-usdc-monitor/discussions)

---

**Need help? Open an issue on GitHub!**