"""
BONIF - Hidden Instructor Test Suite
=====================================

These tests detect structural evidence of improvements to the base weather
station code. They analyze code via AST and regex -- NO student code is
imported or executed.

Each test maps to an intentional gap in the base code (main.py docstring
lists 8 gaps). Students must make improvements; these tests detect evidence
of those improvements automatically.

Results inform the oral validation discussion (IND-00SX-D, 20%).
"""

import ast
import io
import re
import tokenize
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_repo_root():
    """Find the repository root by looking for .github folder."""
    current = Path(__file__).parent.parent
    if (current / ".github").exists():
        return current
    return current


REPO_ROOT = _get_repo_root()
MAIN_PY = REPO_ROOT / "main.py"
SENSORS_DIR = REPO_ROOT / "sensors"


def _parse_file(filepath):
    """
    Read and parse a Python file via AST.

    Returns:
        tuple: (ast.Module, str) -- the AST tree and raw content,
               or None if the file does not exist or has syntax errors.
    """
    path = Path(filepath)
    if not path.exists():
        return None
    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        return tree, content
    except SyntaxError:
        return None


def _find_python_files(root):
    """
    Find all .py files under *root*, excluding hidden directories (.venv/,
    .git/, .tox/, .mypy_cache/, etc.) and __pycache__/ directories.

    Returns:
        list[Path]: Python file paths found.
    """
    root = Path(root)
    result = []
    for f in root.rglob("*.py"):
        parts = f.relative_to(root).parts
        if not any(p.startswith('.') or p == '__pycache__' for p in parts):
            result.append(f)
    return result


def _strip_comments_and_docstrings(source: str) -> str:
    """Remove comments and docstrings from Python source code."""
    result = []
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        prev_toktype = tokenize.INDENT
        for toktype, tokval, _, _, _ in tokens:
            if toktype == tokenize.COMMENT:
                continue
            elif toktype == tokenize.STRING:
                if prev_toktype in (
                    tokenize.INDENT,
                    tokenize.NEWLINE,
                    tokenize.NL,
                    tokenize.DEDENT,
                ):
                    # This is a docstring -- skip it
                    continue
            result.append(tokval)
            if toktype not in (
                tokenize.NL,
                tokenize.NEWLINE,
                tokenize.INDENT,
                tokenize.DEDENT,
            ):
                prev_toktype = toktype
    except tokenize.TokenError:
        # If tokenization fails, return original source
        return source
    return " ".join(result)


# ---------------------------------------------------------------------------
# Test 1: Error Handling Added
# ---------------------------------------------------------------------------

def test_error_handling_added():
    """
    Detect try/except blocks in main.py.

    The base code has 0 try/except blocks. Any try/except is evidence that
    the student added error handling (gap #1 in base code).
    """
    result = _parse_file(MAIN_PY)
    if result is None:
        pytest.skip("main.py not found or has syntax errors")

    tree, _ = result
    try_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.Try)]

    if len(try_nodes) == 0:
        pytest.fail(
            "\n\n"
            "Expected: At least one try/except block in main.py\n"
            "Actual:   0 try/except blocks found\n\n"
            "Suggestion: Ajoutez la gestion d'erreurs pour les lectures capteur:\n"
            "  try:\n"
            "      temperature = sensor.temperature\n"
            "  except Exception as e:\n"
            "      print(f'Erreur de lecture: {e}')\n"
        )


# ---------------------------------------------------------------------------
# Test 2: KeyboardInterrupt Handling
# ---------------------------------------------------------------------------

def test_keyboard_interrupt_handling():
    """
    Detect KeyboardInterrupt handling in main.py.

    The base code crashes on Ctrl+C (gap #6). A proper station should shut
    down gracefully.
    """
    result = _parse_file(MAIN_PY)
    if result is None:
        pytest.skip("main.py not found or has syntax errors")

    tree, content = result

    # AST -- look for ExceptHandler with KeyboardInterrupt
    found_ast = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if node.type is not None:
                if isinstance(node.type, ast.Name) and node.type.id == "KeyboardInterrupt":
                    found_ast = True
                    break
                elif isinstance(node.type, ast.Tuple):
                    for elt in node.type.elts:
                        if isinstance(elt, ast.Name) and elt.id == "KeyboardInterrupt":
                            found_ast = True
                            break
                    if found_ast:
                        break

    if not found_ast:
        pytest.fail(
            "\n\n"
            "Expected: KeyboardInterrupt handling in main.py\n"
            "Actual:   No KeyboardInterrupt handler found\n\n"
            "Suggestion: Gerez l'arret propre avec Ctrl+C:\n"
            "  try:\n"
            "      while True:\n"
            "          # ... lecture capteur ...\n"
            "  except KeyboardInterrupt:\n"
            "      print('Arret propre de la station.')\n"
        )


