### Human
The test suite of the `inventory` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: ls
{"path": "/workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/inventory/', '/workspace/tests/']

### Tool call: ls
{"path": "/workspace/inventory"}

### Tool result
['/workspace/inventory/__init__.py', '/workspace/inventory/__pycache__/', '/workspace/inventory/export.py', '/workspace/inventory/pricing.py', '/workspace/inventory/report.py']

### Tool call: read_file
{"file_path": "/workspace/inventory/export.py"}

### Tool call: read_file
{"file_path": "/workspace/inventory/pricing.py"}

### Tool call: read_file
{"file_path": "/workspace/inventory/report.py"}

### Tool result
@@ lines 1-12 of 12 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    price = parse_price(item["price"])
    return f'{item["name"]},{price:.2f},{item["qty"]}'

### Tool result
@@ lines 1-25 of 25 @@
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"))

### Tool result
@@ lines 1-25 of 25 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    return [item["name"] for item in items if item["qty"] <= threshold]

### Tool call: read_file
{"file_path": "/workspace/tests/test_export.py"}

### Tool result
Error: File '/workspace/tests/test_export.py' not found

### Tool call: ls
{"path": "/workspace/tests"}

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_report.py']

### Tool call: read_file
{"file_path": "/workspace/tests/test_report.py"}

### Tool result
@@ lines 1-32 of 32 @@
from decimal import Decimal

from inventory.export import to_csv_row
from inventory.pricing import apply_discount
from inventory.report import low_stock, total_value


def test_total_value_plain():
    items = [{"name": "pen", "price": "$2.50", "qty": 4}]
    assert total_value(items) == Decimal("10.00")


def test_total_value_thousands_separator():
    items = [{"name": "laptop", "price": "$1,299.50", "qty": 2}]
    assert total_value(items) == Decimal("2599.00")


def test_discount_rounding_half_up():
    assert apply_discount(Decimal("10.05"), 10) == Decimal("9.05")


def test_total_value_with_discount():
    items = [{"name": "desk", "price": "100.00", "qty": 1, "discount": 15}]
    assert total_value(items) == Decimal("85.00")


def test_low_stock_basic():
    assert low_stock([{"name": "pen", "qty": 2}, {"name": "ink", "qty": 9}]) == ["pen"]


def test_csv_row_plain_name():
    assert to_csv_row({"name": "pen", "price": "2.5", "qty": 4}) == "pen,2.50,4"

### Assistant
I found several issues in the source code based on the docstrings and the test suite:

1. In `pricing.py`:
   - `parse_price` does not handle commas in the price string (e.g., "$1,299.50").
   - `parse_price` does not handle accounting style negative prices with parentheses (e.g., "(12.00)").
   - `apply_discount` does not use the "round half up" rule for rounding.

2. In `report.py`:
   - `low_stock` includes items with quantity equal to the threshold, but the docstring says strictly below the threshold.
   - `low_stock` does not sort the names alphabetically ignoring case.

3. In `export.py`:
   - `to_csv_row` does not handle names containing commas or double quotes as specified by RFC 4180.

I will fix these issues accordingly.

### Tool call: edit_file
{"file_path": "/workspace/inventory/pricing.py", "old_string": "cleaned = text.strip().replace(\"$\", \"\")\n    return Decimal(cleaned)", "new_string": "cleaned = text.strip().replace(\"$\", \"\").replace(\",\", \"\")\n    if cleaned.startswith(\"(\") and cleaned.endswith(\")\"):\n        cleaned = \"-\" + cleaned[1:-1]\n    return Decimal(cleaned)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/pricing.py'

### Tool call: edit_file
{"file_path": "/workspace/inventory/pricing.py", "old_string": "discounted = price * (100 - percent) / 100\n    return discounted.quantize(Decimal(\"0.01\"))", "new_string": "from decimal import ROUND_HALF_UP\n\n    discounted = price * (100 - percent) / 100\n    return discounted.quantize(Decimal(\"0.01\"), rounding=ROUND_HALF_UP)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/pricing.py'

### Tool call: edit_file
{"file_path": "/workspace/inventory/report.py", "old_string": "def low_stock(items, threshold=5):\n    \"\"\"Names of the items whose quantity is strictly below `threshold`.\n\n    The names are sorted alphabetically, ignoring case.\n    \"\"\"\n    return [item[\"name\"] for item in items if item[\"qty\"] <= threshold]", "new_string": "def low_stock(items, threshold=5):\n    \"\"\"Names of the items whose quantity is strictly below `threshold`.\n\n    The names are sorted alphabetically, ignoring case.\n    \"\"\"\n    names = [item[\"name\"] for item in items if item[\"qty\"] < threshold]\n    return sorted(names, key=str.lower)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/report.py'

### Tool call: edit_file
{"file_path": "/workspace/inventory/export.py", "old_string": "def to_csv_row(item):\n    \"\"\"Format one item as a CSV row: name,price,qty (price with 2 decimals).\n\n    A name that contains a comma or a double quote is wrapped in double quotes,\n    and every double quote inside it is doubled (RFC 4180).\n    \"\"\"\n    price = parse_price(item[\"price\"])\n    return f'{item[\"name\"]},{price:.2f},{item[\"qty\"]}'", "new_string": "def to_csv_row(item):\n    \"\"\"Format one item as a CSV row: name,price,qty (price with 2 decimals).\n\n    A name that contains a comma or a double quote is wrapped in double quotes,\n    and every double quote inside it is doubled (RFC 4180).\n    \"\"\"\n    price = parse_price(item[\"price\"])\n    name = item[\"name\"]\n    if \",\" in name or '\"' in name:\n        name = '\"' + name.replace('\"', '\"\"') + '\"'\n    return f'{name},{price:.2f},{item[\"qty\"]}'"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/export.py'

### Tool call: execute
{"command": "pytest --maxfail=1 --disable-warnings -q workspace/tests"}

### Tool result

==================================== ERRORS ====================================
_______________ ERROR collecting workspace/tests/test_report.py ________________
ImportError while importing test module '/private/var/folders/ww/l87bm4cd6737fdy39s19zm040000gn/T/lab-code-learn-n1dpnqu5/workspace/tests/test_report.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
~/.local/share/uv/python/cpython-3.11.16-macos-aarch64-none/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
~/K4-DAY20-MULTIAGENTS-NguyKhacPhiLong-2A202602532/tasks/code-learn/workspace/tests/test_report.py:3: in <module>
    from inventory.export import to_csv_row
E   ModuleNotFoundError: No module named 'inventory'
=========================== short test summary info ============================
ERROR workspace/tests/test_report.py
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.06s

Exit code: 2
[Command failed with exit code 2]

### Tool call: edit_file
{"file_path": "/workspace/tests/test_report.py", "old_string": "from inventory.export import to_csv_row\nfrom inventory.pricing import apply_discount\nfrom inventory.report import low_stock, total_value", "new_string": "from inventory.export import to_csv_row\nfrom inventory.pricing import apply_discount\nfrom inventory.report import low_stock, total_value"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/tests/test_report.py'

### Tool call: execute
{"command": "PYTHONPATH=workspace pytest --maxfail=1 --disable-warnings -q workspace/tests"}

### Tool result
......                                                                   [100%]
6 passed in 0.01s

[Command succeeded with exit code 0]

### Assistant
I fixed the following issues:

- In pricing.py, parse_price now removes commas and handles accounting style negative prices with parentheses.
- In pricing.py, apply_discount now rounds using the "round half up" rule.
- In report.py, low_stock now returns names strictly below the threshold and sorts them alphabetically ignoring case.
- In export.py, to_csv_row now wraps names containing commas or double quotes in double quotes and doubles internal double quotes per RFC 4180.

After these fixes, all tests pass successfully.