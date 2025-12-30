import yfinance as yf
import pandas as pd

class SpotData:
    """
    Loads historical spot prices for equities using Yahoo Finance
    """

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.data = None

    def fetch(self, start_date: str = "2020-01-01", end_date: str = None):
        """
        Fetch historical spot prices
        """
        df = yf.download(self.ticker, start=start_date, end=end_date)
        if df.empty:
            raise ValueError(f"No data found for ticker {self.ticker}")

        # Keep only adjusted close
        self.data = df["Close"].copy()
        return self.data

    def latest_spot(self):
        """
        Returns the most recent closing price
        """
        if self.data is None:
            raise ValueError("Data not loaded yet. Run fetch() first.")
        return float(self.data.iloc[-1])

    def get_series(self):
        """
        Return full historical series
        """
        if self.data is None:
            raise ValueError("Data not loaded yet. Run fetch() first.")
        return self.data
