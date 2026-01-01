#Pre-defined stress scenarios

SCENARIOS = {
    "Mild Up + Mild Vol Expansion": {
        "spot_shift": +0.01,
        "vol_shocks": [{"type": "parallel", "value": 0.02}],
        "description": "1% upward spot move combined with parallel volatility increase of +2 vol points",
    },
    "Equity Selloff + Vol Compression": {
        "spot_shift": -0.05,
        "vol_shocks": [{"type": "parallel", "value": -0.03}, {"type": "skew", "value": -0.03}],
        "description": "5% downward spot move with parallel volatility reduction and skew reduction by 3 vol points",
    },
    "Equity Rally + Vol Expansion": {
        "spot_shift": 0.03,
        "vol_shocks": [{"type": "parallel", "value": 0.05}],
        "description": "3% upward spot move with parallel volatility increase of +5 vol points",
    },
    "Equity Selloff + Vol Convexity Increase": {
        "spot_shift": -0.05,
        "vol_shocks": [{"type": "curvature", "value": 0.03}],
        "description": "5% downward spot move with an increase in volatility smile curvature by 3 vol points",
    },
    "Crash Scenario": {
        "spot_shift": -0.10,
        "vol_shocks": [{"type": "parallel", "value": 0.15}, {"type": "skew", "value": -0.03}],
        "description": "10% downward spot move with large parallel volatility increase (+15 vol points) and skew reduction by 3 vol points",
    },
}
