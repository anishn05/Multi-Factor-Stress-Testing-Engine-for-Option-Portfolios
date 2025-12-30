from models.black_scholes import bs_price


def vol_stress_pnl(portfolio, surface, stress_engine, shock, r=0.0):
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