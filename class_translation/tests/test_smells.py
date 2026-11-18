import pytest

from class_translation.smells import count_pmd, count_smells, pmd_executable
from class_translation.tests.samples import CLEAN, SMELLY

CLEAN_JAVA = """\
package org.example;

public class Clean {
    private int value;

    public void add(int amount) {
        this.value += amount;
    }

    public int getValue() {
        return this.value;
    }
}
"""

SMELLY_JAVA = """\
package org.example;

public class Smelly {
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


def test_unused_variable_increases_smell_count():
    smelly = count_smells(SMELLY, "counter")
    clean = count_smells(CLEAN, "counter")
    assert smelly.count > clean.count
    assert "unused-variable" in smelly.feedback


@pytest.mark.skipif(pmd_executable() is None, reason="PMD 7.1.0 binary is not installed")
def test_pmd_unused_field_increases_smell_count():
    smelly = count_pmd(SMELLY_JAVA, "Smelly")
    clean = count_pmd(CLEAN_JAVA, "Clean")
    assert smelly.count > clean.count
    assert "UnusedPrivateField" in smelly.feedback
