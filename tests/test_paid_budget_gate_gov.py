"""Regression tests for the fail-closed paid API admission gate."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
WF=ROOT/".github/workflows/private-ai-development.yml"

def script():
    src=WF.read_text()
    start=src.index("      - name: Require explicit paid budget and daily run cap")
    end=src.index("      - name: Require the private OpenAI API secret",start)
    assert end<src.index("uses: openai/codex-action@v1")
    block=src[start:end]
    run=block.split("        run: |\n",1)[1]
    return "\n".join(line[10:] if line.startswith("          ") else line
                      for line in run.splitlines())

class PaidBudgetGateTests(unittest.TestCase):
    def test_precedes_codex_and_has_explicit_limits(self):
        src=WF.read_text()
        for marker in ("SMARTSVG_MONTHLY_API_BUDGET_USD",
                       "SMARTSVG_MAX_PAID_RUNS_PER_DAY",
                       "GITHUB_RUN_ATTEMPT", "gh api",
                       "Provider-side billing cap is NOT verified"):
            self.assertIn(marker,src)
        self.assertIn("set -euo pipefail",script())
        self.assertIn("exit 1",script())

    def run_admission(self,budget="10",cap="4",total=2,attempt="1"):
        if not shutil.which("bash") or not shutil.which("jq"):
            self.skipTest("bash and jq required")
        with tempfile.TemporaryDirectory() as tmp:
            stub=Path(tmp)/"gh"
            stub.write_text("#!/bin/sh\nprintf '%s\\n' \"$SMARTSVG_TEST_JSON\"\n")
            stub.chmod(0o755)
            env=os.environ.copy()
            env.update(PATH=tmp+os.pathsep+env.get("PATH",""),
                       MONTHLY_API_BUDGET_USD=budget,
                       MAX_PAID_RUNS_PER_DAY=cap,
                       GITHUB_RUN_ATTEMPT=attempt,
                       SMARTSVG_TEST_JSON='{"total_count":'+str(total)+'}')
            return subprocess.run(["bash","-c",script()],env=env,
                                  text=True,capture_output=True,timeout=10)

    def test_success_requires_explicit_budget_and_remaining_runs(self):
        p=self.run_admission()
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("NOT verified",p.stdout)

    def test_budget_invalid_fail_closed(self):
        for x in ("","0","-2","10.999","100000","nan"):
            with self.subTest(x=x):
                self.assertNotEqual(self.run_admission(budget=x).returncode,0)

    def test_cap_and_retries_fail_closed(self):
        for x in ("","0","25","1.2","nan"):
            with self.subTest(x=x):
                self.assertNotEqual(self.run_admission(cap=x).returncode,0)
        for opts in (dict(attempt="2"),dict(total=5),dict(total=0),
                     dict(total=101,cap="24"),dict(total='"oops"')):
            with self.subTest(opts=opts):
                self.assertNotEqual(self.run_admission(**opts).returncode,0)

if __name__=="__main__":unittest.main()
