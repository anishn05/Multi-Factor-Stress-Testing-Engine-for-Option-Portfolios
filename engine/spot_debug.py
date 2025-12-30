from models.black_scholes import bs_price
import pandas as pd
import numpy as np


def spot_debug_report(
    portfolio,
    surface,
    spot,
    spot_shock_pct,
    rate=0.0,
    verbose=True
):
    """
    Detailed per-option PnL breakdown under spot shock.
    """

    shocked_spot = spot * (1 + spot_shock_pct)
    rows = []

    for opt in portfolio:
        K = opt.strike
        T = opt.maturity
        qty = opt.quantity
        opt_type = opt.option_type

        # Vol must be queried with the SAME surface, but using new spot
        sigma_base = surface.get_vol(K, T)
        sigma_shocked = surface.get_vol(K, T)

        price_base = bs_price(
            spot, K, T, rate, sigma_base, opt_type
        )

        price_shocked = bs_price(
            shocked_spot, K, T, rate, sigma_shocked, opt_type
        )

        pnl = (price_shocked - price_base) * qty

        # Intrinsic values for sanity check
        if opt_type == "call":
            intrinsic_base = max(spot - K, 0.0)
            intrinsic_shocked = max(shocked_spot - K, 0.0)
            delta_sign = +1
        else:
            intrinsic_base = max(K - spot, 0.0)
            intrinsic_shocked = max(K - shocked_spot, 0.0)
            delta_sign = -1

        delta_approx = delta_sign * qty

        rows.append({
            "strike": K,
            "type": opt_type,
            "qty": qty,
            "T": round(T, 4),
            "price_base": round(price_base, 4),
            "price_shocked": round(price_shocked, 4),
            "pnl": round(pnl, 2),
            "intrinsic_base": round(intrinsic_base, 4),
            "intrinsic_shocked": round(intrinsic_shocked, 4),
            "delta_direction": delta_approx
        })

    df = pd.DataFrame(rows)
    total_pnl = df["pnl"].sum()

    if verbose:
        print("\n=== Spot Shock Debug Report ===")
        print(f"Spot base: {spot:.2f}")
        print(f"Spot shocked: {shocked_spot:.2f} ({spot_shock_pct*100:.1f}%)\n")
        print(df.to_string(index=False))
        print("\nTotal PnL:", round(total_pnl, 2))

    return df
