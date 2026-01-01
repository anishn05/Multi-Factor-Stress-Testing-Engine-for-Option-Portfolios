from models.black_scholes import bs_price


class PortfolioPricer:
    """
    Prices an option portfolio given spot and vol surface
    """

    def __init__(self, rate: float):
        self.rate = rate

    def price(self, portfolio, spot: float, vol_surface) -> float:
        total_value = 0.0

        for opt in portfolio:
            vol = vol_surface.get_vol(opt.strike, opt.maturity)

            price = bs_price(
                spot=spot,
                strike=opt.strike,
                maturity=opt.maturity,
                rate=self.rate,
                vol=vol,
                option_type=opt.option_type
            )

            total_value += opt.quantity * price * opt.contract_size

        return total_value
    
    def price_with_rolled_maturity(pricer, portfolio, spot, vol_surface, dt):
        """
        Prices a portfolio assuming each option's maturity is reduced by dt.
        Only used for theta calculation.
        """
        total_value = 0.0
        for opt in portfolio:
            # Reduce time to maturity
            T_new = max(opt.maturity - dt, 1e-6)  # avoid zero/negative maturity

            # Use the existing vol surface for this rolled maturity
            vol = vol_surface.get_vol(opt.strike, T_new)

            # Price the option
            price = bs_price(
                spot=spot,
                strike=opt.strike,
                maturity=T_new,
                rate=pricer.rate,
                vol=vol,
                option_type=opt.option_type
            )

            # Account for quantity and contract size
            total_value += opt.quantity * price * opt.contract_size

        return total_value

