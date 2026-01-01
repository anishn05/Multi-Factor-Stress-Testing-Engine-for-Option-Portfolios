from engine.pnl_explain import PnLExplain
from stress.scenario_engine import ScenarioEngine

def run_scenario(context, scenario, portfolio):
    """
    Run a single scenario on a given portfolio.
    """
    surface = context["surface"]
    pricer = context["pricer"]
    rate = context["rate"]
    spot = context["spot"]

    # --- Rebuild engines dynamically per portfolio ---
    pnl_engine = PnLExplain(portfolio, pricer, surface, r=rate)
    scenario_engine = ScenarioEngine(portfolio, pricer, surface, rate)

    # --- Base value ---
    base_value = pricer.price(portfolio, spot, surface)

    # --- Apply scenario ---
    stressed_value, pnl, shocked_spot, stressed_surface = scenario_engine.apply_scenario(
        spot_shift=scenario.get("spot_shift", 0.0),
        vol_shocks=scenario.get("vol_shocks", [])
    )

    # --- PnL explain ---
    pnl_breakdown = pnl_engine.explain(
        shocked_spot=shocked_spot,
        vol_shocks=scenario.get("vol_shocks", [])
    )

    # --- Build plots (your existing plotting function) ---
    from plots.plots import plot_scenario_dashboard
    fig = plot_scenario_dashboard(
        scenario_name=scenario.get("name", "Scenario"),
        base_spot=surface.spot,
        shocked_spot=shocked_spot,
        true_pnl=pnl,
        pnl_breakdown=pnl_breakdown
    )

    # --- Optionally run Greek diagnostics ---
    from diagnostics.greek_diagnostics import GreekValidityDiagnostics
    validator = GreekValidityDiagnostics(
        base_spot=surface.spot,
        shocked_spot=shocked_spot,
        base_value=base_value,
        pnl_breakdown=pnl_breakdown,
        portfolio=portfolio
    )
    diagnostics = validator.run()

    return {
        "base_value": base_value,
        "stressed_value": stressed_value,
        "pnl": pnl,
        "pnl_breakdown": pnl_breakdown,
        "plots": fig,
        "diagnostics": diagnostics
    }
