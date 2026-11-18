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

BOX_BUGGY = """\
package org.example;

public class Box {
    private int value;

    public void add(int amount) {
        this.value = amount;
    }

    public int getValue() {
        return this.value;
    }
}
"""

BOX_SMELLY = """\
package org.example;

public class Box {
    private int value;
    private int unusedField;

    public void add(int amount) {
        this.value += amount;
    }

    public int getValue() {
        return this.value;
    }
}
"""

BOX_CLEAN = """\
package org.example;

public class Box {
    private int value;

    public void add(int amount) {
        this.value += amount;
    }

    public int getValue() {
        return this.value;
    }
}
"""

BOX_BROKEN = """\
package org.example;

public class Box {
    private int value;

    public void add(int amount) {
        this.value = 0;
    }

    public int getValue() {
        return this.value;
    }
}
"""
