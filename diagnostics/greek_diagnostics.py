#Runs diagnostics to check validaity of the computed greeks

class GreekValidityDiagnostics:
    def __init__(
        self,
        base_spot,
        shocked_spot,
        base_value,
        pnl_breakdown,
        portfolio
    ):
        self.base_spot = base_spot
        self.shocked_spot = shocked_spot
        self.base_value = base_value
        self.pnl = pnl_breakdown
        self.portfolio = portfolio

    def run(self):
        diagnostics = {}

        # --- Spot move check ---
        spot_move_pct = abs(self.shocked_spot - self.base_spot) / self.base_spot
        diagnostics["spot_move_pct"] = spot_move_pct
        diagnostics["spot_valid"] = spot_move_pct <= 0.03

        # --- Residual check ---
        total_pnl = self.pnl["Total Pnl"]
        residual = self.pnl["Residual"]

        residual_ratio = (
            abs(residual) / abs(total_pnl)
            if abs(total_pnl) > 1e-6 else 0.0
        )

        diagnostics["residual_ratio"] = residual_ratio
        diagnostics["residual_valid"] = residual_ratio <= 0.2

        # --- Gamma dominance ---
        gamma_ratio = (
            abs(self.pnl["Gamma Pnl"]) / abs(total_pnl)
            if abs(total_pnl) > 1e-6 else 0.0
        )

        diagnostics["gamma_ratio"] = gamma_ratio
        diagnostics["gamma_valid"] = gamma_ratio <= 0.5

        # --- Time-to-expiry ---
        min_T = min(opt.maturity for opt in self.portfolio)
        diagnostics["min_maturity_days"] = min_T * 252
        diagnostics["expiry_valid"] = min_T >= 5 / 252

        # --- Overall verdict ---
        diagnostics["greeks_trustworthy"] = all([
            diagnostics["spot_valid"],
            diagnostics["residual_valid"],
            diagnostics["gamma_valid"],
            diagnostics["expiry_valid"]
        ])

        return diagnostics
