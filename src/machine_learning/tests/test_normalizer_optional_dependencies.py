"""Regression tests for optional ML dependency isolation."""

from pathlib import Path
import subprocess
import sys
import textwrap


def test_normalizer_import_does_not_require_ml_dependencies():
    script = textwrap.dedent(
        """
        import importlib.abc
        import sys

        blocked = {"numpy", "pandas", "sklearn", "matplotlib"}

        class BlockOptionalMlDependencies(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname.split(".", 1)[0] in blocked:
                    raise ModuleNotFoundError(
                        f"optional ML dependency blocked for test: {fullname}"
                    )
                return None

        sys.meta_path.insert(0, BlockOptionalMlDependencies())
        import src.machine_learning.normalize_power655  # noqa: F401
        """
    )
    repository_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=repository_root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, (
        "Normalizer import unexpectedly required optional ML dependencies.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
