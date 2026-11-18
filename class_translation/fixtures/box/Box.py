class Box:
    def __init__(self) -> None:
        self.value = 0

    def add(self, amount: int) -> None:
        self.value += amount

    def getValue(self) -> int:
        return self.value
