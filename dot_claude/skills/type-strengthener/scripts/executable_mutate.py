#!/usr/bin/env python3
"""Test whether Python types protect consumers from plausible edits.

The script applies one edit, runs the type checker, and reports the consumers
that receive no new error. Supported edits include renaming or changing a field,
changing a parameter, adding a closed-set variant or required mapping key,
breaking a generic return relationship, changing a tuple shape, and adding
`None` to a return type.

A consumer with no new checker error might have lost its type connection to the changed declaration.
Review every result because an unrelated symbol can have the same name.

The script changes a temporary copy and leaves the source tree unchanged.
It uses only the Python standard library.

Usage:

    uv run mutate.py discover --root .
    uv run mutate.py run --root . --json out.json
    uv run mutate.py run --root . --kind rename --target User.email
    uv run mutate.py run --root . --checker pyright --limit 10
    uv run mutate.py run --root . --checker-command "uv run ty check {target}"
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from pathlib import Path

PROBE = "erosion_probe"
SKIP_DIRS = {
    ".git",
    ".hg",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".tox",
    ".eggs",
    "site-packages",
    ".idea",
    ".vscode",
}
TEST_HINT = re.compile(r"(^|/)(tests?|testing)(/|$)|(^|/)(test_|conftest)")
TYPE_ALIAS_NODE = getattr(ast, "TypeAlias", None)


# --------------------------------------------------------------------------
# Candidates
# --------------------------------------------------------------------------


@dataclass
class Candidate:
    kind: str
    qualname: str  # Examples include User.email, Status, and module:get_user.
    relpath: str
    lineno: int
    detail: str = ""
    symbol: str = ""  # The consumer search uses this bare name.
    # Consumers can dispatch on enum member names and literal values.
    extra_symbols: list[str] = field(default_factory=list)
    def_end: int = (
        0  # Consumer searches exclude the definition block through this line.
    )
    # The declaration fragment changed by relationship and parameter mutations.
    mutation_value: str = ""

    @property
    def key(self) -> str:
        return f"{self.kind}:{self.qualname}"


def iter_py_files(
    root: Path, include_tests: bool = False
) -> Iterator[tuple[Path, str]]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
        ]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            p = Path(dirpath) / fn
            rel = p.relative_to(root).as_posix()
            if not include_tests and TEST_HINT.search(rel):
                continue
            yield p, rel


def _base_names(cls: ast.ClassDef) -> set[str]:
    out: set[str] = set()
    for b in cls.bases:
        if isinstance(b, ast.Name):
            out.add(b.id)
        elif isinstance(b, ast.Attribute):
            out.add(b.attr)
        elif isinstance(b, ast.Subscript):
            v = b.value
            out.add(v.id if isinstance(v, ast.Name) else getattr(v, "attr", ""))
    return out


def _is_enum(cls: ast.ClassDef) -> bool:
    return bool(
        _base_names(cls) & {"Enum", "StrEnum", "IntEnum", "IntFlag", "Flag", "ReprEnum"}
    )


def _is_typed_dict(cls: ast.ClassDef) -> bool:
    return "TypedDict" in _base_names(cls)


def _typed_dict_adds_required_keys(cls: ast.ClassDef) -> bool:
    for keyword in cls.keywords:
        if (
            keyword.arg == "total"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value is False
        ):
            return False
    return True


def _subscript_name(node: ast.AST) -> str:
    if not isinstance(node, ast.Subscript):
        return ""
    value = node.value
    if isinstance(value, ast.Name):
        return value.id
    if isinstance(value, ast.Attribute):
        return value.attr
    return ""


def _literal_values(node: ast.AST) -> list[str] | None:
    if _subscript_name(node) != "Literal":
        return None
    assert isinstance(node, ast.Subscript)
    elements = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
    values: list[str] = []
    for element in elements:
        if not isinstance(element, ast.Constant) or not isinstance(
            element.value, (str, int, bool)
        ):
            return None
        values.append(str(element.value))
    return values


def _typevar_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for statement in tree.body:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            continue
        target = statement.targets[0]
        call = statement.value
        if not isinstance(target, ast.Name) or not isinstance(call, ast.Call):
            continue
        function = call.func
        function_name = (
            function.id
            if isinstance(function, ast.Name)
            else getattr(function, "attr", "")
        )
        if function_name == "TypeVar":
            names.add(target.id)
    return names


def _annotation_src(src_lines: list[str], node: ast.AST) -> str | None:
    if getattr(node, "lineno", None) != getattr(node, "end_lineno", None):
        return None  # The script skips multiline annotations to avoid corrupting them.
    line = src_lines[node.lineno - 1]
    return line[node.col_offset : node.end_col_offset]


def discover(root: Path, include_tests: bool = False) -> list[Candidate]:
    found: list[Candidate] = []
    for path, rel in iter_py_files(root, include_tests):
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        lines = src.splitlines()
        legacy_typevars = _typevar_names(tree)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if _is_enum(node):
                    members, values = [], []
                    for st in node.body:
                        if (
                            isinstance(st, ast.Assign)
                            and st.targets
                            and isinstance(st.targets[0], ast.Name)
                        ):
                            members.append(st.targets[0].id)
                            if isinstance(st.value, ast.Constant) and isinstance(
                                st.value.value, (str, int)
                            ):
                                values.append(str(st.value.value))
                    if members:
                        found.append(
                            Candidate(
                                "add_variant",
                                node.name,
                                rel,
                                node.lineno,
                                f"enum with {len(members)} members",
                                node.name,
                                extra_symbols=members + values,
                                def_end=node.end_lineno or node.lineno,
                            )
                        )
                    continue

                if _is_typed_dict(node) and _typed_dict_adds_required_keys(node):
                    fields = [
                        statement
                        for statement in node.body
                        if isinstance(statement, ast.AnnAssign)
                        and isinstance(statement.target, ast.Name)
                    ]
                    if fields:
                        found.append(
                            Candidate(
                                "add_required_key",
                                node.name,
                                rel,
                                node.lineno,
                                f"TypedDict with {len(fields)} declared keys",
                                node.name,
                                def_end=node.end_lineno or node.lineno,
                            )
                        )

                for stmt in node.body:
                    if not isinstance(stmt, ast.AnnAssign):
                        continue
                    if not isinstance(stmt.target, ast.Name):
                        continue
                    fname = stmt.target.id
                    if fname.startswith("_"):
                        continue
                    ann = _annotation_src(lines, stmt.annotation)
                    if ann is None:
                        continue
                    q = f"{node.name}.{fname}"
                    found.append(Candidate("rename", q, rel, stmt.lineno, ann, fname))
                    found.append(Candidate("retype", q, rel, stmt.lineno, ann, fname))

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_") or node.returns is None:
                    continue
                ann = _annotation_src(lines, node.returns)
                if ann is None:
                    continue
                flat = ann.replace(" ", "")
                if not (
                    flat in {"None", "Any"}
                    or "None" in flat
                    or flat.startswith("Optional")
                ):
                    found.append(
                        Candidate(
                            "optionalize",
                            f"{rel}:{node.name}",
                            rel,
                            node.lineno,
                            ann,
                            node.name,
                        )
                    )

                all_args = [
                    *node.args.posonlyargs,
                    *node.args.args,
                    *node.args.kwonlyargs,
                ]
                if node.args.vararg:
                    all_args.append(node.args.vararg)
                if node.args.kwarg:
                    all_args.append(node.args.kwarg)
                for argument in all_args:
                    if argument.arg in {"self", "cls"} or argument.annotation is None:
                        continue
                    argument_ann = _annotation_src(lines, argument.annotation)
                    if argument_ann is None:
                        continue
                    found.append(
                        Candidate(
                            "retype_param",
                            f"{rel}:{node.name}:{argument.arg}",
                            rel,
                            node.lineno,
                            argument_ann,
                            node.name,
                            mutation_value=argument.arg,
                        )
                    )

                native_typevars = {
                    getattr(parameter, "name", "")
                    for parameter in getattr(node, "type_params", [])
                    if parameter.__class__.__name__ == "TypeVar"
                }
                available_typevars = legacy_typevars | (native_typevars - {""})
                argument_annotations = [
                    _annotation_src(lines, argument.annotation) or ""
                    for argument in all_args
                    if argument.annotation is not None
                ]
                related = [
                    name
                    for name in available_typevars
                    if re.search(rf"\b{re.escape(name)}\b", ann)
                    and any(
                        re.search(rf"\b{re.escape(name)}\b", item)
                        for item in argument_annotations
                    )
                ]
                for name in related:
                    found.append(
                        Candidate(
                            "break_relation",
                            f"{rel}:{node.name}:{name}",
                            rel,
                            node.lineno,
                            f"return annotation {ann} relates input and output through {name}",
                            node.name,
                            mutation_value=name,
                        )
                    )

                if flat.startswith("tuple[") and flat.endswith("]"):
                    found.append(
                        Candidate(
                            "extend_tuple",
                            f"{rel}:{node.name}",
                            rel,
                            node.lineno,
                            ann,
                            node.name,
                        )
                    )

            elif isinstance(node, (ast.Assign, ast.AnnAssign)) or (
                TYPE_ALIAS_NODE is not None and isinstance(node, TYPE_ALIAS_NODE)
            ):
                if isinstance(node, ast.Assign):
                    if len(node.targets) != 1 or not isinstance(
                        node.targets[0], ast.Name
                    ):
                        continue
                    alias_name = node.targets[0].id
                    value = node.value
                elif isinstance(node, ast.AnnAssign):
                    if not isinstance(node.target, ast.Name) or node.value is None:
                        continue
                    alias_name = node.target.id
                    value = node.value
                else:
                    if not isinstance(node.name, ast.Name):
                        continue
                    alias_name = node.name.id
                    value = node.value
                literal_values = _literal_values(value)
                if literal_values and value.lineno == value.end_lineno:
                    found.append(
                        Candidate(
                            "add_literal_variant",
                            alias_name,
                            rel,
                            node.lineno,
                            f"Literal alias with {len(literal_values)} variants",
                            alias_name,
                            extra_symbols=literal_values,
                        )
                    )
    return found


# --------------------------------------------------------------------------
# Mutation application
# --------------------------------------------------------------------------


@dataclass
class Applied:
    ok: bool
    note: str = ""
    insert_line: int = 0  # The mutation inserts lines at or after this line.
    line_delta: int = 0


def _replace_span(path: Path, lineno: int, col: int, end_col: int, new: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    line = lines[lineno - 1]
    nl = "\n" if line.endswith("\n") else ""
    body = line[:-1] if nl else line
    lines[lineno - 1] = body[:col] + new + body[end_col:] + nl
    path.write_text("".join(lines), encoding="utf-8")


def apply_mutation(work: Path, cand: Candidate) -> Applied:
    path = work / cand.relpath
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except (SyntaxError, UnicodeDecodeError) as exc:
        return Applied(
            False,
            f"Couldn't parse {cand.relpath}: {exc}. Fix the file's syntax before you run "
            "this mutation again.",
        )
    lines = src.splitlines()

    if cand.kind in {"rename", "retype"}:
        cls_name, fname = cand.qualname.split(".", 1)
        for node in ast.walk(tree):
            if not (isinstance(node, ast.ClassDef) and node.name == cls_name):
                continue
            for stmt in node.body:
                if (
                    isinstance(stmt, ast.AnnAssign)
                    and isinstance(stmt.target, ast.Name)
                    and stmt.target.id == fname
                ):
                    if cand.kind == "rename":
                        _replace_span(
                            path,
                            stmt.target.lineno,
                            stmt.target.col_offset,
                            stmt.target.end_col_offset,
                            f"{fname}_{PROBE}",
                        )
                        return Applied(
                            True, f"Renamed {cand.qualname} to {fname}_{PROBE}."
                        )
                    ann = _annotation_src(lines, stmt.annotation) or ""
                    new = "complex" if "bytes" in ann else "bytes"
                    _replace_span(
                        path,
                        stmt.annotation.lineno,
                        stmt.annotation.col_offset,
                        stmt.annotation.end_col_offset,
                        new,
                    )
                    return Applied(
                        True, f"Changed {cand.qualname} from {ann} to {new}."
                    )
        return Applied(
            False,
            f"Field {cand.qualname} wasn't found. Run discovery again before you retry the mutation.",
        )

    if cand.kind == "retype_param":
        parts = cand.qualname.rsplit(":", 2)
        fn_name = parts[-2]
        for node in ast.walk(tree):
            if not (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == fn_name
                and node.lineno == cand.lineno
            ):
                continue
            arguments = [
                *node.args.posonlyargs,
                *node.args.args,
                *node.args.kwonlyargs,
            ]
            if node.args.vararg:
                arguments.append(node.args.vararg)
            if node.args.kwarg:
                arguments.append(node.args.kwarg)
            for argument in arguments:
                if argument.arg != cand.mutation_value or argument.annotation is None:
                    continue
                ann = _annotation_src(lines, argument.annotation) or ""
                new = "complex" if "bytes" in ann else "bytes"
                _replace_span(
                    path,
                    argument.annotation.lineno,
                    argument.annotation.col_offset,
                    argument.annotation.end_col_offset,
                    new,
                )
                return Applied(
                    True,
                    f"Changed parameter {fn_name}.{argument.arg} from {ann} to {new}.",
                )
        return Applied(False, f"Parameter {cand.qualname} wasn't found.")

    if cand.kind in {"break_relation", "extend_tuple"}:
        fn_name = (
            cand.qualname.split(":")[-2]
            if cand.kind == "break_relation"
            else cand.qualname.split(":", 1)[1]
        )
        for node in ast.walk(tree):
            if not (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == fn_name
                and node.lineno == cand.lineno
                and node.returns is not None
            ):
                continue
            ann = _annotation_src(lines, node.returns) or ""
            if cand.kind == "break_relation":
                new = re.sub(rf"\b{re.escape(cand.mutation_value)}\b", "object", ann)
                note = (
                    f"Replaced {cand.mutation_value} with object in the return annotation "
                    f"of {fn_name}."
                )
            else:
                closing = ann.rfind("]")
                if closing < 0:
                    return Applied(False, f"Tuple return for {fn_name} wasn't found.")
                new = ann[:closing] + ", object" + ann[closing:]
                note = f"Added an object element to the return tuple of {fn_name}."
            _replace_span(
                path,
                node.returns.lineno,
                node.returns.col_offset,
                node.returns.end_col_offset,
                new,
            )
            return Applied(True, note)
        return Applied(False, f"Function {cand.qualname} wasn't found.")

    if cand.kind == "optionalize":
        fn_name = cand.qualname.split(":", 1)[1]
        for node in ast.walk(tree):
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == fn_name
                and node.lineno == cand.lineno
                and node.returns is not None
            ):
                ann = _annotation_src(lines, node.returns) or ""
                _replace_span(
                    path,
                    node.returns.lineno,
                    node.returns.col_offset,
                    node.returns.end_col_offset,
                    f"{ann} | None",
                )
                return Applied(
                    True,
                    f"Changed the return type of {fn_name} from {ann} to {ann} | None.",
                )
        return Applied(
            False,
            f"Function {fn_name} wasn't found. Run discovery again before you retry the mutation.",
        )

    if cand.kind == "add_required_key":
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.ClassDef)
                and node.name == cand.qualname
                and _is_typed_dict(node)
                and _typed_dict_adds_required_keys(node)
            ):
                continue
            fields = [
                statement
                for statement in node.body
                if isinstance(statement, ast.AnnAssign)
                and isinstance(statement.target, ast.Name)
            ]
            if not fields:
                return Applied(False, f"TypedDict {cand.qualname} has no fields.")
            last = fields[-1]
            indent = " " * last.col_offset
            insert_at = last.end_lineno or last.lineno
            src_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
            src_lines.insert(insert_at, f"{indent}{PROBE}: object\n")
            path.write_text("".join(src_lines), encoding="utf-8")
            return Applied(
                True,
                f"Added required key {PROBE} to {cand.qualname}.",
                insert_line=insert_at + 1,
                line_delta=1,
            )
        return Applied(False, f"TypedDict {cand.qualname} wasn't found.")

    if cand.kind == "add_literal_variant":
        for node in ast.walk(tree):
            if getattr(node, "lineno", 0) != cand.lineno:
                continue
            value: ast.AST | None = None
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == cand.qualname
            ):
                value = node.value
            elif (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == cand.qualname
            ):
                value = node.value
            elif (
                TYPE_ALIAS_NODE is not None
                and isinstance(node, TYPE_ALIAS_NODE)
                and isinstance(node.name, ast.Name)
                and node.name.id == cand.qualname
            ):
                value = node.value
            if value is None or _literal_values(value) is None:
                continue
            alias = _annotation_src(lines, value) or ""
            closing = alias.rfind("]")
            if closing < 0:
                return Applied(False, f"Literal alias {cand.qualname} wasn't found.")
            new = alias[:closing] + f', "__{PROBE}__"' + alias[closing:]
            _replace_span(
                path, value.lineno, value.col_offset, value.end_col_offset, new
            )
            return Applied(True, f"Added a literal variant to {cand.qualname}.")
        return Applied(False, f"Literal alias {cand.qualname} wasn't found.")

    if cand.kind == "add_variant":
        for node in ast.walk(tree):
            if not (isinstance(node, ast.ClassDef) and node.name == cand.qualname):
                continue
            members = [
                s
                for s in node.body
                if isinstance(s, ast.Assign)
                and s.targets
                and isinstance(s.targets[0], ast.Name)
            ]
            if not members:
                return Applied(
                    False,
                    f"Enum {cand.qualname} has no members. Add a member before you retry the mutation.",
                )
            last = members[-1]
            value = _probe_enum_value(last, _base_names(node))
            indent = " " * (last.col_offset)
            insert_at = last.end_lineno or last.lineno
            src_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
            src_lines.insert(insert_at, f"{indent}{PROBE.upper()} = {value}\n")
            path.write_text("".join(src_lines), encoding="utf-8")
            return Applied(
                True,
                f"Added enum member {PROBE.upper()} = {value}.",
                insert_line=insert_at + 1,
                line_delta=1,
            )
        return Applied(
            False,
            f"Enum {cand.qualname} wasn't found. Run discovery again before you retry the mutation.",
        )

    return Applied(
        False,
        f"Mutation kind {cand.kind} isn't supported. Run discover to list supported kinds.",
    )


def _probe_enum_value(last: ast.Assign, bases: set[str]) -> str:
    v = last.value
    if isinstance(v, ast.Call):
        fn = v.func
        name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", "")
        if name == "auto":
            return "auto()"
    if isinstance(v, ast.Constant):
        if isinstance(v.value, str):
            return f'"__{PROBE}__"'
        if isinstance(v.value, int):
            return str(v.value + 9001)
    if bases & {"IntEnum", "IntFlag"}:
        return "424242"
    return f'"__{PROBE}__"'


# --------------------------------------------------------------------------
# Checker
# --------------------------------------------------------------------------

GENERIC_LOCATION = re.compile(
    r"(?:^|\s)(?:-->\s*)?(?P<file>(?:[A-Za-z]:)?[^:\n]+\.py):"
    r"(?P<line>\d+):(?P<col>\d+)"
)

# These patterns show that the checker did not analyze the code.
FATAL_PATTERNS = re.compile(
    r"Source file found twice|Cannot find implementation|INTERNAL ERROR|"
    r"is not a valid Python package|Duplicate module named|error: unrecognized|"
    r"No such file or directory|Cannot parse config",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Diag:
    relpath: str
    line: int
    code: str
    msg: str


def run_checker(
    work: Path,
    checker: str | None,
    checker_command: str | None,
    timeout: int,
    extra: list[str] | None = None,
    target: str = ".",
) -> tuple[list[Diag], str]:
    """Return the diagnostics and an error message.

    A nonempty error message means the checker run isn't valid.
    """
    if checker:
        cmd = [checker, "--outputjson", target, *(extra or [])]
        output_format = "pyright-json"
    else:
        try:
            command_parts = shlex.split(checker_command or "")
        except ValueError as exc:
            return [], f"The checker command isn't valid: {exc}. Fix --checker-command."
        if not command_parts:
            return (
                [],
                "No checker command was provided. Set --checker or --checker-command.",
            )
        has_target = any("{target}" in part for part in command_parts)
        cmd = [part.replace("{target}", target) for part in command_parts]
        if not has_target:
            cmd.append(target)
        cmd.extend(extra or [])
        output_format = "generic"

    try:
        proc = subprocess.run(
            cmd,
            cwd=work,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return [], (
            f"The checker executable {cmd[0]} wasn't found. Install the project's checker "
            "or fix the checker command."
        )
    except subprocess.TimeoutExpired:
        return [], (
            f"The checker timed out after {timeout} seconds. Increase --timeout or reduce the "
            "target scope."
        )

    out = proc.stdout or ""
    combined = out + "\n" + (proc.stderr or "")
    if FATAL_PATTERNS.search(combined):
        first = next(
            (line for line in combined.splitlines() if FATAL_PATTERNS.search(line)), ""
        )
        return [], (
            f"The checker couldn't analyze the tree: {first.strip()[:220]}. Fix the reported "
            "checker error, and then run the checker again."
        )
    if proc.returncode not in (0, 1):
        return [], (
            f"The checker exited with status {proc.returncode}, so the run isn't valid: "
            f"{combined.strip()[:220]}. Fix the reported error, and then run the checker again."
        )

    if output_format == "pyright-json":
        return _parse_pyright_output(out, work, checker or "checker")
    return _parse_generic_output(combined, work), ""


def _parse_pyright_output(out: str, work: Path, checker: str) -> tuple[list[Diag], str]:
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        return [], (
            f"The script couldn't parse {checker} output: {out[:200]}. Run the checker "
            "directly to inspect its output."
        )

    diags: list[Diag] = []
    for diagnostic in payload.get("generalDiagnostics", []):
        if diagnostic.get("severity") != "error":
            continue
        start = diagnostic.get("range", {}).get("start", {})
        diags.append(
            Diag(
                _relative_path(diagnostic.get("file", ""), work),
                int(start.get("line", 0)) + 1,
                diagnostic.get("rule", ""),
                (diagnostic.get("message") or "").splitlines()[0],
            )
        )
    return diags, ""


def _parse_generic_output(output: str, work: Path) -> list[Diag]:
    diags: list[Diag] = []
    for raw_line in output.splitlines():
        match = GENERIC_LOCATION.search(raw_line)
        if not match:
            continue
        diags.append(
            Diag(
                _relative_path(match.group("file").strip(), work),
                int(match.group("line")),
                "",
                raw_line.strip()[:220],
            )
        )
    return diags


def _relative_path(filename: str, work: Path) -> str:
    filename = filename.strip().removeprefix("-->").strip()
    path = Path(filename)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(work.resolve()).as_posix()
        except ValueError:
            pass
    return _norm(filename)


def _norm(p: str) -> str:
    return Path(p).as_posix().lstrip("./")


def _count_phrase(count: int, singular: str) -> str:
    noun = singular if count == 1 else f"{singular}s"
    return f"{count:,} {noun}"


# --------------------------------------------------------------------------
# Consumer sites
# --------------------------------------------------------------------------


@dataclass
class Site:
    relpath: str
    line: int
    category: str  # attribute | string | keyword | name
    text: str
    flagged: bool = False


def find_consumer_sites(root: Path, cand: Candidate, include_tests: bool) -> list[Site]:
    sym = cand.symbol
    if not sym:
        return []
    pats = [
        ("attribute", re.compile(rf"\.{re.escape(sym)}\b")),
        ("string", re.compile(rf"""['"]{re.escape(sym)}['"]""")),
        ("keyword", re.compile(rf"\b{re.escape(sym)}\s*=[^=]")),
    ]
    if cand.kind in {
        "add_variant",
        "add_literal_variant",
        "add_required_key",
        "optionalize",
        "retype_param",
        "break_relation",
        "extend_tuple",
    }:
        pats.append(("name", re.compile(rf"\b{re.escape(sym)}\b")))
    for extra in cand.extra_symbols:
        # Closed-set dispatch uses member names and values, not the enum class name.
        pats.append(("member", re.compile(rf"\b{re.escape(extra)}\b")))
        pats.append(("string", re.compile(rf"""['\"]{re.escape(extra)}['\"]""")))

    sites: list[Site] = []
    for path, rel in iter_py_files(root, include_tests):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(lines, 1):
            if rel == cand.relpath:
                # The definition block is not a consumer.
                if abs(i - cand.lineno) <= 1:
                    continue
                if cand.def_end and cand.lineno <= i <= cand.def_end:
                    continue
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for cat, pat in pats:
                if pat.search(line):
                    sites.append(Site(rel, i, cat, stripped[:160]))
                    break
    return sites


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


