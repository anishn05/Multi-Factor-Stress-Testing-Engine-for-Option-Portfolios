#Prints the debug report for every scenario if analysis is required

def scenario_debug_report(portfolio, pricer, surface, shocked_spot, base_spot=None, r=0.0):
    """
    Print per-option breakdown for a shocked spot scenario.
    """
    if base_spot is None:
        base_spot = surface.spot

    print(f"\n=== Scenario Debug Report ===")
    print(f"Base spot: {base_spot:.2f}")
    print(f"Shocked spot: {shocked_spot:.2f} ({(shocked_spot/base_spot-1)*100:.2f}%)\n")
    print(f"{'strike':>8} {'type':>6} {'qty':>6} {'T':>6} {'price_base':>12} {'price_shocked':>14} {'pnl':>10}")

    total_pnl = 0.0
    total_value = 0.0

    for opt in portfolio:
        price_base = pricer.price([opt], base_spot, surface)
        price_shocked = pricer.price([opt], shocked_spot, surface)
        pnl = (price_shocked - price_base) * opt.quantity * opt.contract_size

        total_pnl += pnl
        total_value += price_shocked * opt.quantity * opt.contract_size

        print(f"{opt.strike:8.2f} {opt.option_type:6} {opt.quantity:6} {opt.maturity:6.4f} "
              f"{price_base:12.4f} {price_shocked:14.4f} {pnl:10.2f}")

    print(f"\nTotal PnL: {total_pnl:.2f}")
    print(f"Total portfolio value: {total_value:.2f}")

    return total_pnl, total_value
