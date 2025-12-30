import copy
import numpy as np

class GreeksEngine:
    """
    Finite-difference Greeks engine for option portfolios.
    """

    def __init__(self, portfolio, pricer, surface, r=0.0):
        self.portfolio = portfolio
        self.pricer = pricer
        self.surface = surface
        self.r = r

        self.base_spot = surface.spot
        self.base_value = pricer.price(portfolio, self.base_spot, surface)

    # ---------- SPOT GREEKS ---------- #

    def delta(self, bump=0.01):
        """
        First-order spot sensitivity.
        bump = relative bump, e.g. 0.01 = 1%
        """
        spot_up = self.base_spot * (1 + bump)
        spot_dn = self.base_spot * (1 - bump)

        v_up = self.pricer.price(self.portfolio, spot_up, self.surface)
        v_dn = self.pricer.price(self.portfolio, spot_dn, self.surface)

        delta = (v_up - v_dn) / (spot_up - spot_dn)
        return delta

    def gamma(self, bump=0.01):
        """
        Second-order spot sensitivity.
        """
        spot_up = self.base_spot * (1 + bump)
        spot_dn = self.base_spot * (1 - bump)

        v_up = self.pricer.price(self.portfolio, spot_up, self.surface)
        v_mid = self.base_value
        v_dn = self.pricer.price(self.portfolio, spot_dn, self.surface)

        gamma = (v_up - 2 * v_mid + v_dn) / ((spot_up - self.base_spot) ** 2)
        return gamma

    # ---------- VOL GREEKS ---------- #

    def vega(self, vol_bump=0.01):
        """
        Parallel vol surface bump (absolute vol).
        vol_bump = 0.01 = +1 vol point
        """
        bumped_surface = copy.deepcopy(self.surface)
        bumped_surface.bump_parallel(vol_bump)

        v_up = self.pricer.price(self.portfolio, self.base_spot, bumped_surface)

        vega = (v_up - self.base_value) / vol_bump
        return vega

    # ---------- TIME GREEK ---------- #

    def theta(self, dt=1/252):
        """
        One-day time decay.
        dt in years (1/252 ≈ one trading day)
        """
        decayed_surface = copy.deepcopy(self.surface)
        decayed_surface.roll_down(dt)

        v_new = self.pricer.price(self.portfolio, self.base_spot, decayed_surface)

        theta = v_new - self.base_value
        return theta

    # ---------- SUMMARY ---------- #

    def compute_all(self):
        """
        Compute main Greeks in one call.
        """
        return {
            "delta": self.delta(),
            "gamma": self.gamma(),
            "vega": self.vega(),
            "theta": self.theta()
        }
