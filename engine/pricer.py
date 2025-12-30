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

            total_value += opt.quantity * price

        return total_value
