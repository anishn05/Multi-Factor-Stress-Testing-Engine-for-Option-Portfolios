import numpy as np
from scipy.interpolate import interp1d
from datetime import datetime
import copy

class Smile:
    """
    Thin wrapper around interp1d that stores
    the data needed for bumps and roll-down.
    """
    def __init__(self, x, y, kind="cubic"):
        self.x = np.asarray(x)
        self.y = np.asarray(y)
        self.kind = kind

        self.fn = interp1d(
            self.x,
            self.y,
            kind=kind,
            fill_value="extrapolate"
        )

    def __call__(self, z):
        return self.fn(z)


class ImpliedVolSurface:
    """
    Fast, realistic implied volatility surface built from market option chains.
    Interpolates in log-moneyness and maturity.
    """

    def __init__(self, spot: float):
        self.spot = float(spot)
        self.surface = {}  # maturity -> interpolator

    @staticmethod
    def _time_to_maturity(expiry: str) -> float:
        expiry_dt = datetime.strptime(expiry, "%Y-%m-%d")
        days = (expiry_dt - datetime.now()).days
        return max(days / 365.0, 0.0)

    def build_from_option_chains(self, option_chains: dict):
        """
        option_chains: dict[expiry] = DataFrame (calls OR puts)
        Each DataFrame must contain:
        - 'strike'
        - 'impliedVolatility'
        """

        for expiry, df in option_chains.items():
            maturity = self._time_to_maturity(expiry)

            df = df.copy()
            df = df[df["impliedVolatility"].notna()]
            df = df[df["impliedVolatility"] > 0]

            strikes = df["strike"].astype(float).values
            vols = df["impliedVolatility"].astype(float).values

            log_moneyness = np.log(strikes / self.spot)

            # Sort for stable interpolation
            order = np.argsort(log_moneyness)
            log_moneyness = log_moneyness[order]
            vols = vols[order]

            # Linear interpolation in log-moneyness

            """
            interp = interp1d(
                log_moneyness,
                vols,
                kind="linear",
                fill_value="extrapolate",
                bounds_error=False
            )
            self.surface[maturity] = interp
            """
            self.surface[maturity] = Smile(
            log_moneyness,
            vols,
            kind="linear"
            )
            

    def get_vol(self, strike: float, maturity: float) -> float:
        """
        Interpolate implied volatility for any strike and maturity
        """

        if not self.surface:
            raise ValueError("Vol surface has not been built")

        log_m = np.log(float(strike) / self.spot)

        maturities = np.array(sorted(self.surface.keys()))

        # Exact maturity available
        if maturity in self.surface:
            return float(self.surface[maturity](log_m))

        # Interpolate across maturities
        if maturity <= maturities.min():
            return float(self.surface[maturities.min()](log_m))
        if maturity >= maturities.max():
            return float(self.surface[maturities.max()](log_m))

        idx = np.searchsorted(maturities, maturity)
        t1, t2 = maturities[idx - 1], maturities[idx]

        vol1 = self.surface[t1](log_m)
        vol2 = self.surface[t2](log_m)

        # Linear interpolation in time
        w = (maturity - t1) / (t2 - t1)
        return float((1 - w) * vol1 + w * vol2)

    
    def bump_parallel(self, bump: float):
        """
        Parallel volatility bump (additive).
        Returns a NEW ImpliedVolSurface.
        """
        bumped = copy.deepcopy(self)

        for T, f_interp in bumped.surface.items():
            x = f_interp.x                    # log-moneyness grid
            vols = f_interp(x)                # original vols
            vols_bumped = np.maximum(vols + bump, 1e-4)

            bumped.surface[T] = interp1d(
                x,
                vols_bumped,
                kind="linear",
                fill_value="extrapolate",
                bounds_error=False
            )

        return bumped


