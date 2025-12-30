import copy
from engine.pricer import PortfolioPricer

class SpotStressEngine:
    """
    Apply spot shocks to an option portfolio and compute PnL impacts.
    """

    def __init__(self, portfolio, pricer, surface, r=0.0):
        """
        Parameters:
        -----------
        portfolio : OptionPortfolio or list of EuropeanOption
        pricer : PortfolioPricer instance
        surface : ImpliedVolSurface instance (base surface)
        r : risk-free rate
        """
        self.portfolio = portfolio
        self.pricer = pricer
        self.surface = surface
        self.r = r
        self.base_spot = surface.spot
        self.base_value = pricer.price(portfolio, self.base_spot, surface)

    def apply_parallel_shocks(self, shock_list):
        """
        Apply multiple parallel spot shocks and compute PnL.

        Parameters:
        -----------
        shock_list : list of floats
            Each float is a percentage move, e.g., 0.01 = +1%, -0.05 = -5%

        Returns:
        --------
        dict : {shock_pct: pnl}
        """
        pnl_results = {}

        for shock in shock_list:
            shocked_spot = self.base_spot * (1 + shock)
            shocked_value = self.pricer.price(self.portfolio, shocked_spot, self.surface)
            pnl = shocked_value - self.base_value
            pnl_results[shock] = pnl

        return pnl_results

    def apply_custom_shock(self, shocked_spot):
        """
        Apply a single custom spot level and compute PnL.

        Returns:
        --------
        float : pnl impact
        """
        shocked_value = self.pricer.price(self.portfolio, shocked_spot, self.surface)
        pnl = shocked_value - self.base_value
        return pnl
