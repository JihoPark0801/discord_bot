import sqlite3

DB_PATH = 'watchlist.db'

def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            ticker TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, ticker)
        )
    ''')
    conn.commit()
    conn.close()

def add_to_watchlist(user_id, ticker):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO watchlist (user_id, ticker) VALUES (?, ?)', (user_id, ticker))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    
def remove_from_watchlist(user_id, ticker):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM watchlist WHERE user_id = ? AND ticker = ?', (user_id, ticker))
    rows_deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_deleted > 0

def get_watchlist(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT ticker, added_at FROM watchlist WHERE user_id = ? ORDER BY added_at', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_watchlist_count(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM watchlist WHERE user_id = ?', (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def clear_watchlist(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM watchlist WHERE user_id = ?', (user_id,))
    row_count = cursor.rowcount
    conn.commit()
    conn.close()
    return row_count
