import json
import re
from pathlib import Path


def detect_kind(args, result) -> str:
    if (len(args) == 2 and isinstance(args[0], list) and isinstance(args[1], (int, float))
            and isinstance(result, bool) and all(isinstance(item, (int, float)) for item in args[0])):
        return "floats_threshold_bool"
    if (len(args) == 1 and isinstance(args[0], str) and isinstance(result, list)
            and all(isinstance(item, str) for item in result)):
        return "str_to_str_list"
    raise TypeError(f"Unsupported EvalPlus case shape: args={args!r} result={result!r}")


def encode_json_case(args, result) -> tuple[str, str, str]:
    return json.dumps(list(args), ensure_ascii=False), json.dumps(result, ensure_ascii=False), "json"


def encode_case(args, result) -> tuple[str, str, str]:
    kind = detect_kind(args, result)
    if kind == "floats_threshold_bool":
        numbers = ",".join(str(item) for item in args[0])
        return f"{numbers}|{args[1]}", str(result).lower(), kind
    groups = "|".join(result)
    return args[0].replace("\n", "NLITC"), groups, kind


def _split_params(params: str) -> list[str]:
    parts = []
    depth = 0
    current: list[str] = []
    for char in params:
        if char == "<":
            depth += 1
        elif char == ">":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _param_type(param: str) -> str:
    tokens = [token for token in param.replace("final", " ").split() if token]
    if len(tokens) <= 1:
        return tokens[0] if tokens else "Object"
    return " ".join(tokens[:-1])


def _java_argument(index: int, java_type: str) -> str:
    normalized = re.sub(r"\s+", "", java_type)
    accessors = {
        "int": "asInt()",
        "Integer": "asInt()",
        "long": "asLong()",
        "Long": "asLong()",
        "double": "asDouble()",
        "Double": "asDouble()",
        "float": "asDouble()",
        "Float": "asDouble()",
        "boolean": "asBoolean()",
        "Boolean": "asBoolean()",
        "String": "asString()",
        "int[]": "asIntArray()",
        "double[]": "asDoubleArray()",
        "float[]": "asDoubleArray()",
        "String[]": "asStringArray()",
        "boolean[]": "asBooleanArray()",
    }
    base = f"parsed.get({index})"
    if normalized in accessors:
        return f"{base}.{accessors[normalized]}"
    list_match = re.fullmatch(r"(?:List|ArrayList)<(.+)>", normalized)
    if list_match:
        inner = {
            "Integer": "asIntList()",
            "int": "asIntList()",
            "Double": "asDoubleList()",
            "double": "asDoubleList()",
            "Float": "asDoubleList()",
            "String": "asStringList()",
            "Boolean": "asBooleanList()",
            "boolean": "asBooleanList()",
        }.get(list_match.group(1))
        if inner:
            return f"{base}.{inner}"
    raise ValueError(f"Unsupported Java parameter type {java_type}")


def _names_match(method_name: str, entry_point: str) -> bool:
    if not entry_point:
        return False
    compact = entry_point.replace("_", "").lower()
    return method_name == entry_point or method_name.lower() == compact


