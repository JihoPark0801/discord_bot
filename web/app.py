from flask import Flask, render_template, redirect, url_for, session, request
import sqlite3
import os
import sys
import requests
from dotenv import load_dotenv
from pathlib import Path


env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.stocks import get_stock_price

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for sessions

# Database paths
DB_PATH = '../portfolio.db'
WATCHLIST_DB_PATH = '../watchlist.db'
ALERTS_DB_PATH = '../alerts.db'

# Discord OAuth settings
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI')
DISCORD_API_URL = 'https://discord.com/api/v10'
DISCORD_OAUTH_URL = f'{DISCORD_API_URL}/oauth2/authorize'
DISCORD_TOKEN_URL = f'{DISCORD_API_URL}/oauth2/token'
DISCORD_USER_URL = f'{DISCORD_API_URL}/users/@me'

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_portfolio(user_id):
    """Get user's portfolio data with current prices"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT cash_balance, starting_balance FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return None
    
    cursor.execute('SELECT ticker, quantity, avg_cost FROM portfolio WHERE user_id = ?', (user_id,))
    holdings = cursor.fetchall()
    
    conn.close()
    
    portfolio_data = []
    total_cost_basis = 0
    total_current_value = 0
    
    for holding in holdings:
        ticker = holding['ticker']
        quantity = holding['quantity']
        avg_cost = holding['avg_cost']
        cost_basis = quantity * avg_cost
        
        current_price = get_stock_price(ticker)
        
        if current_price:
            current_value = quantity * current_price
            profit_loss = current_value - cost_basis
            percent_change = (profit_loss / cost_basis) * 100
        else:
            current_price = avg_cost
            current_value = cost_basis
            profit_loss = 0
            percent_change = 0
        
        portfolio_data.append({
            'ticker': ticker,
            'quantity': quantity,
            'avg_cost': avg_cost,
            'cost_basis': cost_basis,
            'current_price': current_price,
            'current_value': current_value,
            'profit_loss': profit_loss,
            'percent_change': percent_change
        })
        
        total_cost_basis += cost_basis
        total_current_value += current_value
    
    cash_balance = user['cash_balance']
    total_account_value = cash_balance + total_current_value
    overall_pl = total_account_value - user['starting_balance']
    overall_percent = (overall_pl / user['starting_balance']) * 100
    
    return {
        'cash_balance': cash_balance,
        'starting_balance': user['starting_balance'],
        'holdings': portfolio_data,
        'total_cost_basis': total_cost_basis,
        'total_current_value': total_current_value,
        'total_account_value': total_account_value,
        'overall_pl': overall_pl,
        'overall_percent': overall_percent
    }

def get_user_watchlist(user_id):
    """Get user's watchlist with current prices"""
    try:
        conn = sqlite3.connect(WATCHLIST_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT ticker FROM watchlist WHERE user_id = ? ORDER BY ticker', (user_id,))
        watchlist = cursor.fetchall()
        conn.close()
        
        watchlist_data = []
        for item in watchlist:
            ticker = item['ticker']
            current_price = get_stock_price(ticker)
            
            watchlist_data.append({
                'ticker': ticker,
                'current_price': current_price if current_price else 'N/A'
            })
        
        return watchlist_data
    except:
        return []

def get_user_alerts(user_id):
    """Get user's active alerts"""
    try:
        conn = sqlite3.connect(ALERTS_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT ticker, target_price, alert_type FROM alerts WHERE user_id = ? ORDER BY ticker', (user_id,))
        alerts = cursor.fetchall()
        conn.close()
        
        alerts_data = []
        for alert in alerts:
            ticker = alert['ticker']
            target_price = alert['target_price']
            alert_type = alert['alert_type']
            current_price = get_stock_price(ticker)
            
            if current_price:
                distance = abs(current_price - target_price)
            else:
                distance = None
            
            alerts_data.append({
                'ticker': ticker,
                'target_price': target_price,
                'alert_type': alert_type,
                'current_price': current_price if current_price else 'N/A',
                'distance': distance
            })
        
        return alerts_data
    except:
        return []

# Routes
@app.route('/')
def home():
    # Check if user is logged in
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login')
def login():
    """Redirect to Discord OAuth"""
    discord_login_url = f"{DISCORD_OAUTH_URL}?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify"
    return redirect(discord_login_url)

@app.route('/callback')
def callback():
    """Handle Discord OAuth callback"""
    code = request.args.get('code')
    
    if not code:
        return "Error: No code provided", 400
    
    # Exchange code for access token
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(DISCORD_TOKEN_URL, data=data, headers=headers)
    
    if response.status_code != 200:
        return f"Error getting token: {response.text}", 400
    
    token_data = response.json()
    access_token = token_data['access_token']
    
    # Get user info
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    user_response = requests.get(DISCORD_USER_URL, headers=headers)
    
    if user_response.status_code != 200:
        return "Error getting user info", 400
    
    user_data = user_response.json()
    
    # Store user info in session
    session['user_id'] = user_data['id']
    session['username'] = user_data['username']
    session['avatar'] = user_data.get('avatar')
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard - requires login"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    username = session.get('username', 'User')
    
    portfolio_data = get_user_portfolio(user_id)
    
    if not portfolio_data:
        return render_template('no_account.html', username=username)
    
    watchlist_data = get_user_watchlist(user_id)
    alerts_data = get_user_alerts(user_id)
    
    return render_template('portfolio.html', 
                         data=portfolio_data, 
                         watchlist=watchlist_data,
                         alerts=alerts_data,
                         user_id=user_id,
                         username=username)

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)