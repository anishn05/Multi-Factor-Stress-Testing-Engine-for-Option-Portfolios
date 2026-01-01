#Function to split option chains into calibration and validation to test vol surface adn run diagnostics

def split_option_chains(option_chains, holdout_frac=0.25, seed=42):
    calibration = {}
    validation = {}

    for expiry, df in option_chains.items():
        val = df.sample(frac=holdout_frac, random_state=seed)
        cal = df.drop(val.index)

        calibration[expiry] = cal.reset_index(drop=True)
        validation[expiry] = val.reset_index(drop=True)

    return calibration, validation