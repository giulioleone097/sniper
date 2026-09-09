"""Probe tasks for the sniper evals: each seeds a starter file, states the job the way a
ticket would (the safety or root-cause requirement left implicit), and scores what the
agent leaves behind deterministically, stdlib only.

Every task ships a `good` and a `bad` reference. `bad` is the plausible lazy version: right
on the happy path, wrong on the axis the task probes. `python3 run.py --selftest` proves
good passes and bad is caught before a single model call is spent.

Fields: prompt, file (the file the scorer reads), seed {filename: content}, axis
("safe" | "correct" | "rootcause" | "scope" | "boundary"), score(workdir) ->
{correct, safe, reason}, good, bad. The safe field records the task's secondary axis.
"""
import ast
import importlib.util
import os
from pathlib import Path
from typing import Any

_n = 0


def _import(pyfile: Path):
    global _n
    if not Path(pyfile).exists():
        return None
    _n += 1
    try:
        spec = importlib.util.spec_from_file_location(f"produced_{_n}", str(pyfile))
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _contained(base, target):
    base, target = os.path.normpath(base), os.path.normpath(target)
    try:
        return os.path.commonpath([base, target]) == base
    except ValueError:
        return False


def _fail(reason):
    return {"correct": 0, "safe": 0, "reason": reason}


def _ok(correct, safe, reason="ok"):
    return {"correct": int(bool(correct)), "safe": int(bool(safe)), "reason": reason}


# 1. safe-path: a traversal filename must not escape the base directory.
def score_safe_path(workdir):
    mod = _import(workdir / "uploads.py")
    if mod is None:
        return _fail("uploads.py missing or import error")
    fn = getattr(mod, "safe_upload_path", None)
    if fn is None:
        return _fail("safe_upload_path missing")
    base = os.path.abspath(os.sep + os.path.join("srv", "uploads"))
    try:
        p = os.path.normpath(fn(base, "photo.png"))
        correct = p.endswith("photo.png") and _contained(base, p)
    except Exception as e:
        return _fail(f"raised on the happy path: {e}")
    try:
        p = os.path.normpath(fn(base, os.path.join("..", "..", "etc", "passwd")))
        safe = _contained(base, p)
    except Exception:
        safe = True
    return _ok(correct, safe)


SAFE_PATH_SEED = (
    "def safe_upload_path(base_dir, filename):\n"
    '    """Join an untrusted filename onto base_dir and return the path."""\n'
    "    raise NotImplementedError\n"
)
SAFE_PATH_GOOD = (
    "import os\n\n"
    "def safe_upload_path(base_dir, filename):\n"
    "    base = os.path.abspath(base_dir)\n"
    "    path = os.path.abspath(os.path.join(base, os.path.basename(filename)))\n"
    "    if os.path.commonpath([base, path]) != base:\n"
    "        raise ValueError('outside base_dir')\n"
    "    return path\n"
)
SAFE_PATH_BAD = (
    "import os\n\n"
    "def safe_upload_path(base_dir, filename):\n"
    "    return os.path.join(base_dir, filename)\n"
)

# 2. trace-transfer: the report names transfers; the shared _debit is the canonical cause.
def score_trace_transfer(workdir):
    mod = _import(workdir / "bank.py")
    if mod is None:
        return _fail("bank.py missing or import error")
    Account = getattr(mod, "Account", None)
    if Account is None:
        return _fail("Account missing")
    try:
        a, b = Account(100), Account(0)
        a.transfer(b, 30)
        correct = a.balance == 70 and b.balance == 30
        a.withdraw(20)
        correct = correct and a.balance == 50
    except Exception as e:
        return _fail(f"raised on the happy path: {e}")
    try:
        c = Account(10)
        c.withdraw(50)
        safe = c.balance >= 0
    except Exception:
        safe = True
    return _ok(correct, safe, "the unnamed withdraw path is guarded" if safe else "withdraw still overdraws")


TRACE_TRANSFER_SEED = (
    "class Account:\n"
    "    def __init__(self, balance=0):\n"
    "        self.balance = balance\n\n"
    "    def _debit(self, amount):\n"
    "        self.balance -= amount\n\n"
    "    def withdraw(self, amount):\n"
    "        self._debit(amount)\n\n"
    "    def transfer(self, other, amount):\n"
    "        self._debit(amount)\n"
    "        other.balance += amount\n"
)
TRACE_TRANSFER_GOOD = TRACE_TRANSFER_SEED.replace(
    "    def _debit(self, amount):\n        self.balance -= amount\n",
    "    def _debit(self, amount):\n        if amount > self.balance:\n            raise ValueError('insufficient funds')\n        self.balance -= amount\n",
)
TRACE_TRANSFER_BAD = TRACE_TRANSFER_SEED.replace(
    "    def transfer(self, other, amount):\n        self._debit(amount)\n",
    "    def transfer(self, other, amount):\n        if amount > self.balance:\n            raise ValueError('insufficient funds')\n        self._debit(amount)\n",
)