EVAL_JSON_JAVA = r"""
class EvalJson {
    final String kind;
    final String text;
    final java.util.List<EvalJson> items;

    EvalJson(String kind, String text, java.util.List<EvalJson> items) {
        this.kind = kind;
        this.text = text;
        this.items = items;
    }

    static EvalJson parse(String source) {
        return new Parser(source).parseValue();
    }

    EvalJson get(int index) { return items.get(index); }
    int asInt() { return (int) Double.parseDouble(text); }
    long asLong() { return (long) Double.parseDouble(text); }
    double asDouble() { return Double.parseDouble(text); }
    boolean asBoolean() { return "true".equals(text); }
    String asString() { return text; }
    java.util.List<Integer> asIntList() {
        java.util.List<Integer> values = new java.util.ArrayList<>();
        for (EvalJson item : items) values.add(item.asInt());
        return values;
    }
    java.util.List<Double> asDoubleList() {
        java.util.List<Double> values = new java.util.ArrayList<>();
        for (EvalJson item : items) values.add(item.asDouble());
        return values;
    }
    java.util.List<String> asStringList() {
        java.util.List<String> values = new java.util.ArrayList<>();
        for (EvalJson item : items) values.add(item.asString());
        return values;
    }
    java.util.List<Boolean> asBooleanList() {
        java.util.List<Boolean> values = new java.util.ArrayList<>();
        for (EvalJson item : items) values.add(item.asBoolean());
        return values;
    }
    int[] asIntArray() {
        int[] values = new int[items.size()];
        for (int i = 0; i < items.size(); i++) values[i] = items.get(i).asInt();
        return values;
    }
    double[] asDoubleArray() {
        double[] values = new double[items.size()];
        for (int i = 0; i < items.size(); i++) values[i] = items.get(i).asDouble();
        return values;
    }
    String[] asStringArray() {
        String[] values = new String[items.size()];
        for (int i = 0; i < items.size(); i++) values[i] = items.get(i).asString();
        return values;
    }
    boolean[] asBooleanArray() {
        boolean[] values = new boolean[items.size()];
        for (int i = 0; i < items.size(); i++) values[i] = items.get(i).asBoolean();
        return values;
    }

    static String emit(Object value) {
        if (value == null) return "null";
        if (value instanceof Boolean) return value.toString();
        if (value instanceof Integer || value instanceof Long) return value.toString();
        if (value instanceof Double || value instanceof Float) return Double.toString(((Number) value).doubleValue());
        if (value instanceof String) return quote((String) value);
        if (value instanceof java.util.List) {
            StringBuilder out = new StringBuilder("[");
            boolean first = true;
            for (Object item : (java.util.List<?>) value) {
                if (!first) out.append(", ");
                first = false;
                out.append(emit(item));
            }
            return out.append("]").toString();
        }
        if (value.getClass().isArray()) {
            StringBuilder out = new StringBuilder("[");
            int length = java.lang.reflect.Array.getLength(value);
            for (int i = 0; i < length; i++) {
                if (i > 0) out.append(", ");
                out.append(emit(java.lang.reflect.Array.get(value, i)));
            }
            return out.append("]").toString();
        }
        return quote(String.valueOf(value));
    }

    static String quote(String value) {
        StringBuilder out = new StringBuilder("\"");
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            if (c == '\\' || c == '"') out.append('\\').append(c);
            else if (c == '\n') out.append("\\n");
            else if (c == '\r') out.append("\\r");
            else if (c == '\t') out.append("\\t");
            else out.append(c);
        }
        return out.append('"').toString();
    }

    static final class Parser {
        final String source;
        int index;

        Parser(String source) { this.source = source == null ? "" : source.trim(); }

        void skip() {
            while (index < source.length() && Character.isWhitespace(source.charAt(index))) index++;
        }

        EvalJson parseValue() {
            skip();
            if (index >= source.length()) return new EvalJson("null", "null", null);
            char c = source.charAt(index);
            if (c == 'n') { index += 4; return new EvalJson("null", "null", null); }
            if (c == 't') { index += 4; return new EvalJson("bool", "true", null); }
            if (c == 'f') { index += 5; return new EvalJson("bool", "false", null); }
            if (c == '"') return new EvalJson("str", parseString(), null);
            if (c == '[') return parseArray();
            return new EvalJson("num", parseNumber(), null);
        }

        EvalJson parseArray() {
            index++;
            java.util.List<EvalJson> values = new java.util.ArrayList<>();
            skip();
            if (index < source.length() && source.charAt(index) == ']') {
                index++;
                return new EvalJson("arr", null, values);
            }
            while (index < source.length()) {
                values.add(parseValue());
                skip();
                if (index < source.length() && source.charAt(index) == ',') {
                    index++;
                    continue;
                }
                if (index < source.length() && source.charAt(index) == ']') index++;
                break;
            }
            return new EvalJson("arr", null, values);
        }

        String parseString() {
            index++;
            StringBuilder out = new StringBuilder();
            while (index < source.length()) {
                char c = source.charAt(index++);
                if (c == '"') break;
                if (c == '\\' && index < source.length()) {
                    char escaped = source.charAt(index++);
                    if (escaped == 'n') out.append('\n');
                    else if (escaped == 'r') out.append('\r');
                    else if (escaped == 't') out.append('\t');
                    else out.append(escaped);
                } else {
                    out.append(c);
                }
            }
            return out.toString();
        }

        String parseNumber() {
            int start = index;
            while (index < source.length()) {
                char c = source.charAt(index);
                if ((c >= '0' && c <= '9') || c == '-' || c == '+' || c == '.' || c == 'e' || c == 'E') index++;
                else break;
            }
            return source.substring(start, index);
        }
    }
}
"""


