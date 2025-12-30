import yfinance as yf
from datetime import datetime
from instruments.option import EuropeanOption
from instruments.portfolio import OptionPortfolio
import numpy as np


class OptionChainLoader:
    """
    Loads real option chain and builds realistic trading portfolios
    """

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.ticker_obj = yf.Ticker(ticker)

    def get_expirations(self):
        return self.ticker_obj.options

    def _time_to_maturity(self, expiry: str) -> float:
        expiry_dt = datetime.strptime(expiry, "%Y-%m-%d")
        days = (expiry_dt - datetime.now()).days
        return max(days / 365.0, 0.0)

    def _closest_strike(self, strikes, target):
        return min(strikes, key=lambda x: abs(x - target))
    
    def get_option_chain_for_surface(self, expiries: list, option_type="call"):
        """
        Returns dict[expiry] = DataFrame suitable for vol surface
        """
        chains = {}
        for expiry in expiries:
            chain = self.ticker_obj.option_chain(expiry)
            df = chain.calls if option_type == "call" else chain.puts
            chains[expiry] = df[["strike", "impliedVolatility"]]
        return chains

    def build_portfolio(self, expiry: str, spot: float, base_size: int = 10) -> OptionPortfolio:
        """
        Builds a equity options trading portfolio:
        ATM straddle + OTM wings
        """

        chain = self.ticker_obj.option_chain(expiry)
        calls = chain.calls
        puts = chain.puts

        strikes = sorted(calls["strike"].values)
        maturity = self._time_to_maturity(expiry)

        atm_strike = self._closest_strike(strikes, spot)

        strikes_map = {
            "ATM": atm_strike,
            "+5%": self._closest_strike(strikes, spot * 1.05),
            "-5%": self._closest_strike(strikes, spot * 0.95),
            "+10%": self._closest_strike(strikes, spot * 1.10),
            "-10%": self._closest_strike(strikes, spot * 0.90),
        }

        portfolio = OptionPortfolio()

        # ATM Straddle
        portfolio.add(EuropeanOption(strikes_map["ATM"], maturity, "call", base_size))
        #portfolio.add(EuropeanOption(strikes_map["ATM"], maturity, "put", base_size))

        # Long wings
        #portfolio.add(EuropeanOption(strikes_map["+5%"], maturity, "call", base_size // 2))
        #portfolio.add(EuropeanOption(strikes_map["-5%"], maturity, "put", base_size // 2))

        # Short far wings (risk-financing)
        #portfolio.add(EuropeanOption(strikes_map["+10%"], maturity, "call", -base_size // 5))
        #portfolio.add(EuropeanOption(strikes_map["-10%"], maturity, "put", -base_size // 5))

        return portfolio