@dataclass
class Result:
    candidate: dict
    status: str  # ok | inconclusive | skipped
    note: str
    new_errors: int = 0
    new_error_files: int = 0
    sample_errors: list[str] = field(default_factory=list)
    sites_total: int = 0
    sites_flagged: int = 0
    unflagged: list[dict] = field(default_factory=list)
    verdict: str = ""


def copy_tree(root: Path) -> Path:
    dest = Path(tempfile.mkdtemp(prefix="erosion-"))
    work = dest / root.name
    shutil.copytree(
        root,
        work,
        ignore=shutil.ignore_patterns(*SKIP_DIRS, "*.pyc"),
        symlinks=True,
    )
    return work


def adjust(
    baseline: list[Diag], relpath: str, insert_line: int, delta: int
) -> set[Diag]:
    if not delta:
        return set(baseline)
    out = set()
    for d in baseline:
        if d.relpath == relpath and d.line >= insert_line:
            out.add(Diag(d.relpath, d.line + delta, d.code, d.msg))
        else:
            out.add(d)
    return out


def validate_baseline(
    root: Path, args: argparse.Namespace, cands: list[Candidate]
) -> str:
    """Confirm that the checker reads the files selected for mutation.

    The function adds a clear type error to each target in a temporary copy.
    Excluded files, skipped imports, and unchecked regions can cause the checker
    to report no errors, just as fully checked code can.
    """
    targets: list[str] = []
    for c in cands:
        if c.relpath not in targets:
            targets.append(c.relpath)
        if len(targets) >= 4:
            break
    if not targets:
        return ""

    work = copy_tree(root)
    try:
        for rel in targets:
            p = work / rel
            with p.open("a", encoding="utf-8") as fh:
                fh.write(f'\n_{PROBE}_canary: int = "definitely not an int"\n')
        diags, err = run_checker(
            work,
            args.checker,
            args.checker_command,
            args.timeout,
            args.checker_arg,
        )
        if err:
            return f"The verification run failed: {err}. Treat runs with no new errors as unproven."
        noisy = {d.relpath for d in diags}
        blind = [t for t in targets if t not in noisy]
        if blind:
            return (
                "The checker reported no error for "
                + ", ".join(blind)
                + " after the script added a deliberate type error. The checker might "
                "exclude these files, skip their imports, or ignore their function bodies. "
                "Report this verification gap instead of treating the files as safe."
            )
        return ""
    finally:
        shutil.rmtree(work.parent, ignore_errors=True)


