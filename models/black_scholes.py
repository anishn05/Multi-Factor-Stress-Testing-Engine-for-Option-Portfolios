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

    d1 = (np.log(spot / strike)+ (rate + 0.5 * vol ** 2) * maturity) / (vol * np.sqrt(maturity))
    d2 = d1 - vol * np.sqrt(maturity)

    if option_type == "Call":
        price = spot * norm.cdf(d1) - strike * np.exp(-rate * maturity) * norm.cdf(d2)
    elif option_type == "Put":
        price = strike * np.exp(-rate * maturity) * norm.cdf(-d2) - spot * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'Call' or 'Put'")

    return max(price, 1e-4)



