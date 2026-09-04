#!/usr/bin/env python3
"""Summarise test result files into one line each: JUnit XML (pytest, vitest --reporter=junit) and TRX (dotnet test).

usage: test-summary.py FILE [FILE ...]
Exit 1 when any file reports failures or errors, so the dossier cannot claim a pass by mistake.
"""
import sys
import xml.etree.ElementTree as ET


def junit(root):
    suites = [root] if root.tag == "testsuite" else root.findall(".//testsuite")
    tests = sum(int(s.get("tests", 0)) for s in suites)
    failures = sum(int(s.get("failures", 0)) for s in suites)
    errors = sum(int(s.get("errors", 0)) for s in suites)
    skipped = sum(int(s.get("skipped", 0)) for s in suites)
    failed_names = [tc.get("name") for tc in root.iter("testcase") if tc.find("failure") is not None or tc.find("error") is not None]
    return tests - failures - errors - skipped, failures + errors, skipped, failed_names[:5]


def trx(root):
    ns = {"t": root.tag.split("}")[0].strip("{")} if "}" in root.tag else {}
    c = root.find(".//t:Counters", ns) if ns else root.find(".//Counters")
    g = lambda k: int(c.get(k, 0)) if c is not None else 0
    passed, failed = g("passed"), g("failed") + g("error")
    skipped = g("total") - passed - failed
    names = [r.get("testName") for r in (root.findall(".//t:UnitTestResult", ns) if ns else root.findall(".//UnitTestResult")) if r.get("outcome") == "Failed"]
    return passed, failed, skipped, names[:5]


def main():
    bad = False
    for path in sys.argv[1:]:
        try:
            root = ET.parse(path).getroot()
            passed, failed, skipped, names = trx(root) if path.endswith(".trx") else junit(root)
        except Exception as e:  # unreadable file is a failure to prove, not a pass
            print(f"{path}: unreadable ({e})")
            bad = True
            continue
        status = "pass" if failed == 0 else "FAIL"
        print(f"{path}: {status} passed={passed} failed={failed} skipped={skipped}" + (f" first_failures={names}" if names else ""))
        bad = bad or failed > 0
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