# ---------------------------------------------------------------------------
# Test 3: Data Validation Present
# ---------------------------------------------------------------------------

def test_data_validation_present():
    """
    Detect data validation logic (range checks on sensor values).

    The base code does not validate sensor readings (gap #2). Students should
    check for unrealistic values (e.g., temperature > 100 or < -50).
    """
    result = _parse_file(MAIN_PY)
    if result is None:
        pytest.skip("main.py not found or has syntax errors")

    _, content = result
    stripped = _strip_comments_and_docstrings(content)

    # Look for comparison operators near sensor-related variable names
    patterns = [
        r"(temperature|temp|humidity|humidite|hum)\s*[<>]=?\s*-?\d",
        r"-?\d+\.?\d*\s*[<>]=?\s*(temperature|temp|humidity|humidite|hum)",
        r"(is_valid|valide|validate|validation|plage|range|aberrant)",
        r"(MIN_|MAX_|SEUIL_|THRESHOLD)",
    ]

    found = any(re.search(p, stripped, re.IGNORECASE) for p in patterns)

    if not found:
        pytest.fail(
            "\n\n"
            "Expected: Data validation (range checks on sensor values)\n"
            "Actual:   No validation patterns found in main.py\n\n"
            "Suggestion: Validez les valeurs avant de les afficher:\n"
            "  if temperature < -50 or temperature > 100:\n"
            "      print('Valeur aberrante!')\n"
            "  MIN_TEMPERATURE = -40\n"
            "  MAX_TEMPERATURE = 120\n"
        )


# ---------------------------------------------------------------------------
# Test 4: Timestamp Added
# ---------------------------------------------------------------------------

def test_timestamp_added():
    """
    Detect datetime or time.strftime usage in main.py.

    The base code has no timestamps (gap #4). Measurements should be
    time-stamped for traceability.
    """
    result = _parse_file(MAIN_PY)
    if result is None:
        pytest.skip("main.py not found or has syntax errors")

    tree, content = result

    # AST: look for import of datetime or time.strftime usage
    found_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in ("datetime",):
                    found_import = True
        elif isinstance(node, ast.ImportFrom):
            if node.module in ("datetime", "time"):
                found_import = True

    # Regex fallback: strftime, isoformat, datetime.now
    found_regex = bool(re.search(
        r"(strftime|isoformat|datetime\.now|datetime\.utcnow|time\.ctime|time\.localtime)",
        content,
    ))

    if not found_import and not found_regex:
        pytest.fail(
            "\n\n"
            "Expected: Timestamp usage (datetime or time.strftime)\n"
            "Actual:   No timestamp import or usage found\n\n"
            "Suggestion: Ajoutez un horodatage a chaque mesure:\n"
            "  from datetime import datetime\n"
            "  timestamp = datetime.now().isoformat()\n"
            "  print(f'{timestamp} - Temperature: {temp:.1f} C')\n"
        )


# ---------------------------------------------------------------------------
# Test 5: Configuration Externalized
# ---------------------------------------------------------------------------

def test_configuration_externalized():
    """
    Detect externalized configuration (argparse, configparser, env vars,
    or significant UPPERCASE constants).

    The base code hardcodes the sleep interval (gap #5). Configuration
    should be adjustable without modifying source code.
    """
    result = _parse_file(MAIN_PY)
    if result is None:
        pytest.skip("main.py not found or has syntax errors")

    tree, content = result

    # AST: look for argparse, click, configparser, os.environ imports
    config_imports = {"argparse", "click", "configparser", "dotenv"}
    found_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in config_imports:
                    found_import = True
        elif isinstance(node, ast.ImportFrom):
            if node.module in config_imports or (node.module and node.module.startswith("os")):
                # Check for os.environ usage
                if node.module == "os":
                    found_import = True

    # Regex: os.environ.get, os.getenv, or many UPPERCASE constants
    found_env = bool(re.search(r"os\.(environ|getenv)", content))
    uppercase_constants = re.findall(r"^[A-Z][A-Z_0-9]{2,}\s*=", content, re.MULTILINE)
    # Base code has very few constants; 3+ suggests externalization effort
    found_constants = len(uppercase_constants) >= 3

    if not found_import and not found_env and not found_constants:
        pytest.fail(
            "\n\n"
            "Expected: Externalized configuration (argparse, env vars, or constants)\n"
            "Actual:   No configuration mechanism found\n\n"
            "Suggestion: Rendez la configuration ajustable:\n"
            "  # Option 1: Constants\n"
            "  INTERVAL = 5\n"
            "  MAX_RETRIES = 3\n"
            "  SENSOR_TYPE = 'AHT20'\n\n"
            "  # Option 2: argparse\n"
            "  import argparse\n"
            "  parser = argparse.ArgumentParser()\n"
            "  parser.add_argument('--interval', type=int, default=5)\n\n"
            "  # Option 3: Environment variable\n"
            "  import os\n"
            "  interval = int(os.environ.get('INTERVAL', 5))\n"
        )


