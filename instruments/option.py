from dataclasses import dataclass


@dataclass
class EuropeanOption:
    """
    European option instrument
    """
    strike: float
    maturity: float      # years
    option_type: str     # "call" or "put"
    quantity: float      # positive = long, negative = short

    def __post_init__(self):
        if self.option_type not in ("call", "put"):
            raise ValueError("option_type must be 'call' or 'put'")