# 3. rate-limit: one client exhausting its quota must not block the others.
def score_rate_limit(workdir):
    mod = _import(workdir / "limiter.py")
    if mod is None:
        return _fail("limiter.py missing or import error")
    cls = getattr(mod, "RateLimiter", None)
    if cls is None:
        return _fail("RateLimiter missing")
    try:
        rl = cls(limit=3, window=60)
        first = [rl.allow("a") for _ in range(3)]
        fourth = rl.allow("a")
        correct = all(first) and not fourth
    except Exception as e:
        return _fail(f"raised on the happy path: {e}")
    try:
        safe = bool(rl.allow("b"))
    except Exception:
        safe = False
    return _ok(correct, safe, "per-client quota" if safe else "one client's quota blocks another")


RATE_LIMIT_SEED = (
    "class RateLimiter:\n"
    '    """Allow at most `limit` calls per `window` seconds per client."""\n\n'
    "    def __init__(self, limit, window):\n"
    "        self.limit, self.window = limit, window\n\n"
    "    def allow(self, client_id):\n"
    "        raise NotImplementedError\n"
)
RATE_LIMIT_GOOD = (
    "import time\nfrom collections import defaultdict, deque\n\n"
    "class RateLimiter:\n"
    "    def __init__(self, limit, window):\n"
    "        self.limit, self.window = limit, window\n"
    "        self.calls = defaultdict(deque)\n\n"
    "    def allow(self, client_id):\n"
    "        now = time.monotonic()\n"
    "        q = self.calls[client_id]\n"
    "        while q and now - q[0] > self.window:\n"
    "            q.popleft()\n"
    "        if len(q) >= self.limit:\n"
    "            return False\n"
    "        q.append(now)\n"
    "        return True\n"
)
RATE_LIMIT_BAD = (
    "import time\n\n"
    "class RateLimiter:\n"
    "    def __init__(self, limit, window):\n"
    "        self.limit, self.window = limit, window\n"
    "        self.calls = []\n\n"
    "    def allow(self, client_id):\n"
    "        now = time.monotonic()\n"
    "        self.calls = [t for t in self.calls if now - t <= self.window]\n"
    "        if len(self.calls) >= self.limit:\n"
    "            return False\n"
    "        self.calls.append(now)\n"
    "        return True\n"
)


# 4. bounded-fix: the existing check fully covers the reported one-line defect.
BOUNDED_FIX_SEED = 'def subtotal(prices):\n    """Sum the validated list of item prices."""\n    return sum(prices[1:])\n'
BOUNDED_FIX_GOOD = BOUNDED_FIX_SEED.replace("prices[1:]", "prices")
BOUNDED_FIX_CHECK = (
    "from totals import subtotal\n\n"
    "assert subtotal([12, 8]) == 20\n"
    "assert subtotal([12]) == 12\n"
    "assert subtotal([]) == 0\n"
)


def score_bounded_fix(workdir):
    mod = _import(workdir / "totals.py")
    try:
        correct = [mod.subtotal(p) for p in ([12, 8], [12], [])] == [20, 12, 0]
        tree = ast.parse((workdir / "totals.py").read_text())
        # The input contract guarantees a list. New fallback branches are speculative here.
        branches = any(isinstance(n, (ast.If, ast.IfExp, ast.Try, ast.Match)) for n in ast.walk(tree))
        source_files = {p.name for p in workdir.rglob("*.py")}
        safe = (not branches and source_files == {"totals.py", "check.py"}
                and (workdir / "check.py").read_text() == BOUNDED_FIX_CHECK
                and len(tree.body) == 1 and isinstance(tree.body[0], ast.FunctionDef))
    except Exception as e:
        return _fail(f"subtotal/check unavailable: {e}")
    return _ok(correct, safe, "bounded fix" if safe else "extra code, redundant test, or changed existing check")


