"""Consolidate the four ClassEval-T batch shards into a Markdown report."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_INPUTS = (
    Path("reports/classeval_openai_gpt41mini_2026-11-19.jsonl"),
    Path("reports/classeval_openai_gpt41mini_python_to_java_51-94_2026-11-19.jsonl"),
    Path("reports/classeval_openai_gpt41mini_java_to_python_2026-11-19.jsonl"),
    Path("reports/classeval_openai_gpt41mini_java_to_python_51-94_2026-11-19.jsonl"),
)


def read_rows(paths: tuple[Path, ...]) -> dict[tuple[str, str], dict]:
    rows = {}
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                rows[(row["direction"], row["task_id"])] = row
    return rows


def trajectory(row: dict) -> str:
    labels = {"translation": "T", "correction": "C", "smell_graph": "S"}
    pieces = []
    for event in row.get("loop_trace", []):
        label = f"{labels.get(event['phase'], '?')}{event['iteration']}"
        metrics = f"{event['tests_passed']}/{event['tests_total']}; {event['smells']}"
        if event.get("phase") == "smell_graph":
            metrics += " ✓" if event.get("accepted") else " ×"
        pieces.append(f"{label} ({metrics})")
    return " → ".join(pieces) or "—"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("reports/relatorio_gpt41mini_classeval_94_2026-11-19.md"))
    args = parser.parse_args()
    rows = read_rows(DEFAULT_INPUTS)
    directions = ("python_to_java", "java_to_python")
    expected = 94 * len(directions)
    now = datetime.now(timezone(timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")
    lines = [
        "# ClassEval-T — 94 classes com gpt-4.1-mini",
        "",
        f"Atualizado em {now} (São Paulo). API oficial OpenAI; uma execução por classe e direção.",
        f"Cobertura: **{len(rows)}/{expected}** traduções registradas.",
        "",
        "## Resumo",
        "",
        "| Direção | Classes | Passaram | Falharam | Erros | Sem testes executados | Testes corretos | Smells após tradução | Após correção | Finais | Iterações de correção | Iterações de smells |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for direction in directions:
        group = [r for (d, _), r in rows.items() if d == direction]
        measured = [r for r in group if r.get("status") in ("passed", "failed")]
        counts = Counter(r.get("status") for r in group)
        no_tests = sum(r["tests_total"] == 0 for r in measured)
        total_passed = sum(r["tests_passed"] for r in measured)
        total_tests = sum(r["tests_total"] for r in measured)
        sums = [sum(r[field] for r in measured) for field in (
            "smells_after_translation", "smells_after_correction", "smells_after_smell_graph",
            "correction_iterations", "smell_iterations",
        )]
        lines.append(
            f"| {direction} | {len(group)}/94 | {counts['passed']} | {counts['failed']} | {counts['error']} | {no_tests} "
            f"| {total_passed}/{total_tests} | " + " | ".join(map(str, sums)) + " |"
        )
    lines += [
        "",
        "`Testes corretos` soma os testes da linguagem de destino das classes concluídas. `0/0` significa que nenhum teste foi executado com sucesso, por exemplo por falha de compilação; essas classes continuam no denominador de 94 classes e não entram no denominador de testes. "
        "Smells são somas por direção: PMD 7.1.0 em Java e Pylint em Python. As contagens entre ferramentas não são diretamente comparáveis.",
        "",
        "## Resultado por classe",
        "",
        "Na trajetória, `T0` é a tradução inicial, `C1–C3` são correções e `S1–S3` são candidatos de redução de smells. "
        "Cada parêntese mostra `testes corretos/total; smells`. `✓` indica refatoração aceita e `×`, rejeitada.",
        "",
        "| Direção | Classe | Estado | Testes finais | Smells T/C/F | Correções | Loops de smells | Trajetória |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for direction in directions:
        for task_id in sorted(task for d, task in rows if d == direction):
            row = rows[(direction, task_id)]
            state = row.get("status", "error")
            if state in ("passed", "failed"):
                tests = f"{row['tests_passed']}/{row['tests_total']}"
                smells = "/".join(str(row[field]) for field in (
                    "smells_after_translation", "smells_after_correction", "smells_after_smell_graph"
                ))
                corrections = row["correction_iterations"]
                smell_loops = row["smell_iterations"]
            else:
                tests, smells, corrections, smell_loops = "—", "—", "—", "—"
            lines.append(
                f"| {direction} | {task_id} | {state} | {tests} | {smells} | {corrections} "
                f"| {smell_loops} | {trajectory(row)} |"
            )
    errors = [r for r in rows.values() if r.get("status") == "error"]
    if errors:
        lines += ["", "## Erros de execução", ""]
        for row in errors:
            lines.append(f"- {row['direction']} / {row['task_id']}: {row.get('error', {})}")
    lines += [
        "",
        "## Dados brutos",
        "",
        "Os quatro arquivos JSONL de entrada contêm os resultados completos, inclusive `loop_trace`, duração e contagens por etapa:",
        "",
    ]
    lines += [f"- `{path.name}`" for path in DEFAULT_INPUTS]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {args.output} coverage={len(rows)}/{expected}")


if __name__ == "__main__":
    main()
