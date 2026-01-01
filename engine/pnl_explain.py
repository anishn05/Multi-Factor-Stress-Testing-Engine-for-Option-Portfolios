import copy
from models.black_scholes import bs_price
from models.greeks import GreeksEngine
from stress.vol_stress import SurfaceStressEngine


class PnLExplain:
    """
    Industry-style PnL Explain:
    - Spot PnL via Delta + Gamma
    - Vol PnL via repricing (true Vega)
    - Theta via roll-down
    - Residual captures higher-order terms
    """

    def __init__(self, portfolio, pricer, surface, r=0.0):
        self.portfolio = portfolio
        self.pricer = pricer
        self.surface = surface
        self.r = r

        self.base_spot = surface.spot
        self.base_value = pricer.price(portfolio, self.base_spot, surface)

    def explain(self, shocked_spot=None, vol_shocks=None, dt=1/252):
        """
        Parameters
        ----------
        shocked_spot : float
            Scenario spot
        vol_shocks : list[dict]
            Same structure as scenario engine
        dt : float
            Time step in years (theta)

        Returns
        -------
        dict : PnL explain components
        """

        # -------------------------
        # 1. Base Greeks (LOCAL)
        # -------------------------
        greeks_engine = GreeksEngine(
            portfolio=self.portfolio,
            pricer=self.pricer,
            surface=self.surface,
            r=self.r
        )
        greeks = greeks_engine.compute_all()

        # -------------------------
        # 2. Shocked spot
        # -------------------------
        spot_new = shocked_spot if shocked_spot is not None else self.base_spot
        dS = spot_new - self.base_spot

        # -------------------------
        # 3. Spot PnL (Taylor)
        # -------------------------
        delta_pnl = greeks["delta"] * dS
        gamma_pnl = 0.5 * greeks["gamma"] * dS ** 2

        # -------------------------
        # 4. Vega PnL (REPRICING)
        # -------------------------
        vega_pnl = 0.0
        surface_vol = self.surface

        if vol_shocks:
            stress_engine = SurfaceStressEngine(self.surface)
            surface_vol = copy.deepcopy(self.surface)

            for shock in vol_shocks:
                surface_vol = stress_engine.apply_shock(shock)

            value_vol = self.pricer.price(
                self.portfolio,
                self.base_spot,
                surface_vol
            )
            vega_pnl = value_vol - self.base_value

        # -------------------------
        # 5. Theta PnL
        # -------------------------
        theta_pnl = greeks["theta"] * dt

        # -------------------------
        # 6. Full Repricing (Truth)
        # -------------------------
        value_new = self.pricer.price(
            self.portfolio,
            spot_new,
            surface_vol
        )
        total_pnl = value_new - self.base_value

        # -------------------------
        # 7. Residual
        # -------------------------
        explained = delta_pnl + gamma_pnl + vega_pnl + theta_pnl
        residual = total_pnl - explained

        return {
            "Total Pnl": total_pnl,
            "Delta Pnl": delta_pnl,
            "Gamma Pnl": gamma_pnl,
            "Vega Pnl": vega_pnl,
            "Theta Pnl": theta_pnl,
            "Residual": residual
        }
