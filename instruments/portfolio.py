class OptionPortfolio:
    """
    Container for option positions
    """

    def __init__(self):
        self.positions = []

    def add(self, option):
        self.positions.append(option)

    def __iter__(self):
        return iter(self.positions)

    def __len__(self):
        return len(self.positions)
