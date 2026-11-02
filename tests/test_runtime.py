"""Public CLI regression checks using isolated synthetic state."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI = Path(__file__).resolve().parents[1] / "scripts" / "run_workflow.py"


class RuntimeCLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "state.sqlite"

    def run_cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(CLI), "--db", str(self.db), *args], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0 if ok else 2, result.stderr)
        return json.loads(result.stdout) if ok else result.stderr

    def add(self, name="one", *args):
        return self.run_cli("add", name, "--payload", "synthetic value", "--due", "20", *args)

    def test_unreadable_job_does_not_starve_later_pending_job(self):
        self.add("a", "--mode", "unreadable")
        self.add("b")
        for _ in range(4):
            state = self.run_cli("tick", "--now", "20", "--limit", "1")
        statuses = {task["id"]: task["status"] for task in state["tasks"]}
        self.assertEqual(statuses, {"a": "uncertain", "b": "verified"})
        self.assertEqual(sum(e["kind"] == "intent" and e["task"] == "a" for e in state["events"]), 1)

    def test_due_and_approval_gate(self):
        self.add("later")
        self.add("held", "--approval-required")
        before = self.run_cli("tick", "--now", "19")
        self.assertEqual(before["effects"], [])
        due = self.run_cli("tick", "--now", "20")
        self.assertEqual(len(due["effects"]), 1)
        self.assertEqual({t["id"]: t["status"] for t in due["tasks"]}["held"], "approval-required")
        self.run_cli("approve", "held")
        after = self.run_cli("tick", "--now", "20")
        self.assertEqual(len(after["effects"]), 2)

    def test_new_arrivals_do_not_starve_uncertain_reconciliation(self):
        self.add("old", "--mode", "unreadable")
        self.run_cli("tick", "--now", "20", "--limit", "1")
        for index in range(5):
            self.add(f"new-{index}")
            state = self.run_cli("tick", "--now", "20", "--limit", "1")
        events = state["events"]
        self.assertTrue(any(e["task"] == "old" and e["kind"] == "reconciliation-unavailable" for e in events))
        self.assertTrue(any(t["id"].startswith("new-") and t["status"] == "verified" for t in state["tasks"]))
        self.assertEqual(sum(e["task"] == "old" and e["kind"] == "intent" for e in events), 1)

    def test_restart_reconciles_without_duplicate_and_outbox_deduplicates(self):
        self.add("one", "--mode", "timeout-after-write")
        uncertain = self.run_cli("tick", "--now", "20")
        self.assertEqual(uncertain["tasks"][0]["status"], "uncertain")
        self.assertEqual(len(uncertain["effects"]), 1)
        recovered = self.run_cli("tick", "--now", "20")
        self.assertEqual(recovered["tasks"][0]["status"], "verified")
        repeated = self.run_cli("tick", "--now", "20")
        self.assertEqual(len(repeated["effects"]), 1)
        self.assertEqual(len(repeated["notifications"]), 1)
        self.assertEqual([e["kind"] for e in repeated["events"]].count("intent"), 1)
        acked = self.run_cli("ack", repeated["notifications"][0]["id"])
        self.assertEqual(acked["notifications"][0]["acknowledged"], 1)

    def test_confirmed_absence_precedes_retry(self):
        self.add("one", "--mode", "timeout-before-write")
        self.run_cli("tick", "--now", "20")
        reconciled = self.run_cli("tick", "--now", "20")
        self.assertEqual(reconciled["effects"], [])
        self.assertEqual(reconciled["tasks"][0]["status"], "pending")
        complete = self.run_cli("tick", "--now", "20")
        self.assertEqual(complete["tasks"][0]["status"], "verified")
        kinds = [e["kind"] for e in complete["events"]]
        self.assertLess(kinds.index("confirmed-absent"), len(kinds) - 1 - kinds[::-1].index("intent"))

    def test_unavailable_reconciliation_never_retries(self):
        self.add("one", "--mode", "unreadable")
        for _ in range(3):
            state = self.run_cli("tick", "--now", "20")
        self.assertEqual(state["tasks"][0]["status"], "uncertain")
        self.assertEqual(len(state["effects"]), 1)
        self.assertEqual([e["kind"] for e in state["events"]].count("intent"), 1)

    def test_bounded_jobs_and_unknown_adapter(self):
        self.add("a")
        self.add("b")
        state = self.run_cli("tick", "--now", "20", "--limit", "1")
        self.assertEqual(len(state["effects"]), 1)
        self.run_cli("tick", "--limit", "0", ok=False)
        self.run_cli("add", "remote", "--payload", "x", "--due", "0", "--adapter", "remote", ok=False)
        state = self.run_cli("show")
        self.assertEqual(len(state["tasks"]), 2)

    def test_process_lock_prevents_second_writer(self):
        import fcntl
        with open(str(self.db) + ".lock", "a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertIn("another runner", self.run_cli("tick", ok=False))


if __name__ == "__main__":
    unittest.main()