# ---------------------------------------------------------------------------
# Test 6: Additional Sensor Integration
# ---------------------------------------------------------------------------

def test_additional_sensor_integration():
    """
    Detect import of additional Adafruit sensor libraries beyond AHT20.

    The base code only uses AHT20 (gap #7 -- monolithic). Adding sensors
    like HTS221, AS7341, VCNL4200, or Neoslider shows expansion.
    """
    # Scan all .py files in repo root and sensors/ directory
    search_dirs = [REPO_ROOT, SENSORS_DIR]
    all_py_files = []
    for d in search_dirs:
        if d.exists():
            for f in d.glob("*.py"):
                all_py_files.append(f)
    # Also check subdirectories of sensors/
    if SENSORS_DIR.exists():
        for f in SENSORS_DIR.rglob("*.py"):
            if f not in all_py_files:
                all_py_files.append(f)

    additional_sensors = [
        "hts221", "as7341", "vcnl4200", "seesaw",
        "bmp280", "bme280", "bme680", "dht",
    ]

    found_sensors = []
    for py_file in all_py_files:
        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue
        for sensor in additional_sensors:
            if re.search(rf"(import|from).*{sensor}", content, re.IGNORECASE):
                found_sensors.append(sensor)

    if not found_sensors:
        pytest.fail(
            "\n\n"
            "Expected: At least one additional sensor library imported\n"
            "Actual:   Only AHT20 detected (base code)\n\n"
            "Suggestion: Integrez un capteur supplementaire:\n"
            "  # HTS221 (temperature/humidite alternative)\n"
            "  from adafruit_hts221 import HTS221\n\n"
            "  # AS7341 (spectrometre, analyse couvert nuageux)\n"
            "  from adafruit_as7341 import AS7341\n\n"
            "  # VCNL4200 (luminosite, proximite)\n"
            "  from adafruit_vcnl4200 import VCNL4200\n"
        )


# ---------------------------------------------------------------------------
# Test 7: Data Persistence
# ---------------------------------------------------------------------------

def test_data_persistence():
    """
    Detect CSV or JSON data persistence (file I/O with structured format).

    The base code does not persist data. Students should save measurements
    to files for later analysis.
    """
    # Check all .py files in the repo
    all_py = _find_python_files(REPO_ROOT)

    found_persistence = False
    for py_file in all_py:
        result = _parse_file(py_file)
        if result is None:
            continue
        tree, content = result

        # AST: look for csv or json import
        has_format_import = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("csv", "json"):
                        has_format_import = True
            elif isinstance(node, ast.ImportFrom):
                if node.module in ("csv", "json"):
                    has_format_import = True

        # Also check for open() usage with write mode
        has_file_write = bool(re.search(
            r"open\s*\(.+['\"]w['\"]|['\"]a['\"]",
            content,
        ))

        if has_format_import and has_file_write:
            found_persistence = True
            break

        # Looser check: just csv/json import is strong evidence
        if has_format_import and re.search(r"(write|dump|save|append|fichier|file)", content, re.IGNORECASE):
            found_persistence = True
            break

    if not found_persistence:
        pytest.fail(
            "\n\n"
            "Expected: Data persistence (csv or json with file writing)\n"
            "Actual:   No data persistence pattern found\n\n"
            "Suggestion: Sauvegardez les mesures dans un fichier:\n"
            "  import csv\n"
            "  with open('data/mesures.csv', 'a') as f:\n"
            "      writer = csv.writer(f)\n"
            "      writer.writerow([timestamp, temperature, humidity])\n"
        )


# ---------------------------------------------------------------------------
# Test 8: Student Tests Written
# ---------------------------------------------------------------------------

def test_tests_written():
    """
    Check for student-written test files in the tests/ directory.

    The base code has no tests. Writing tests shows quality consciousness
    (Category C improvement).
    """
    tests_dir = REPO_ROOT / "tests"
    if not tests_dir.exists():
        pytest.fail(
            "\n\n"
            "Expected: tests/ directory with test files\n"
            "Actual:   tests/ directory not found\n\n"
            "Suggestion: Creez des tests pour votre code:\n"
            "  mkdir tests\n"
            "  # Creez tests/test_sensors.py avec vos tests pytest\n"
        )

    # Find test files (excluding this file)
    test_files = [
        f for f in tests_dir.glob("test_*.py")
        if f.name != "test_instructor.py"
    ]

    if not test_files:
        pytest.fail(
            "\n\n"
            "Expected: At least one test_*.py file in tests/ (besides test_instructor.py)\n"
            f"Actual:   0 student test files found in {tests_dir}\n\n"
            "Suggestion: Ecrivez des tests pour vos fonctions:\n"
            "  # tests/test_sensors.py\n"
            "  def test_temperature_range():\n"
            "      assert -50 <= temperature <= 100\n"
        )


