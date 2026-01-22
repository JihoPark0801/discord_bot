# 📊 Discord Stock Trading Bot & Portfolio Dashboard

A full-featured Discord bot for virtual stock trading with an interactive web dashboard. Track your portfolio, set price alerts, manage watchlists, and compete with friends - all with real-time stock market data.

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.3+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🤖 Discord Bot
- **Real-time Stock Prices** - Get current stock prices with `/stock` command
- **Virtual Trading** - Buy and sell stocks with $100,000 virtual cash
- **Portfolio Management** - Track your holdings, profit/loss, and performance
- **Watchlists** - Create personalized stock watchlists
- **Price Alerts** - Get notified when stocks hit your target prices
- **Transaction History** - View all your past trades
- **Portfolio Reset** - Start over with a fresh $100,000

### 🌐 Web Dashboard
- **Discord OAuth Login** - Secure login with your Discord account
- **Interactive Charts** - Visualize portfolio allocation with Chart.js
- **Real-time Data** - Live stock prices and portfolio values
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Comprehensive View** - Portfolio, watchlist, and alerts all in one place
- **Profit/Loss Tracking** - See your gains and losses at a glance

## 📸 Screenshots

### Discord Bot Commands
```
/portfolio_start - Create your account
/buy AAPL 10 - Buy 10 shares of Apple
/sell TSLA 5 - Sell 5 shares of Tesla
/portfolio - View your holdings
/watchlist_add GOOGL - Add Google to watchlist
/alert_add MSFT 350 above - Alert when Microsoft goes above $350
```

### Web Dashboard
*[Your dashboard showing portfolio, charts, watchlist, and alerts]*

## 🛠️ Tech Stack

**Backend:**
- Python 3.12+
- discord.py 2.3+ - Discord bot framework
- Flask 3.0+ - Web framework
- SQLite - Database storage

**Frontend:**
- HTML5/CSS3
- JavaScript
- Chart.js - Interactive charts
- Jinja2 - Template engine

**APIs:**
- Discord OAuth2 - Authentication
- Stock Price API - Real-time market data

## 📋 Prerequisites

- Python 3.12 or higher
- Discord account and bot token
- Discord Developer Application (for OAuth)
- Stock price API access (e.g., Alpha Vantage, Yahoo Finance)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/discord-stock-bot.git
cd discord-stock-bot
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" tab and create a bot
4. Copy the bot token
5. Enable these Privileged Gateway Intents:
   - Server Members Intent
   - Message Content Intent
6. Go to "OAuth2" → "URL Generator"
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: `Send Messages`, `Use Slash Commands`, `Read Messages`
   - Copy the generated URL and invite bot to your server

### 5. Set Up Discord OAuth

1. In your Discord application, go to "OAuth2" → "General"
2. Copy your Client ID and Client Secret
3. Add redirect URL: `http://127.0.0.1:5001/callback` (for local development)

### 6. Configure Environment Variables

Create a `.env` file in the project root:
```env
# Discord Bot
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here

# Discord OAuth (for web dashboard)
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_CLIENT_SECRET=your_client_secret_here
DISCORD_REDIRECT_URI=http://127.0.0.1:5001/callback

# Dashboard URL
DASHBOARD_URL=http://127.0.0.1:5001

# Stock API (if applicable)
STOCK_API_KEY=your_api_key_here
```

### 7. Initialize Databases

The databases will be created automatically on first run, but you can verify the structure in:
- `portfolio.db` - User accounts and holdings
- `watchlist.db` - User watchlists
- `alerts.db` - Price alerts

## 🎮 Usage

### Running Locally

**Terminal 1 - Start Discord Bot:**
```bash
python main.py
```

**Terminal 2 - Start Web Dashboard:**
```bash
cd web
python app.py
```

Visit: `http://127.0.0.1:5001`

### Discord Commands

#### Portfolio Management
- `/portfolio_start` - Create your virtual trading account
- `/buy <ticker> <quantity>` - Purchase stocks
- `/sell <ticker> <quantity>` - Sell stocks
- `/portfolio` - View your current holdings
- `/balance` - Check your cash and total account value
- `/history [ticker]` - View transaction history
- `/portfolio_reset` - Reset your portfolio to $100,000

#### Watchlist
- `/watchlist_add <ticker>` - Add stock to watchlist
- `/watchlist_remove <ticker>` - Remove stock from watchlist
- `/watchlist` - View your watchlist with current prices
- `/watchlist_clear` - Clear entire watchlist

#### Price Alerts
- `/alert_add <ticker> <price> <type>` - Set price alert (above/below)
- `/alert_list` - View active alerts
- `/alert_remove <ticker> <price>` - Remove specific alert
- `/alert_clear` - Clear all alerts

#### Utilities
- `/stock <ticker>` - Get current stock price
- `/dashboard` - Get link to web dashboard
