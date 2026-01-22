from flask import Flask, render_template
import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.stocks import get_stock_price

app = Flask(__name__)

DB_PATH = '../portfolio.db'  # Adjust as needed
WATCHLIST_DB_PATH = '../watchlist.db'  # Adjust as needed
ALERTS_DB_PATH = '../alerts.db'  # Adjust as needed

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_portfolio(user_id):
    """Get user's portfolio data with current prices"""
    # ... your existing function stays the same ...
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
            
            # Calculate distance to target
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/portfolio/<user_id>')
def portfolio(user_id):
    portfolio_data = get_user_portfolio(user_id)
    
    if not portfolio_data:
        return "User not found. Please run /portfolio_start in Discord first."
    
    # Get watchlist and alerts
    watchlist_data = get_user_watchlist(user_id)
    alerts_data = get_user_alerts(user_id)
    
    return render_template('portfolio.html', 
                         data=portfolio_data, 
                         watchlist=watchlist_data,
                         alerts=alerts_data,
                         user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True)