# ---------------------------------------------------------------------------
# Test 9: Documentation Improved
# ---------------------------------------------------------------------------

def test_documentation_improved():
    """
    Count docstrings in main.py.

    The base code has approximately 2 docstrings (module + main function).
    An increase suggests the student improved documentation (gap #8).
    """
    result = _parse_file(MAIN_PY)
    if result is None:
        pytest.skip("main.py not found or has syntax errors")

    tree, _ = result

    # Count docstrings: ast.Expr nodes containing ast.Constant with str
    docstring_count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            if (node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)):
                docstring_count += 1

    # Base code has ~2 docstrings (module docstring + main() docstring)
    BASE_DOCSTRINGS = 2

    if docstring_count <= BASE_DOCSTRINGS:
        pytest.fail(
            "\n\n"
            f"Expected: More than {BASE_DOCSTRINGS} docstrings (base code level)\n"
            f"Actual:   {docstring_count} docstring(s) found\n\n"
            "Suggestion: Ajoutez des docstrings a vos fonctions:\n"
            "  def read_temperature(sensor):\n"
            "      \"\"\"Lit la temperature du capteur en Celsius.\"\"\"\n"
            "      ...\n"
        )


# ---------------------------------------------------------------------------
# Test 10: Code Modularization
# ---------------------------------------------------------------------------

def test_code_modularization():
    """
    Check for new .py files in sensors/ or new directories (utils/, config/).

    The base code is monolithic with only sensors/aht20_sensor.py (gap #7).
    New modules or directories show modularization effort.
    """
    # Check for new .py files in sensors/ beyond aht20_sensor.py and __init__.py
    new_sensor_files = []
    if SENSORS_DIR.exists():
        for f in SENSORS_DIR.glob("*.py"):
            if f.name not in ("__init__.py", "aht20_sensor.py"):
                new_sensor_files.append(f.name)

    # Check for new directories (utils/, config/, data/, lib/, etc.)
    # Exclude standard dirs that exist in base: .github, sensors, tests, data
    base_dirs = {".github", "sensors", "tests", "data", "__pycache__", ".venv", ".git"}
    new_dirs = []
    for item in REPO_ROOT.iterdir():
        if item.is_dir() and item.name not in base_dirs and not item.name.startswith("."):
            new_dirs.append(item.name)

    # Check for new .py files at root (beyond main.py)
    base_root_files = {"main.py"}
    new_root_py = [
        f.name for f in REPO_ROOT.glob("*.py")
        if f.name not in base_root_files
    ]

    has_modularization = bool(new_sensor_files or new_dirs or new_root_py)

    if not has_modularization:
        pytest.fail(
            "\n\n"
            "Expected: Code modularization (new modules or directories)\n"
            "Actual:   Only base code files found (main.py + sensors/aht20_sensor.py)\n\n"
            "Suggestion: Separarez votre code en modules:\n"
            "  sensors/aht20_sensor.py    # Nouveau capteur\n"
            "  utils/validation.py        # Fonctions de validation\n"
            "  config/settings.py         # Configuration centralisee\n"
        )


# ---------------------------------------------------------------------------
# Test 11: Non-Blocking Timer Pattern
# ---------------------------------------------------------------------------

def test_timer_pattern():
    """
    Detect time.monotonic() usage for non-blocking timing.

    The base code uses time.sleep(5) in a blocking loop. Upgrading to
    time.monotonic() with interval comparison shows the student applied
    the timer-in-loop pattern from semaine 4.
    """
    result = _parse_file(MAIN_PY)
    if result is None:
        pytest.skip("main.py not found or has syntax errors")

    _, content = result

    # Check for time.monotonic usage (timer-in-loop pattern)
    has_monotonic = "time.monotonic" in content or "monotonic()" in content

    # Check for interval comparison (evidence of timer pattern)
    has_interval = bool(re.search(
        r'\w+\s*-\s*\w+\s*>=?\s*\w+',
        content,
    ))

    if not has_monotonic:
        pytest.fail(
            "\n\n"
            "Expected: time.monotonic() usage for non-blocking timing\n"
            "Actual:   No time.monotonic() found\n\n"
            "Suggestion: Remplacez time.sleep() par le pattern timer-in-loop:\n"
            "  previous = time.monotonic()\n"
            "  while True:\n"
            "      current = time.monotonic()\n"
            "      if current - previous >= INTERVAL:\n"
            "          read_sensor(sensor)\n"
            "          previous = current\n"
            "      time.sleep(0.05)  # Polling rapide\n"
        )
