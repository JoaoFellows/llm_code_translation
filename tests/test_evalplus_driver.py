from evalplus_driver import encode_case, java_main_for_evalplus

SOLUTION = """
import java.util.Collections;
import java.util.List;

public class Solution {
    public static boolean hasCloseElements(List<Double> numbers, double threshold) {
        return false;
    }
}
"""

GROUPS = """
import java.util.List;

public class ParenSeparator {
    public static List<String> separateParenGroups(String parenString) {
        return java.util.List.of();
    }
}
"""


def test_json_driver_calls_the_entry_point_with_typed_arguments():
    source = """
public class CloseElementsChecker {
    public static boolean hasCloseElements(double[] numbers, double threshold) {
        return false;
    }
}
"""
    wrapped = java_main_for_evalplus(source, "json", "has_close_elements")
    assert "parsed.get(0).asDoubleArray()" in wrapped
    assert "parsed.get(1).asDouble()" in wrapped
    assert "CloseElementsChecker.hasCloseElements" in wrapped


def test_encode_bool_and_string_cases():
    raw, expected, kind = encode_case([[1.0, 2.0], 0.3], False)
    assert kind == "floats_threshold_bool"
    assert raw == "1.0,2.0|0.3"
    assert expected == "false"
    raw, expected, kind = encode_case(["(()()) ()"], ["()", "()"])
    assert kind == "str_to_str_list"
    assert raw == "(()()) ()"
    assert expected == "()|()"


ARRAY_SOLUTION = """
import java.util.Arrays;

public class CloseElementsChecker {
    public static boolean hasCloseElements(double[] numbers, double threshold) {
        return false;
    }
}
"""


def test_java_main_uses_a_double_array_when_the_method_declares_one():
    wrapped = java_main_for_evalplus(ARRAY_SOLUTION, "floats_threshold_bool")
    assert "double[] numbers = new double[pieces.length];" in wrapped
    assert "CloseElementsChecker.hasCloseElements(numbers, threshold)" in wrapped


def test_java_main_calls_the_translated_static_method():
    wrapped = java_main_for_evalplus(SOLUTION, "floats_threshold_bool")
    assert "class Solution" in wrapped
    assert "public class Solution" not in wrapped
    assert "Solution.hasCloseElements(numbers, threshold)" in wrapped
    assert wrapped.index("public class Main") < wrapped.index("class Solution")

    groups = java_main_for_evalplus(GROUPS, "str_to_str_list")
    assert "ParenSeparator.separateParenGroups(input)" in groups