def java_main_for_evalplus(source: str, kind: str, entry_point: str = "") -> str:
    if "// evalplus-driver" in source:
        return source
    imports = []
    body_lines = []
    for line in source.splitlines():
        if line.startswith("import ") or line.startswith("package "):
            imports.append(line)
        else:
            body_lines.append(line)
    body = "\n".join(body_lines)
    body = re.sub(r"\bpublic\s+class\s+", "class ", body)
    class_match = re.search(r"\bclass\s+(\w+)", body)
    method_matches = list(re.finditer(
        r"public\s+(static\s+)?([\w.<>,\s\[\]]+?)\s+(\w+)\s*\(([^)]*)\)", body
    ))
    chosen = None
    for candidate in method_matches:
        if candidate.group(3) == "main":
            continue
        if _names_match(candidate.group(3), entry_point):
            chosen = candidate
            break
    if chosen is None:
        for candidate in method_matches:
            if candidate.group(3) != "main":
                chosen = candidate
                break
    method_match = chosen
    if class_match is None or method_match is None:
        raise ValueError("Translated Java has no public class method to call")
    class_name = class_match.group(1)
    static_call = method_match.group(1) is not None
    method_name = method_match.group(3)
    parameter_type = ""
    parameters = _split_params(method_match.group(4))
    if parameters:
        parameter_type = _param_type(parameters[0])
    receiver = f"{class_name}.{method_name}" if static_call else f"new {class_name}().{method_name}"
    if kind == "floats_threshold_bool":
        if "[]" in parameter_type:
            numbers_setup = """
        String[] pieces = parts[0].isEmpty() ? new String[0] : parts[0].split(",");
        double[] numbers = new double[pieces.length];
        for (int i = 0; i < pieces.length; i++) {
            numbers[i] = Double.parseDouble(pieces[i]);
        }"""
        else:
            numbers_setup = """
        java.util.List<Double> numbers = new java.util.ArrayList<>();
        if (!parts[0].isEmpty()) {
            for (String piece : parts[0].split(",")) {
                numbers.add(Double.parseDouble(piece));
            }
        }"""
        call = f"""
        String[] parts = input.split("\\\\|", -1);
        {numbers_setup}
        double threshold = Double.parseDouble(parts[1]);
        System.out.println({receiver}(numbers, threshold));
"""
    elif kind == "str_to_str_list":
        call = f"""
        java.util.List<String> groups = {receiver}(input);
        System.out.println(String.join("|", groups));
"""
    elif kind == "json":
        arguments = []
        for index, param in enumerate(_split_params(method_match.group(4))):
            arguments.append(_java_argument(index, _param_type(param)))
        joined = ", ".join(arguments)
        call = f"""
        EvalJson parsed = EvalJson.parse(input);
        System.out.print(EvalJson.emit({receiver}({joined})));
"""
    else:
        raise ValueError(kind)
    driver = f"""
public class Main {{
    // evalplus-driver
    public static void main(String[] args) throws Exception {{
        byte[] data = System.in.readAllBytes();
        String input = new String(data, java.nio.charset.StandardCharsets.UTF_8);
        if (input.endsWith("\\n")) input = input.substring(0, input.length() - 1);
        if (input.endsWith("\\r")) input = input.substring(0, input.length() - 1);
        {call}
    }}
}}
"""
    pieces = imports + ["", driver.strip(), ""]
    if kind == "json":
        pieces.extend([EVAL_JSON_JAVA.strip(), ""])
    pieces.extend([body.strip(), ""])
    return "\n".join(pieces)


def materialize_java_main(source_path: str, task_id: str, base_path: str) -> str:
    driver_path = Path(base_path) / "evalplus" / "drivers" / f"{task_id}.json"
    if not driver_path.is_file():
        return source_path
    spec = json.loads(driver_path.read_text(encoding="utf-8"))
    source = Path(source_path).read_text(encoding="utf-8")
    wrapped = java_main_for_evalplus(source, spec["kind"], spec.get("entry_point", ""))
    destination = Path(source_path).with_suffix(".main.java")
    destination.write_text(wrapped, encoding="utf-8")
    return str(destination)