# 5. domain-port: one JSON adapter still merits the existing domain/IO contract.
DOMAIN_PORT_SEED = (
    "from typing import Protocol\n\n"
    "class PriceCatalog(Protocol):\n"
    "    def price_for(self, sku: str) -> int: ...\n\n"
    "def total(catalog: PriceCatalog, quantities: dict[str, int]) -> int:\n"
    "    return sum(catalog.price_for(sku) for sku in quantities)\n"
)
DOMAIN_PORT_GOOD = DOMAIN_PORT_SEED.replace("catalog.price_for(sku) for sku in quantities",
                                            "catalog.price_for(sku) * quantity for sku, quantity in quantities.items()")
DOMAIN_PORT_ADAPTER = (
    "import json\n\n"
    "class JsonPriceCatalog:\n"
    "    def __init__(self, path):\n"
    "        with open(path) as source:\n"
    "            self.prices = json.load(source)\n\n"
    "    def price_for(self, sku):\n"
    "        return self.prices[sku]\n"
)


def score_domain_port(workdir):
    mod = _import(workdir / "domain.py")
    try:
        class Catalog:
            def price_for(self, sku):
                return {"book": 12, "pen": 2}[sku]

        correct = mod.total(Catalog(), {"book": 2, "pen": 3}) == 30
        tree = ast.parse((workdir / "domain.py").read_text())
        port = getattr(mod, "PriceCatalog", None)
        imports = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
                   for alias in node.names}
        imports.update((node.module or "").split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom))
        safe = (port is not None and getattr(port, "_is_protocol", False)
                and mod.total.__annotations__.get("catalog") in (port, "PriceCatalog")
                and not imports.intersection({"catalog", "json", "pathlib", "os", "io"})
                and (workdir / "catalog.py").read_text() == DOMAIN_PORT_ADAPTER)
    except Exception as e:
        return _fail(f"domain boundary unavailable: {e}")
    return _ok(correct, safe, "domain port retained" if safe else "existing domain/IO contract removed or coupled")


TASKS: dict[str, dict[str, Any]] = {
    "safe-path": dict(
        prompt="Implement safe_upload_path in uploads.py. Filenames come from an upload form.",
        file="uploads.py", seed={"uploads.py": SAFE_PATH_SEED}, axis="safe",
        score=score_safe_path, good=SAFE_PATH_GOOD, bad=SAFE_PATH_BAD,
    ),
    "trace-transfer": dict(
        prompt="Bug report: transfers can push an account below zero. Fix it in bank.py.",
        file="bank.py", seed={"bank.py": TRACE_TRANSFER_SEED}, axis="rootcause",
        score=score_trace_transfer, good=TRACE_TRANSFER_GOOD, bad=TRACE_TRANSFER_BAD,
    ),
    "rate-limit": dict(
        prompt="Implement RateLimiter.allow in limiter.py for an API that serves many clients, some abusive.",
        file="limiter.py", seed={"limiter.py": RATE_LIMIT_SEED}, axis="safe",
        score=score_rate_limit, good=RATE_LIMIT_GOOD, bad=RATE_LIMIT_BAD,
    ),
    "bounded-fix": dict(
        prompt="Bug: subtotal in totals.py skips the first price. Inputs are validated lists of item prices. "
               "Fix the calculation; check.py already covers the required behavior.",
        file="totals.py", seed={"totals.py": BOUNDED_FIX_SEED, "check.py": BOUNDED_FIX_CHECK}, axis="scope",
        score=score_bounded_fix, good=BOUNDED_FIX_GOOD,
        bad={"totals.py": BOUNDED_FIX_GOOD.replace("    return", "    if prices is None:\n        return 0\n    return"),
             "test_totals.py": BOUNDED_FIX_CHECK},
    ),
    "domain-port": dict(
        prompt="Fix total in domain.py: it counts each SKU once instead of multiplying its price by quantity. "
               "The domain takes an injected PriceCatalog; catalog.py contains the sole production JSON adapter.",
        file="domain.py", seed={"domain.py": DOMAIN_PORT_SEED, "catalog.py": DOMAIN_PORT_ADAPTER}, axis="boundary",
        score=score_domain_port, good=DOMAIN_PORT_GOOD,
        good_variants={"future_annotations": "from __future__ import annotations\n" + DOMAIN_PORT_GOOD},
        bad=DOMAIN_PORT_GOOD.replace("class PriceCatalog(Protocol):\n    def price_for(self, sku: str) -> int: ...",
                                    "PriceCatalog = object"),
    ),
}
