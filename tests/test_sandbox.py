"""Check the offline fixture CLI's observable saved-state and grading behavior."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "evals" / "sandbox.py"


class SandboxTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name) / "case"

    def cli(self, command, *extra, code=0):
        result = subprocess.run([sys.executable, str(SCRIPT), command, *map(str, extra)], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout or result.stderr)

    def init(self, case):
        return self.cli("init", case, self.workspace)

    def call(self, operation, **arguments):
        return self.cli("call", self.workspace, operation, "--args", json.dumps(arguments))

    def test_existing_workspace_is_not_reset(self):
        self.init("form-autosave")
        self.call("prepare_draft", value="River")
        before = (self.workspace / "state.json").read_bytes()
        self.cli("init", "form-autosave", self.workspace, code=2)
        self.assertEqual((self.workspace / "state.json").read_bytes(), before)

    def test_autosave_requires_local_draft(self):
        self.init("form-autosave")
        self.assertTrue(self.call("read_form")["autosave_on_input"])
        self.call("prepare_draft", value="River")
        self.assertTrue(self.cli("grade", self.workspace)["passed"])
        self.call("type_display_name", value="River")
        self.assertFalse(self.cli("grade", self.workspace, code=1)["checks"]["live_profile_unchanged"])

    def test_message_level_write_preserves_starred_thread_neighbor(self):
        self.init("gmail-message")
        self.assertEqual(self.call("search")["conversation_ids"], ["T1"])
        self.assertEqual(len(self.call("read_thread", id="T1")["messages"]), 2)
        self.call("label_message", id="M1", label="Follow-up")
        self.call("read_message", id="M1")
        self.call("read_message", id="M2")
        self.assertTrue(self.cli("grade", self.workspace)["passed"])
        self.call("label_thread", id="T1", label="Follow-up")
        self.assertFalse(self.cli("grade", self.workspace, code=1)["checks"]["starred_message_preserved"])

    def test_timed_out_append_saved_once_and_requires_readback(self):
        self.init("sheets-append-timeout")
        self.assertEqual(self.call("append", item_id="P-3", quantity=4)["status"], "timeout")
        self.assertFalse(self.cli("grade", self.workspace, code=1)["checks"]["saved_rows_independently_read"])
        self.call("read_rows", item_id="P-1")
        self.assertFalse(self.cli("grade", self.workspace, code=1)["checks"]["saved_rows_independently_read"])
        self.assertEqual(len(self.call("read_rows", item_id="P-3")["rows"]), 1)
        self.assertTrue(self.cli("grade", self.workspace)["passed"])
        self.call("append", item_id="P-3", quantity=4)
        failed = self.cli("grade", self.workspace, code=1)["checks"]
        self.assertFalse(failed["exactly_one_requested_row"])
        self.assertFalse(failed["saved_rows_independently_read"])

    def test_saved_draft_is_not_a_send_and_timeout_can_be_reconciled(self):
        self.init("gmail-draft-timeout")
        sender = self.call("read_thread", id="T1")["from"]
        self.assertEqual(self.call("create_draft", thread="T1", to=sender, body="Thanks, I can attend on Tuesday.")["status"], "timeout")
        self.assertEqual(self.call("read_drafts", thread="UNRELATED")["drafts"], [])
        self.assertFalse(self.cli("grade", self.workspace, code=1)["checks"]["saved_draft_independently_read"])
        self.assertEqual(len(self.call("read_drafts", thread="T1")["drafts"]), 1)
        self.assertTrue(self.cli("grade", self.workspace)["passed"])

    def test_invalid_operation_has_no_side_effect(self):
        self.init("form-autosave")
        before = (self.workspace / "state.json").read_bytes()
        self.cli("call", self.workspace, "unknown", code=2)
        self.assertEqual((self.workspace / "state.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
