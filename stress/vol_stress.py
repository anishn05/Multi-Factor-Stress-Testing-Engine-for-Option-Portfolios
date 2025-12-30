import copy
import numpy as np
from scipy.interpolate import interp1d

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