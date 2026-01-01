from market_data.spot import SpotData
from market_data.option_chain import OptionChainLoader
from market_data.vol_surface import ImpliedVolSurface
from engine.pricer import PortfolioPricer

def build_context(ticker="SPY", rate=0.04):
    """
    Build cached market context: spot, vol surface, pricer, interest rate.
    Portfolio is NOT included — it's user-dependent and must be passed in at runtime.
    """
    # --- Spot ---
    spot_loader = SpotData(ticker)
    spot_loader.fetch(start_date="2023-01-01")
    spot = spot_loader.latest_spot()

    # --- Vol surface ---
    chain_loader = OptionChainLoader(ticker)
    expiries = chain_loader.get_expirations()[:15]
    option_chains = chain_loader.get_option_chain_for_surface(expiries)

    surface = ImpliedVolSurface(spot)
    surface.build_from_option_chains(option_chains)

    # --- Pricing engine ---
    pricer = PortfolioPricer(rate=rate)

    return {
        "spot": spot,
        "surface": surface,
        "pricer": pricer,
        "rate": rate,
        "chain_loader": chain_loader
    }
