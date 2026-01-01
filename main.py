from market_data.spot import SpotData
from market_data.option_chain import OptionChainLoader
from market_data.vol_surface import ImpliedVolSurface
from engine.pricer import PortfolioPricer
from engine.pnl_explain import PnLExplain
from stress.scenario_engine import ScenarioEngine
from diagnostics.data_split import split_option_chains
from diagnostics.greek_diagnostics import GreekValidityDiagnostics
from plots.plots import plot_scenario_dashboard
import copy

# =============================
# Helper Functions
# =============================

def normalize_greeks(greeks, portfolio, portfolio_value):
    """
    Normalize Greeks for reporting:
    - Total
    - Per contract
    - % of portfolio value
    """

    total_contracts = sum(opt.quantity * opt.contract_size for opt in portfolio)

    normalized = {}

    for greek in ["delta", "gamma", "vega", "theta"]:
        normalized[f"{greek}_total"] = greeks[greek]
        normalized[f"{greek}_per_contract"] = greeks[greek] / total_contracts
        normalized[f"{greek}_pct_portfolio"] = greeks[greek] / portfolio_value

    return normalized


# =============================
# Main Workflow
# =============================

def main():

    # -----------------------------
    # Global Parameters
    # -----------------------------
    underlying = "SPY"
    rate = 0.04

    # -----------------------------
    # 1. Load Spot Price
    # -----------------------------
    spot_loader = SpotData(underlying)
    spot_loader.fetch(start_date="2023-01-01")
    spot = spot_loader.latest_spot()

    print(f"\nLatest spot for {underlying}: {spot:.2f}")
    # -----------------------------
    # 2. Load Option Chains & Build Portfolio
    # -----------------------------
    chain_loader = OptionChainLoader(underlying)
    expiries = chain_loader.get_expirations()

    target_expiry = expiries[10]
    portfolio = chain_loader.build_portfolio(
        expiry=target_expiry,
        spot=spot,
        base_size=10
    )

    print(f"Portfolio contains {len(portfolio)} option positions")
    # -----------------------------
    # 3. Build Implied Volatility Surface
    # -----------------------------
    surface_expiries = expiries[:15]
    option_chains = chain_loader.get_option_chain_for_surface(surface_expiries)

    calibration_chains, validation_chains = split_option_chains(option_chains)

    surface = ImpliedVolSurface(spot)
    surface.build_from_option_chains(calibration_chains)

    # -----------------------------
    # 4. Base Portfolio Valuation
    # -----------------------------
    pricer = PortfolioPricer(rate=rate)
    base_value = pricer.price(portfolio, spot, surface)

    print(f"Base portfolio value: {base_value:,.2f}")

    # -----------------------------
    # 5. Initialize Stress & Explain Engines
    # -----------------------------
    scenario_engine = ScenarioEngine(
        portfolio=portfolio,
        pricer=pricer,
        surface=surface,
        rate=rate
    )

    pnl_explainer = PnLExplain(
        portfolio=portfolio,
        pricer=pricer,
        surface=surface,
        r=rate
    )

    # -----------------------------
    # 6. Define Stress Scenarios
    # -----------------------------
    scenarios = [
        {
            "name": "Mild Up + Vol Expansion",
            "spot_shift": 0.01,
            "vol_shocks": [{"type": "parallel", "value": 0.05}]
        },
        {
            "name": "Equity Selloff + Vol Compression",
            "spot_shift": -0.05,
            "vol_shocks": [
                {"type": "parallel", "value": -0.05},
                {"type": "skew", "value": 0.02}
            ]
        }
    ]

    # -----------------------------
    # 7. Run Stress Scenarios
    # -----------------------------
    print("\n================ STRESS TEST RESULTS ================\n")

    for idx, scenario in enumerate(scenarios, 1):

        # --- Apply Scenario ---
        stressed_value, pnl, shocked_spot, stressed_surface = (
            scenario_engine.apply_scenario(
                spot_shift=scenario["spot_shift"],
                vol_shocks=scenario["vol_shocks"]
            )
        )

        # --- PnL Explain ---
        pnl_breakdown = pnl_explainer.explain(
            shocked_spot=shocked_spot,
            vol_shocks=scenario["vol_shocks"]
        )

        # --- Greek Validity Diagnostics ---
        validator = GreekValidityDiagnostics(
            base_spot=surface.spot,
            shocked_spot=shocked_spot,
            base_value=base_value,
            pnl_breakdown=pnl_breakdown,
            portfolio=portfolio
        )
        diagnostics = validator.run()

        # =============================
        # 8. Reporting Output (Firm-Grade)
        # =============================

        print(f"Scenario {idx}: {scenario['name']}")
        print("--------------------------------------------------")
        print(f"Spot shock:        {scenario['spot_shift']*100:+.1f}%")
        print(f"Vol shocks:        {scenario['vol_shocks']}")
        print(f"Base value:        {base_value:,.2f}")
        print(f"Stressed value:    {stressed_value:,.2f}")
        print(f"PnL impact:        {pnl:,.2f}")
        print("\nPnL Attribution:")
        for k, v in pnl_breakdown.items():
            print(f"  {k:<12}: {v:,.2f}")

        print("\nModel Validity Diagnostics:")
        for k, v in diagnostics.items():
            print(f"  {k:<25}: {v}")
        
        plot_scenario_dashboard(
        scenario_name=f"Scenario {idx}",
        base_spot=surface.spot,
        shocked_spot=shocked_spot,
        true_pnl=pnl,
        pnl_breakdown=pnl_breakdown
    )

        print("==================================================\n")

if __name__ == "__main__":
    main()