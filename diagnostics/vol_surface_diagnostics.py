# diagnostics/vol_surface_diagnostics.py

import numpy as np

class VolSurfaceDiagnostics:
    def __init__(self, surface):
        self.surface = surface

    def out_of_sample_fit(self, validation_chains):
        errors = []

        for expiry, df in validation_chains.items():
            T = self.surface._time_to_maturity(expiry)

            for _, row in df.iterrows():
                K = float(row["strike"])
                market_vol = float(row["impliedVolatility"])

                model_vol = self.surface.get_vol(K, T)
                errors.append(model_vol - market_vol)

        errors = np.array(errors)

        return {
            "rmse": np.sqrt(np.mean(errors ** 2)),
            "mean_error": np.mean(errors),
            "max_abs_error": np.max(np.abs(errors))
        }
