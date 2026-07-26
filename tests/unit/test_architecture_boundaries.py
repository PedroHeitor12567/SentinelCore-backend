import ast
from pathlib import Path

FORBIDDEN_MODULES = {"fastapi", "starlette", "sqlalchemy", "uvicorn", "pydantic", "alembic"}

DOMAIN_DIR = Path(__file__).resolve().parents[2] / "src" / "sentinelcore" / "shared" / "domain"


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


def test_domain_layer_has_no_framework_dependencies() -> None:
    violations: dict[str, set[str]] = {}
    for py_file in DOMAIN_DIR.glob("*.py"):
        forbidden = _imported_modules(py_file) & FORBIDDEN_MODULES
        if forbidden:
            violations[py_file.name] = forbidden

    assert not violations, f"Domain layer depends on framework code: {violations}"
