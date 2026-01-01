from stress.spot_stress import SpotStressEngine
from stress.vol_stress import SurfaceStressEngine
import copy

class ScenarioEngine:
    """
    Apply combined spot and vol shocks as a scenario.
    """

    def __init__(self, portfolio, pricer, surface, rate=0.0):
        self.portfolio = portfolio
        self.pricer = pricer
        self.surface = surface
        self.rate = rate
        self.base_spot = surface.spot
        self.base_value = pricer.price(portfolio, self.base_spot, surface)
        self.spot_engine = SpotStressEngine(portfolio, pricer, surface, r=rate)
        self.vol_engine = SurfaceStressEngine(surface)

    def apply_scenario(self, spot_shift=0.0, vol_shocks=None):
        """
        Apply spot and vol shocks together.
        spot_shift: percentage, e.g. 0.01 = +1%
        vol_shocks: list of vol shock dicts
        """
        # 1️⃣ Spot move
        shocked_spot = self.base_spot * (1 + spot_shift)

        # 2️⃣ Copy surface and apply vol shocks sequentially
        stressed_surface = copy.deepcopy(self.surface)
        if vol_shocks:
            for shock in vol_shocks:
                stressed_surface = self.vol_engine.apply_shock(shock)

        # 3️⃣ Price portfolio at shocked spot and stressed vol
        total_value = self.pricer.price(self.portfolio, shocked_spot, stressed_surface)
        pnl = total_value - self.base_value

        return total_value, pnl, shocked_spot, stressed_surface
