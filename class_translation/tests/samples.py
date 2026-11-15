BUGGY = """\
class Counter:
    def __init__(self) -> None:
        self.value = 0

    def add(self, amount: int) -> None:
        self.value = amount

    def getValue(self) -> int:
        return self.value
"""

SMELLY = """\
class Counter:
    def __init__(self) -> None:
        self.value = 0

    def add(self, amount: int) -> None:
        unused = amount
        self.value += amount

    def getValue(self) -> int:
        return self.value
"""

CLEAN = """\
class Counter:
    def __init__(self) -> None:
        self.value = 0

    def add(self, amount: int) -> None:
        self.value += amount

    def getValue(self) -> int:
        return self.value
"""

BROKEN = """\
class Counter:
    def __init__(self) -> None:
        self.value = 0

    def add(self, amount: int) -> None:
        self.value = 0

    def getValue(self) -> int:
        return self.value
"""
