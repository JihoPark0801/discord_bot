import yfinance as yf


def get_stock_price(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        data = stock.history(period="1d")
        if data.empty:
            return None
        
        price = data['Close'].iloc[-1]
        return float(price)
    
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return None

def get_percentage_change(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        data = stock.history(period="2d")
        if len(data) < 2:
            return None
        
        previous_close = data['Close'].iloc[-2]
        current_close = data['Close'].iloc[-1]
        percentage_change = ((current_close - previous_close) / previous_close) * 100
        return float(percentage_change)
    
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return None