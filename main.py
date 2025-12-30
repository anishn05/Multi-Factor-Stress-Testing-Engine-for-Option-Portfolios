from market_data.spot import SpotData
from market_data.option_chain import OptionChainLoader
from engine.pricer import PortfolioPricer
from market_data.vol_surface import ImpliedVolSurface
from diagnostics.vol_surface_diagnostics import VolSurfaceDiagnostics
from diagnostics.data_split import split_option_chains
from stress.vol_stress import SurfaceStressEngine
from stress.pnl_recalc import vol_stress_pnl
from stress.spot_stress import SpotStressEngine
from models.greeks import GreeksEngine


def main():

    rate = 0.05

    # -----------------------------
    # 1. Load real spot price
    # -----------------------------
    spot_loader = SpotData("AAPL")
    spot_loader.fetch(start_date="2023-01-01")
    spot = spot_loader.latest_spot()
    print(f"Latest spot for AAPL: {spot}")

    # -----------------------------
    # 2. Load real options for first expiry
    # -----------------------------
    chain_loader = OptionChainLoader("AAPL")
    expiry = chain_loader.get_expirations()[0]

    portfolio = chain_loader.build_portfolio(expiry=expiry, spot=spot, base_size=10)
    print(f"Portfolio size: {len(portfolio)} options")

    # -----------------------------
    # 3. Build vol surface (flat for now)
    # -----------------------------
    expiries = chain_loader.get_expirations()[:15]  # first 3 maturities
    option_chains = chain_loader.get_option_chain_for_surface(expiries)
    calibration_chains, validation_chains = split_option_chains(option_chains)

    surface = ImpliedVolSurface(spot)
    surface.build_from_option_chains(calibration_chains)

    # Diagnostics
    diagnostics = VolSurfaceDiagnostics(surface)
    fit_stats = diagnostics.out_of_sample_fit(validation_chains)

    print("Out-of-sample diagnostics:")
    for k, v in fit_stats.items():
        print(f"{k}: {v:.4f}")

    # -----------------------------
    # 4. Price portfolio
    # -----------------------------
    
    pricer = PortfolioPricer(rate=rate)
    value = pricer.price(portfolio, spot, surface)
    print(f"Portfolio value: {value}")

    # Instantiate stress engine
    stress_engine = SurfaceStressEngine(surface)

    # Define shocks
    shocks = [
        {'type':'parallel','value':0.05},   # +5 vol points
        {'type':'parallel','value':-0.05},  # -5 vol points
        {'type':'skew','value':0.02},       # add slope
        {'type':'curvature','value':0.03}   # add convexity
    ]

    for shock in shocks:
        pnl = vol_stress_pnl(portfolio, surface, stress_engine, shock)
        print(f"Shock: {shock}, PnL impact: {pnl:.2f}")

    # Initialize spot stress engine
    spot_stress = SpotStressEngine(portfolio, pricer, surface, rate)

    # Apply parallel shocks: ±1%, ±5%
    shocks = [0.01, -0.01, 0.05, -0.05]
    spot_pnls = spot_stress.apply_parallel_shocks(shocks)

    for shock_pct, pnl in spot_pnls.items():
        print(f"Spot shock: {shock_pct*100:.1f}%, PnL impact: {pnl:.2f}")
    
    
    from engine.spot_debug import spot_debug_report

    spot_debug_report(
        portfolio=portfolio,
        surface=surface,
        spot=spot,
        spot_shock_pct=-0.05,
        rate=rate
    )



    """
    greeks_engine = GreeksEngine(
    portfolio=portfolio,
    pricer=pricer,
    surface=surface,
    r=0.02
    )

    greeks = greeks_engine.compute_all()

    print("Portfolio Greeks:")
    for k, v in greeks.items():
        print(f"{k}: {v:.4f}")
    """

if __name__ == "__main__":
    main()
