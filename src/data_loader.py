import yfinance as yf
import pandas as pd
import time

class DataLoader:
    def __init__(self, tickers, interval='1d', period='1y'):
        # Ensure tickers is a list
        if isinstance(tickers, str):
            self.tickers = [tickers]
        else:
            self.tickers = tickers
            
        self.interval = interval
        self.period = period
        self.data = {} # Dictionary mapping ticker -> DataFrame

    def fetch_history(self):
        """Fetches historical data for all tickers."""
        print(f"Fetching data for {len(self.tickers)} tickers...")
        
        # yfinance can download multiple tickers at once
        # group_by='ticker' makes it easier to separate them
        raw_data = yf.download(self.tickers, period=self.period, interval=self.interval, group_by='ticker', progress=False)
        
        if len(self.tickers) == 1:
            # If single ticker, yfinance returns a single DF, not grouped
            ticker = self.tickers[0]
            if raw_data.empty:
                 raise ValueError(f"No data found for {ticker}")
            raw_data.index = pd.to_datetime(raw_data.index)
            # Flatten columns if MultiIndex (Price, Ticker) -> Price
            if isinstance(raw_data.columns, pd.MultiIndex):
                 # If single ticker but MultiIndex, it might be (Price, Ticker) or just Price
                 # With group_by='ticker', it shouldn't be MultiIndex for single ticker usually, 
                 # but let's be safe.
                 pass 
            self.data[ticker] = raw_data
        else:
            # Split the big DataFrame into a dict of DataFrames
            for ticker in self.tickers:
                try:
                    df = raw_data[ticker].copy()
                    if df.empty:
                        print(f"Warning: No data for {ticker}")
                        continue
                    df.dropna(how='all', inplace=True) # Drop rows where all cols are NaN
                    df.index = pd.to_datetime(df.index)
                    self.data[ticker] = df
                except KeyError:
                    print(f"Warning: Could not extract data for {ticker}")

        print(f"Loaded data for {len(self.data)} tickers.")
        return self.data

    def get_latest_candles(self):
        """
        Generator that yields a dictionary of {ticker: candle} for each timestamp.
        Simulates the market moving forward in time.
        """
        if not self.data:
            self.fetch_history()
            
        # Find the common index (timestamps)
        # We take the union of all indices to handle slightly misaligned data
        all_indices = sorted(set().union(*[df.index for df in self.data.values()]))
        
        for timestamp in all_indices:
            snapshot = {}
            for ticker, df in self.data.items():
                if timestamp in df.index:
                    snapshot[ticker] = df.loc[timestamp]
            
            if snapshot:
                yield timestamp, snapshot

    def fetch_snapshot(self):
        """
        Fetches the absolute latest price for the scanner (Real-time).
        For simulation, we might not use this, but good for the 'Scanner' mode.
        """
        # For now, just re-download the last 1 day
        data = yf.download(self.tickers, period='1d', interval='1m', group_by='ticker', progress=False)
        snapshot = {}
        
        if len(self.tickers) == 1:
             ticker = self.tickers[0]
             if not data.empty:
                 snapshot[ticker] = data.iloc[-1]
        else:
            for ticker in self.tickers:
                try:
                    df = data[ticker]
                    if not df.empty:
                        snapshot[ticker] = df.iloc[-1]
                except KeyError:
                    pass
        return snapshot
