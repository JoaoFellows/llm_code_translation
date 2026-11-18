from __future__ import annotations

from class_translation.correction import correct
from class_translation.providers import ChatClient
from class_translation.smell_graph import reduce_smells
from class_translation.smells import count_smells
from class_translation.state import ClassTask, TaskRecord, ensure_java_to_python
from class_translation.testing import run_target_tests
from class_translation.translate import translate_class


def run_task(task: ClassTask, client: ChatClient) -> TaskRecord:
    ensure_java_to_python(task)
    translated = translate_class(task, client)
    smells_after_translation = count_smells(translated, task.module_name).count
    corrected = correct(task, translated, client)
    smells_after_correction = count_smells(corrected.code, task.module_name).count
    if corrected.status == "passed":
        reduced = reduce_smells(task, corrected.code, client)
        final_code = reduced.code
        smell_iterations = reduced.iterations
    else:
        final_code = corrected.code
        smell_iterations = 0
    smells_after_smell_graph = count_smells(final_code, task.module_name).count
    report = run_target_tests(
        final_code, task.oracle_tests, task.module_name, task.target_lang
    )
    status = "passed" if report.ok else "failed"
    return TaskRecord(
        task_id=task.task_id,
        tests_passed=report.passed,
        tests_total=report.total,
        status=status,
        smells_after_translation=smells_after_translation,
        smells_after_correction=smells_after_correction,
        smells_after_smell_graph=smells_after_smell_graph,
        correction_iterations=corrected.iterations,
        smell_iterations=smell_iterations,
    )
