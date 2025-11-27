import yfinance as yf
import pandas as pd

ticker = 'AAPL'
print(f"Fetching {ticker} data (1h, 60d)...")
data = yf.download(ticker, interval='1h', period='60d', progress=False)

print("Shape:", data.shape)
print("Index head:", data.index[:5])
print("Index frequency:", pd.infer_freq(data.index))

if len(data) > 1:
    diff = data.index[1] - data.index[0]
    print("Time difference between first two rows:", diff)
