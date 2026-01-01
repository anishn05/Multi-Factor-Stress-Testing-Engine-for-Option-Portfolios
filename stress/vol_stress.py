import copy
import numpy as np
from scipy.interpolate import interp1d
from models.black_scholes import bs_price

class SurfaceStressEngine:
    def __init__(self, surface):
        """
        surface: ImpliedVolSurface instance
        """
        self.surface = surface

    def _shock_interpolator(self, f_interp, strikes, shock):
        """
        Apply additive shock to interpolator output
        f_interp: interp1d object
        strikes: array of strikes
        shock: dict with keys 'type' and 'value'
            type: 'parallel', 'skew', 'curvature'
        """
        vols = f_interp(strikes)

        if shock['type'] == 'parallel':
            vols_stressed = vols + shock['value']
        elif shock['type'] == 'skew':
            # linear slope across strikes
            mid = np.mean(strikes)
            vols_stressed = vols + shock['value'] * (strikes - mid)/mid
        elif shock['type'] == 'curvature':
            mid = np.mean(strikes)
            vols_stressed = vols + shock['value'] * ((strikes - mid)/mid)**2
        else:
            raise ValueError("Unknown shock type")

        return vols_stressed

    def apply_shock(self, shock):
        """
        Returns a new stressed surface instance
        shock: dict as above
        """
        stressed_surface = copy.deepcopy(self.surface)
        for T, f_interp in stressed_surface.surface.items():
            strikes = f_interp.x  # interp1d stores input points in .x
            vols_stressed = self._shock_interpolator(f_interp, strikes, shock)
            stressed_surface.surface[T] = interp1d(
                strikes,
                vols_stressed,
                kind='cubic',
                fill_value='extrapolate'
            )
        return stressed_surface
    

    def vol_stress_pnl(portfolio, surface, stress_engine, shock, r=0.0):
        """
        portfolio: OptionPortfolio or iterable of EuropeanOption objects
        surface: ImpliedVolSurface
        stress_engine: SurfaceStressEngine
        shock: dict defining surface shock
        """
        stressed_surface = stress_engine.apply_shock(shock)
        total_pnl = 0.0

        for option in portfolio:
            S = surface.spot
            K = option.strike
            T = option.maturity
            qty = option.quantity
            opt_type = option.option_type  # 'call' or 'put'

            sigma_base = surface.get_vol(K, T)
            sigma_stressed = stressed_surface.get_vol(K, T)

            price_base = bs_price(
                S, K, T, r, sigma_base, opt_type
            )

            price_stressed = bs_price(
                S, K, T, r, sigma_stressed, opt_type
            )

            total_pnl += (price_stressed - price_base) * qty * option.contract_size

        return total_pnl