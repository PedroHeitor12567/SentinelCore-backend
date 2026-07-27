import ast
from pathlib import Path

FORBIDDEN_MODULES = {"fastapi", "starlette", "sqlalchemy", "uvicorn", "pydantic", "alembic"}

SRC_ROOT = Path(__file__).resolve().parents[2] / "src" / "sentinelcore"


def _imported_modules(file_path: Path) -> set[str]:
    tree = ast.parse(file_path.read_text())
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    return modules


def _domain_directories() -> list[Path]:
    return [path for path in SRC_ROOT.rglob("domain") if path.is_dir()]


def test_domain_layer_has_no_framework_dependencies() -> None:
    violations: dict[str, set[str]] = {}
    for domain_dir in _domain_directories():
        for py_file in domain_dir.glob("*.py"):
            forbidden = _imported_modules(py_file) & FORBIDDEN_MODULES
            if forbidden:
                violations[str(py_file.relative_to(SRC_ROOT))] = forbidden

    assert not violations, f"Domain layer depends on framework code: {violations}"
