### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: read_file
{"file_path": "skills/maintain-code-quality/SKILL.md", "limit": 1000}

### Tool call: read_file
{"limit": 1000, "file_path": "skills/enhance-testing-practices/SKILL.md"}

### Tool call: read_file
{"limit": 1000, "file_path": "skills/improve-data-validation/SKILL.md"}

### Tool result
@@ lines 1-9 of 9 @@
---
name: maintain-code-quality
description: Use when writing or refactoring code to ensure adherence to best practices and maintainability.
---
1. **Follow Coding Standards**: Adhere to established coding standards and style guides for consistency across the codebase.
2. **Document Code Thoroughly**: Include docstrings for all functions and classes, explaining their purpose, parameters, and return values.
3. **Use Version Control Effectively**: Commit changes frequently with clear, descriptive messages that explain the purpose of the changes.
4. **Maintain a Changelog**: Keep a changelog updated with all changes made, including bug fixes, new features, and improvements, categorized by version.
5. **Conduct Code Reviews**: Regularly participate in code reviews to provide and receive feedback, ensuring code quality and sharing knowledge among team members.

### Tool result
@@ lines 1-9 of 9 @@
---
name: enhance-testing-practices
description: Use when developing and maintaining tests for code changes and new features.
---
1. **Write Regression Tests**: For every bug fix, create a regression test that replicates the issue to ensure it does not reoccur in the future.
2. **Organize Tests Logically**: Structure tests in a clear hierarchy, grouping related tests together and naming them descriptively to indicate their purpose.
3. **Use Assertions Effectively**: Utilize assertions to check for expected outcomes, ensuring that tests fail when the actual output does not match the expected output.
4. **Run Tests Regularly**: Integrate automated testing into the development workflow, running tests after every significant change to catch issues early.
5. **Document Test Cases**: Provide clear documentation for each test case, explaining its purpose, expected inputs, and expected outputs.

### Tool result
@@ lines 1-9 of 9 @@
---
name: improve-data-validation
description: Use when validating data formats and ensuring data integrity in processing tasks.
---
1. **Define Expected Formats**: Clearly document the expected formats for all data inputs, including types (e.g., string, integer, decimal) and structures (e.g., JSON schema).
2. **Implement Input Validation**: Before processing, validate all inputs against the defined formats. Use try-except blocks to catch and handle exceptions gracefully.
3. **Log Validation Errors**: Maintain a log of any validation errors encountered during processing, including the input that caused the error and a description of the issue.
4. **Use Type Annotations**: Ensure all public functions have type annotations for parameters and return values to clarify expected data types.
5. **Test Edge Cases**: Create unit tests that cover edge cases and invalid inputs to ensure robustness against unexpected data formats.

### Tool call: glob
{"path": "workspace", "pattern": "**"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/__init__.cpython-313.pyc', '/workspace/bookings/__pycache__/billing.cpython-313.pyc', '/workspace/bookings/__pycache__/calendar_export.cpython-313.pyc', '/workspace/bookings/__pycache__/schedule.cpython-313.pyc', '/workspace/bookings/__pycache__/timeutil.cpython-313.pyc', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/__pycache__/test_bookings.cpython-313-pytest-9.1.1.pyc', '/workspace/tests/test_bookings.py']

### Tool call: glob
{"path": ".", "pattern": "*"}

### Tool result
['/skills/enhance-testing-practices/SKILL.md', '/skills/improve-data-validation/SKILL.md', '/skills/maintain-code-quality/SKILL.md', '/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/__init__.cpython-313.pyc', '/workspace/bookings/__pycache__/billing.cpython-313.pyc', '/workspace/bookings/__pycache__/calendar_export.cpython-313.pyc', '/workspace/bookings/__pycache__/schedule.cpython-313.pyc', '/workspace/bookings/__pycache__/timeutil.cpython-313.pyc', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/__pycache__/test_bookings.cpython-313-pytest-9.1.1.pyc', '/workspace/tests/test_bookings.py']

### Tool call: glob
{"path": ".", "pattern": ".*"}

### Tool result
No files found

### Tool call: glob
{"pattern": ".*", "path": "workspace"}

### Tool result
No files found

### Tool call: read_file
{"limit": 1000, "file_path": "workspace/README.md"}

### Tool call: read_file
{"file_path": "workspace/CHANGELOG.md", "limit": 1000}

### Tool result
@@ lines 1-5 of 5 @@
# bookings

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 1.4.2
- initial import

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q"}

### Tool result
FF.                                                                      [100%]
=================================== FAILURES ===================================
_______________________ test_total_minutes_mixed_formats _______________________

    def test_total_minutes_mixed_formats():
>       assert total_minutes(["1h30m", "2h"]) == 210
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

~/AI20K/K4-DAY20-MULTIAGENTS-LeMinhSang-2A202602864/tasks/code-eval/workspace/tests/test_bookings.py:6: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
bookings/schedule.py:7: in total_minutes
    return sum(parse_duration(d) for d in durations)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
bookings/schedule.py:7: in <genexpr>
    return sum(parse_duration(d) for d in durations)
               ^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

text = '2h'

    def parse_duration(text):
        """Convert a duration string to whole minutes (int).
    
        Supported formats:
          "1h30m" -> 90
          "2h"    -> 120
          "45m"   -> 45
          "1:30"  -> 90
          "45"    -> 45    # a bare number means minutes
        Surrounding whitespace is ignored.
        """
        m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
        if not m:
>           raise ValueError(f"bad duration: {text!r}")
E           ValueError: bad duration: '2h'

bookings/timeutil.py:18: ValueError
____________________

### Tool call: grep
{"pattern": "Acme"}

### Tool result
No matches found

### Tool call: grep
{"path": "workspace", "pattern": "Acme"}

### Tool result
No matches found

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py", "limit": 1000}

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Tool call: read_file
{"file_path": "workspace/bookings/__init__.py", "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py", "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py", "limit": 1000}

### Tool call: read_file
{"limit": 1000, "file_path": "workspace/bookings/schedule.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/calendar_export.py", "limit": 1000}

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool call: execute
{"command": "git status"}

### Tool result
[stderr] fatal: not a git repository (or any of the parent directories): .git

Exit code: 128
[Command failed with exit code 128]

### Tool call: execute
{"command": "which ruff flake8 black mypy pylint pytest python"}

### Tool result
~/AI20K/K4-DAY20-MULTIAGENTS-LeMinhSang-2A202602864/.venv/bin/pytest
~/AI20K/K4-DAY20-MULTIAGENTS-LeMinhSang-2A202602864/.venv/bin/python

Exit code: 1
[Command failed with exit code 1]

### Tool call: execute
{"command": "find / -name \"*acme*\" 2>/dev/null || true"}

### Tool result
Error: Command timed out after 120 seconds. For long-running commands, re-run using the timeout parameter.
[Command failed with exit code 124]