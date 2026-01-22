import sqlite3

DB_PATH = 'portfolio.db'

def initialize_portfolio_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            cash_balance REAL NOT NULL DEFAULT 100000.0,
            starting_balance REAL NOT NULL DEFAULT 100000.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            ticker TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            avg_cost REAL NOT NULL,
            UNIQUE(user_id, ticker),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            ticker TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total_cost REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

def create_user(user_id, starting_balance = 100000.0):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (user_id, cash_balance, starting_balance) VALUES (?, ?, ?)', (user_id, starting_balance, starting_balance))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        if conn:
            conn.close()

def user_exists(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT cash_balance, starting_balance, created_at FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_cash_balance(user_id, new_balance):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET cash_balance = ? WHERE user_id = ?', (new_balance, user_id))
    conn.commit()
    conn.close()

def get_user_portfolio(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT ticker, quantity, avg_cost FROM portfolio WHERE user_id = ? ORDER BY ticker', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_position(user_id, ticker):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT quantity, avg_cost FROM portfolio WHERE user_id = ? AND ticker = ?', (user_id, ticker))
    row = cursor.fetchone()
    conn.close()
    return row

def add_or_update_position(user_id, ticker, quantity, price):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT quantity, avg_cost FROM portfolio WHERE user_id = ? AND ticker = ?', (user_id, ticker))
    row = cursor.fetchone()
    if row:
        existing_quantity = row[0]
        existing_avg_cost = row[1]
        new_avg_cost = (existing_quantity * existing_avg_cost + quantity * price) / (existing_quantity + quantity)
        new_quantity = existing_quantity + quantity
        cursor.execute('UPDATE portfolio SET avg_cost = ?, quantity = ? WHERE user_id = ? AND ticker = ?', (new_avg_cost, new_quantity, user_id, ticker))
    else:
        cursor.execute("INSERT INTO portfolio (user_id, ticker, quantity, avg_cost) VALUES (?,?,?,?)", (user_id, ticker, quantity, price))

    conn.commit()
    conn.close()

def reduce_or_remove_position(user_id, ticker, quantity):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT quantity FROM portfolio WHERE user_id = ? AND ticker = ?', (user_id, ticker))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return False
    
    if quantity > row[0]:
        conn.close()
        return False
    
    if row[0] == quantity:
        cursor.execute('DELETE FROM portfolio WHERE user_id = ? AND ticker = ?', (user_id,ticker))
    else:
        new_quantity = row[0] - quantity
        cursor.execute('UPDATE portfolio SET quantity = ? WHERE user_id = ? AND ticker = ?',(new_quantity, user_id, ticker))
    conn.commit()
    conn.close()
    return True

def record_transaction(user_id, ticker, transaction_type, quantity, price, total_cost):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO transactions (user_id, ticker, transaction_type, quantity, price, total_cost) VALUES (?,?,?,?,?,?)', (user_id, ticker, transaction_type, quantity, price, total_cost))
    conn.commit()
    conn.close()

def get_user_transactions(user_id, ticker=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if ticker is None:
        cursor.execute('SELECT ticker, transaction_type, quantity, price, total_cost, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC', (user_id,))
    else:
        cursor.execute('SELECT ticker, transaction_type, quantity, price, total_cost, timestamp FROM transactions WHERE user_id = ? AND ticker = ? ORDER BY timestamp DESC', (user_id, ticker))
    
    rows = cursor.fetchall()
    conn.close()
    return rows

def reset_portfolio(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT starting_balance FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return False
    
    starting_balance = row[0]

    cursor.execute('DELETE FROM portfolio WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM transactions WHERE user_id = ?', (user_id,))
    cursor.execute('UPDATE users SET cash_balance = ? WHERE user_id = ?', (starting_balance, user_id))
    conn.commit()
    conn.close()
    return True