from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from class_translation.extract import extract_python
from class_translation.prompts import smell_messages
from class_translation.providers import ChatClient
from class_translation.smells import count_smells
from class_translation.state import MAX_SMELL_ITERATIONS, ClassTask
from class_translation.testing import run_unittest


class SmellState(TypedDict):
    oracle_tests: str
    module_name: str
    code: str
    previous_code: str
    smell_count: int
    previous_smell_count: int
    smell_feedback: str
    iterations: int
    max_iterations: int
    status: str


@dataclass(frozen=True)
class SmellResult:
    code: str
    iterations: int
    status: str


def build_smell_graph(client: ChatClient, task: ClassTask):
    def lint(state: SmellState) -> dict[str, object]:
        report = count_smells(state["code"], state["module_name"])
        update: dict[str, object] = {
            "smell_count": report.count,
            "smell_feedback": report.feedback,
        }
        if report.count == 0:
            update["status"] = "clean"
        return update

    def refactor(state: SmellState) -> dict[str, object]:
        messages = smell_messages(task, state["code"], state["smell_feedback"])
        return {
            "previous_code": state["code"],
            "previous_smell_count": state["smell_count"],
            "code": extract_python(client.complete(messages)),
            "iterations": state["iterations"] + 1,
        }

    def evaluate(state: SmellState) -> dict[str, object]:
        tests = run_unittest(state["code"], state["oracle_tests"], state["module_name"])
        smells = count_smells(state["code"], state["module_name"])
        accepted = tests.ok and smells.count < state["previous_smell_count"]
        if accepted:
            return {
                "smell_count": smells.count,
                "smell_feedback": smells.feedback,
                "status": "accepted",
            }
        return {"status": "reject"}

    def rollback(state: SmellState) -> dict[str, object]:
        return {
            "code": state["previous_code"],
            "smell_count": state["previous_smell_count"],
            "status": "rolled_back",
        }

    def route_after_lint(state: SmellState) -> Literal["refactor", "end"]:
        if state["smell_count"] == 0:
            return "end"
        if state["iterations"] >= state["max_iterations"]:
            return "end"
        return "refactor"

    def route_after_evaluate(state: SmellState) -> Literal["lint", "rollback"]:
        if state["status"] == "accepted":
            return "lint"
        return "rollback"

    graph = StateGraph(SmellState)
    graph.add_node("lint", lint)
    graph.add_node("refactor", refactor)
    graph.add_node("evaluate", evaluate)
    graph.add_node("rollback", rollback)
    graph.add_edge(START, "lint")
    graph.add_conditional_edges(
        "lint", route_after_lint, {"refactor": "refactor", "end": END}
    )
    graph.add_edge("refactor", "evaluate")
    graph.add_conditional_edges(
        "evaluate",
        route_after_evaluate,
        {"lint": "lint", "rollback": "rollback"},
    )
    graph.add_edge("rollback", "lint")
    return graph.compile()


def reduce_smells(
    task: ClassTask,
    code: str,
    client: ChatClient,
    max_iterations: int = MAX_SMELL_ITERATIONS,
) -> SmellResult:
    app = build_smell_graph(client, task)
    final = app.invoke(
        {
            "oracle_tests": task.oracle_tests,
            "module_name": task.module_name,
            "code": code,
            "previous_code": code,
            "smell_count": -1,
            "previous_smell_count": -1,
            "smell_feedback": "",
            "iterations": 0,
            "max_iterations": max_iterations,
            "status": "start",
        }
    )
    return SmellResult(
        code=final["code"],
        iterations=final["iterations"],
        status=final["status"],
    )
