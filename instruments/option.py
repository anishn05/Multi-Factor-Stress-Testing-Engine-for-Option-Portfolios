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
    contract_size: float = 100.0

    def __post_init__(self):
        if self.option_type not in ("Call", "Put"):
            raise ValueError("option_type must be 'Call' or 'Put'")
