from class_translation.smells import count_smells
from class_translation.tests.samples import CLEAN, SMELLY


def test_unused_variable_increases_smell_count():
    smelly = count_smells(SMELLY, "counter")
    clean = count_smells(CLEAN, "counter")
    assert smelly.count > clean.count
    assert "unused-variable" in smelly.feedback