def evaluate(
    cand: Candidate, args: argparse.Namespace, baseline: list[Diag], root: Path
) -> Result:
    work = copy_tree(root)
    try:
        applied = apply_mutation(work, cand)
        if not applied.ok:
            return Result(asdict(cand), "skipped", applied.note)

        diags, err = run_checker(
            work,
            args.checker,
            args.checker_command,
            args.timeout,
            args.checker_arg,
        )
        if err:
            return Result(asdict(cand), "inconclusive", err)

        base = adjust(baseline, cand.relpath, applied.insert_line, applied.line_delta)
        new = [d for d in diags if d not in base]

        # A mutation that breaks its declaration syntax provides no evidence.
        bad = {"syntax", "valid-type", "misc"}
        at_def = [d for d in new if d.relpath == cand.relpath and d.code in bad]
        if at_def and len(new) == len(at_def):
            return Result(
                asdict(cand),
                "inconclusive",
                f"The mutation produced an invalid declaration: {at_def[0].msg[:100]}. "
                "Treat this result as inconclusive.",
            )

        sites = find_consumer_sites(root, cand, args.include_tests)
        flagged_lines = {(d.relpath, d.line) for d in new}
        for s in sites:
            s.flagged = any(
                (s.relpath, s.line + off) in flagged_lines for off in (-1, 0, 1)
            )

        unflagged = [s for s in sites if not s.flagged]
        strings = [s for s in unflagged if s.category in {"string", "member"}]
        res = Result(
            candidate=asdict(cand),
            status="ok",
            note=applied.note,
            new_errors=len(new),
            new_error_files=len({d.relpath for d in new}),
            sample_errors=[
                f"{d.relpath}:{d.line} {d.msg[:110]} [{d.code}]" for d in new[:6]
            ],
            sites_total=len(sites),
            sites_flagged=len(sites) - len(unflagged),
            unflagged=[asdict(s) for s in unflagged[:25]],
        )
        if not sites:
            res.verdict = "No consumers found. This mutation provides no evidence."
        elif not unflagged:
            res.verdict = "Protected: The checker flagged every consumer site."
        elif strings:
            res.verdict = (
                f"Erosion: The mutation left {_count_phrase(len(strings), 'string-based site')} "
                f"without an error. In total, {_count_phrase(len(unflagged), 'site')} received "
                "no error."
            )
        else:
            res.verdict = (
                f"Review needed: {len(unflagged):,} of {len(sites):,} consumer sites received "
                "no error. Confirm that each site consumes this symbol."
            )
        return res
    finally:
        shutil.rmtree(work.parent, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in ("discover", "run"):
        p = sub.add_parser(name)
        p.add_argument("--root", default=".", help="Set the project root.")
        p.add_argument(
            "--kind",
            action="append",
            choices=[
                "rename",
                "retype",
                "retype_param",
                "add_variant",
                "add_literal_variant",
                "add_required_key",
                "optionalize",
                "break_relation",
                "extend_tuple",
            ],
            help="Limit the run to a mutation kind. Repeat this option as needed.",
        )
        p.add_argument(
            "--target",
            action="append",
            help="Limit the run to a qualified name, such as User.email. Repeat as needed.",
        )
        p.add_argument(
            "--include-tests", action="store_true", help="Include test files."
        )
        p.add_argument("--json", help="Write the full results to this JSON file.")
        if name == "run":
            checker_group = p.add_mutually_exclusive_group(required=True)
            checker_group.add_argument(
                "--checker",
                choices=["pyright", "basedpyright"],
                help="Use the project's Pyright or basedpyright command.",
            )
            checker_group.add_argument(
                "--checker-command",
                help=(
                    "Run another project checker command. Use {target} where the copied "
                    "project path belongs. The script appends the path when omitted."
                ),
            )
            p.add_argument(
                "--limit",
                type=int,
                default=12,
                help="Set the maximum mutation count. The default is 12.",
            )
            p.add_argument(
                "--timeout", type=int, default=300, help="Set the timeout in seconds."
            )
            p.add_argument(
                "--checker-arg",
                action="append",
                default=[],
                help="Pass an extra checker option. Repeat this option as needed.",
            )

    args = ap.parse_args()
    if not hasattr(args, "checker_arg"):
        args.checker_arg = []
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(
            f"The project root isn't a directory: {root}. Set --root to an existing directory.",
            file=sys.stderr,
        )
        return 2

    cands = discover(root, args.include_tests)
    if args.kind:
        cands = [c for c in cands if c.kind in args.kind]
    if args.target:
        want = set(args.target)
        cands = [c for c in cands if c.qualname in want or c.symbol in want]

    if args.cmd == "discover":
        by_kind: dict[str, list[Candidate]] = {}
        for c in cands:
            by_kind.setdefault(c.kind, []).append(c)
        print(f"The script found {len(cands):,} mutation candidates in {root}.\n")
        for kind in (
            "rename",
            "retype",
            "retype_param",
            "add_variant",
            "add_literal_variant",
            "add_required_key",
            "optionalize",
            "break_relation",
            "extend_tuple",
        ):
            group = by_kind.get(kind, [])
            if not group:
                continue
            print(f"[{kind}] {len(group):,}")
            for c in group[:40]:
                print(f"  {c.qualname:<44} {c.relpath}:{c.lineno}  {c.detail}")
            if len(group) > 40:
                print(f"  ... {len(group) - 40:,} more")
            print()
        print(
            "Candidates are a starting inventory, not a complete list. Dynamic access "
            "often has no declared field to mutate. Review the code for these cases."
        )
        if args.json:
            Path(args.json).write_text(json.dumps([asdict(c) for c in cands], indent=2))
        return 0

    checker_label = args.checker or "the project checker command"
    print(
        f"The script is running the {checker_label} baseline on {root}.",
        file=sys.stderr,
    )
    work = copy_tree(root)
    try:
        baseline, err = run_checker(
            work,
            args.checker,
            args.checker_command,
            args.timeout,
            args.checker_arg,
        )
    finally:
        shutil.rmtree(work.parent, ignore_errors=True)
    if err:
        print(f"The script can't establish the baseline: {err}", file=sys.stderr)
        print(
            "\nThis method requires a working checker. A checker that doesn't analyze the "
            "code can report no errors, which can look like full type coverage. Fix missing "
            "packages, imports, or checker "
            "options. Pass extra options with --checker-arg. If the checker cannot run, "
            "trace consumers by hand as SKILL.md describes. Do not report a clean result "
            "from a failed baseline.",
            file=sys.stderr,
        )
        return 1
    print(
        f"The {checker_label} baseline reported {len(baseline):,} existing errors.",
        file=sys.stderr,
    )

    # A checker that reaches no code can look like a successful check.
    probe = validate_baseline(root, args, cands[: args.limit])
    if probe:
        print(f"Warning: {probe}", file=sys.stderr)
    print(file=sys.stderr)

    results: list[Result] = []
    seen: set[str] = set()
    for cand in cands:
        if len(results) >= args.limit:
            break
        if cand.key in seen:
            continue
        seen.add(cand.key)
        res = evaluate(cand, args, baseline, root)
        results.append(res)
        error_count = _count_phrase(res.new_errors, "new error")
        print(
            f"{cand.kind:<12} {cand.qualname:<40} "
            f"{error_count:>12}  {res.status:<13} {res.verdict or res.note}"
        )

    eroded = [
        result
        for result in results
        if result.status == "ok"
        and result.verdict.startswith(("Erosion:", "Review needed:"))
    ]
    print(
        f"\nThe script ran {_count_phrase(len(results), 'mutation')} and found "
        f"{_count_phrase(len(eroded), 'mutation')} with unflagged consumer sites."
    )
    if eroded:
        print(
            "Review each unflagged site before you report it. Name the edit that causes "
            "the silent break. See the report format in SKILL.md."
        )
    if args.json:
        Path(args.json).write_text(
            json.dumps(
                {
                    "root": str(root),
                    "checker": args.checker,
                    "checker_command": args.checker_command,
                    "baseline_errors": len(baseline),
                    "results": [asdict(r) for r in results],
                },
                indent=2,
            )
        )
        print(f"Full results: {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
