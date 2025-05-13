import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "main.py"


def test_console_output():
    result = subprocess.run([sys.executable, SRC], capture_output=True, text=True)
    assert result.stdout.strip() == "Hello, World!!"


def test_exit_code_and_single_line():
    """Le script doit quitter avec un code 0 et n’afficher qu’une ligne."""
    completed = subprocess.run([sys.executable, SRC], capture_output=True, text=True)
    # 1. Retour 0 = exécution sans erreur
    assert completed.returncode == 0
    # 2. Une seule ligne exacte
    lines = completed.stdout.strip().splitlines()
    assert len(lines) == 1 and lines[0] == "Hello, World!!"
