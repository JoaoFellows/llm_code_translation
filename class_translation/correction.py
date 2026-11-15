from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from class_translation.extract import extract_python
from class_translation.prompts import repair_messages
from class_translation.providers import ChatClient
from class_translation.state import MAX_CORRECTION_ITERATIONS, ClassTask
from class_translation.testing import run_unittest


class CorrectionState(TypedDict):
    source_code: str
    source_tests: str
    source_lang: str
    target_lang: str
    oracle_tests: str
    module_name: str
    code: str
    iterations: int
    max_iterations: int
    passed: int
    total: int
    feedback: str
    status: str


@dataclass(frozen=True)
class CorrectionResult:
    code: str
    iterations: int
    passed: int
    total: int
    status: str


def build_correction_graph(client: ChatClient, task: ClassTask):
    def run_tests(state: CorrectionState) -> dict[str, object]:
        report = run_unittest(state["code"], state["oracle_tests"], state["module_name"])
        status = "passed" if report.ok else "failed"
        return {
            "passed": report.passed,
            "total": report.total,
            "feedback": report.feedback,
            "status": status,
        }

    def repair(state: CorrectionState) -> dict[str, object]:
        messages = repair_messages(task, state["code"], state["feedback"])
        return {
            "code": extract_python(client.complete(messages)),
            "iterations": state["iterations"] + 1,
        }

    def route(state: CorrectionState) -> Literal["repair", "end"]:
        if state["status"] == "passed":
            return "end"
        if state["iterations"] >= state["max_iterations"]:
            return "end"
        return "repair"

    graph = StateGraph(CorrectionState)
    graph.add_node("run_tests", run_tests)
    graph.add_node("repair", repair)
    graph.add_edge(START, "run_tests")
    graph.add_conditional_edges("run_tests", route, {"repair": "repair", "end": END})
    graph.add_edge("repair", "run_tests")
    return graph.compile()


def correct(task: ClassTask, code: str, client: ChatClient) -> CorrectionResult:
    app = build_correction_graph(client, task)
    final = app.invoke(
        {
            "source_code": task.source_code,
            "source_tests": task.source_tests,
            "source_lang": task.source_lang,
            "target_lang": task.target_lang,
            "oracle_tests": task.oracle_tests,
            "module_name": task.module_name,
            "code": code,
            "iterations": 0,
            "max_iterations": MAX_CORRECTION_ITERATIONS,
            "passed": 0,
            "total": 0,
            "feedback": "",
            "status": "failed",
        }
    )
    return CorrectionResult(
        code=final["code"],
        iterations=final["iterations"],
        passed=final["passed"],
        total=final["total"],
        status=final["status"],
    )
