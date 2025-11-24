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