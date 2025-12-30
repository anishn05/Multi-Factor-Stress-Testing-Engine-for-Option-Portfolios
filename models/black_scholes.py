import numpy as np
from scipy.stats import norm


def bs_price(spot: float, strike: float, maturity: float, rate: float, vol: float, option_type: str) -> float:
    """
    Black-Scholes price for European options.

    Parameters
    ----------
    spot : float
        Current spot price
    strike : float
        Option strike
    maturity : float
        Time to maturity in years
    rate : float
        Risk-free interest rate
    vol : float
        Implied volatility
    option_type : str
        'call' or 'put'
    """

    if maturity <= 0:
        if option_type == "call":
            return max(spot - strike, 0.0)
        elif option_type == "put":
            return max(strike - spot, 0.0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

    d1 = (
        np.log(spot / strike)
        + (rate + 0.5 * vol ** 2) * maturity
    ) / (vol * np.sqrt(maturity))

    d2 = d1 - vol * np.sqrt(maturity)

    if option_type == "call":
        price = spot * norm.cdf(d1) - strike * np.exp(-rate * maturity) * norm.cdf(d2)
    elif option_type == "put":
        price = strike * np.exp(-rate * maturity) * norm.cdf(-d2) - spot * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    return price

def stress_pnl(portfolio, surface, stress_engine, shock, r=0.0):
    """
    portfolio: OptionPortfolio or iterable of EuropeanOption objects
    surface: ImpliedVolSurface
    stress_engine: SurfaceStressEngine
    shock: dict defining surface shock
    """
    stressed_surface = stress_engine.apply_shock(shock)
    total_pnl = 0.0

    for option in portfolio:
        S = surface.spot
        K = option.strike
        T = option.maturity
        qty = option.quantity
        opt_type = option.option_type  # 'call' or 'put'

        sigma_base = surface.get_vol(K, T)
        sigma_stressed = stressed_surface.get_vol(K, T)

        price_base = bs_price(
            S, K, T, r, sigma_base, opt_type
        )

        price_stressed = bs_price(
            S, K, T, r, sigma_stressed, opt_type
        )

        total_pnl += (price_stressed - price_base) * qty

    return total_pnl

