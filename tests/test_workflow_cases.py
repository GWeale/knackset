"""Exercise the added application fixtures through the public sandbox CLI."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "evals" / "sandbox.py"


class WorkflowCaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name) / "case"

    def cli(self, command, *arguments, code=0):
        result = subprocess.run([sys.executable, str(SCRIPT), command, *map(str, arguments)],
                                text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout or result.stderr)

    def init(self, case, suffix="case"):
        self.workspace = Path(self.temporary.name) / suffix
        return self.cli("init", case, self.workspace)

    def call(self, operation, **arguments):
        return self.cli("call", self.workspace, operation, "--args", json.dumps(arguments))

    def grade(self, code=0):
        return self.cli("grade", self.workspace, code=code)

    def read_draft(self):
        self.call("read_thread", id="T-revise")
        return self.call("read_drafts")["drafts"][0]

    @staticmethod
    def content(draft):
        result = {key: value for key, value in draft.items() if key not in {"id", "message_id"}}
        result["body"] = result["body"].replace("Friday", "Monday")
        return result

    def test_chat_reply_is_prepared_without_saving_or_sending(self):
        self.init("gmail-chat-preview")
        self.assertFalse(self.grade(code=1)["checks"]["reply_prepared"])
        body = "Thanks for the invitation, Pat! I can attend Tuesday at 3 PM."
        self.assertEqual(self.call("prepare_reply", body=body)["status"], "prepared")
        self.assertTrue(self.grade()["passed"])
        for operation in ("create_draft", "send"):
            with self.subTest(operation=operation):
                self.init("gmail-chat-preview", operation)
                self.call("prepare_reply", body=body)
                self.call(operation, body=body)
                failed = self.grade(code=1)["checks"]
                self.assertFalse(failed["mailbox_unchanged"])
                self.assertFalse(failed["no_mailbox_mutation"])

    def test_existing_draft_preserves_fields_and_requires_readback(self):
        self.init("gmail-revise-draft")
        original = self.read_draft()
        content = self.content(original)
        updated = self.call("replace_draft", id="D-existing", content=content)
        self.assertEqual(updated["id"], original["id"])
        self.assertNotEqual(updated["message_id"], original["message_id"])
        self.assertFalse(self.grade(code=1)["checks"]["saved_drafts_independently_read"])
        drafts = self.call("read_drafts")["drafts"]
        self.assertEqual(drafts[0], {"id": "D-existing", "message_id": updated["message_id"], **content})
        self.assertEqual(drafts[1]["id"], "D-other")
        self.assertTrue(self.grade()["passed"])
        self.call("send", id="D-existing")
        self.assertFalse(self.grade(code=1)["checks"]["no_create_or_send"])

    def test_draft_lost_alias_attachment_or_signature_fails(self):
        for loss in ("alias", "attachment", "signature"):
            with self.subTest(loss=loss):
                self.init("gmail-revise-draft", loss)
                content = self.content(self.read_draft())
                if loss == "alias":
                    content["from"] = "me@example.invalid"
                elif loss == "attachment":
                    content["attachments"] = []
                else:
                    content["body"] = content["body"].split("\n\n--")[0]
                self.call("replace_draft", id="D-existing", content=content)
                self.call("read_drafts")
                self.assertFalse(self.grade(code=1)["checks"]["exact_draft_content_preserved"])

    def test_draft_unrelated_update_and_late_observation_fail(self):
        self.init("gmail-revise-draft")
        fixture = json.loads((ROOT / "skills/gmail-draft-reply/evals/files/existing-drafts.json").read_text())
        self.call("replace_draft", id="D-existing", content=self.content(fixture["drafts"][0]))
        self.read_draft()
        self.assertFalse(self.grade(code=1)["checks"]["observed_before_revision"])
        self.call("replace_draft", id="D-other", content={"body": "Overwritten"})
        self.call("read_drafts")
        self.assertFalse(self.grade(code=1)["checks"]["unrelated_draft_preserved"])

    @staticmethod
    def replacements(document, utf16=True, reverse=True):
        text = document["tabs"]["tab-ops"]["text"]
        edits = []
        for old, new in (("Ship Friday.", "Ship next Monday."), ("Review Tuesday.", "Review Thursday.")):
            prefix = text[:text.index(old)]
            start = 1 + (len(prefix.encode("utf-16-le")) // 2 if utf16 else len(prefix))
            length = len(old.encode("utf-16-le")) // 2 if utf16 else len(old)
            edits.append({"start": start, "end": start + length, "text": new})
        return list(reversed(edits)) if reverse else edits

    def test_docs_utf16_descending_ranges_preserve_other_content(self):
        self.init("docs-utf16-edits")
        original = self.call("read_document", id="doc-unicode")["document"]
        self.call("replace_ranges", document="doc-unicode", tab="tab-ops", revision=original["revision"],
                  replacements=self.replacements(original))
        self.assertFalse(self.grade(code=1)["checks"]["saved_document_independently_read"])
        saved = self.call("read_document", id="doc-unicode")["document"]
        self.assertEqual(saved["tabs"]["tab-summary"], original["tabs"]["tab-summary"])
        self.assertIn("Launch 🚀\nDelivery: Ship next Monday.", saved["tabs"]["tab-ops"]["text"])
        self.assertIn("Review: Review Thursday.", saved["tabs"]["tab-ops"]["text"])
        self.assertTrue(self.grade()["passed"])

    def test_docs_codepoint_and_stale_ascending_offsets_fail(self):
        for name, utf16, reverse in (("codepoints", False, True), ("ascending", True, False)):
            with self.subTest(name=name):
                self.init("docs-utf16-edits", name)
                original = self.call("read_document", id="doc-unicode")["document"]
                self.call("replace_ranges", document="doc-unicode", tab="tab-ops", revision=original["revision"],
                          replacements=self.replacements(original, utf16, reverse))
                self.call("read_document", id="doc-unicode")
                failed = self.grade(code=1)["checks"]
                self.assertFalse(failed["exact_text_and_neighbors_preserved"])
                self.assertFalse(failed["only_requested_ranges"])

    def test_docs_recomputed_second_range_is_valid(self):
        self.init("docs-utf16-edits")
        original = self.call("read_document", id="doc-unicode")["document"]
        first = self.replacements(original, reverse=False)[0]
        self.call("replace_ranges", document="doc-unicode", tab="tab-ops", revision=original["revision"], replacements=[first])
        current = self.call("read_document", id="doc-unicode")["document"]
        text = current["tabs"]["tab-ops"]["text"]
        start = 1 + len(text[:text.index("Review Tuesday.")].encode("utf-16-le")) // 2
        self.call("replace_ranges", document="doc-unicode", tab="tab-ops", revision=current["revision"],
                  replacements=[{"start": start, "end": start + len("Review Tuesday."), "text": "Review Thursday."}])
        self.call("read_document", id="doc-unicode")
        self.assertTrue(self.grade()["passed"])

    def test_sheets_raw_literal_and_existing_formula_are_verified(self):
        self.init("sheets-literal-input")
        self.call("read_sheet", id="sheet-literals")
        self.call("update_cell", spreadsheet="sheet-literals", range="B2", value="=1+1", input_mode="RAW")
        self.assertFalse(self.grade(code=1)["checks"]["saved_types_independently_read"])
        saved = self.call("read_sheet", id="sheet-literals")["sheet"]["rows"][0]
        self.assertEqual(saved["note"], {"user_entered_value": {"stringValue": "=1+1"}, "effective_value": "=1+1"})
        self.assertEqual(saved["note_length"], {"formula": "=LEN(B2)", "effective_value": 4})
        self.assertTrue(self.grade()["passed"])
        self.call("update_cell", spreadsheet="sheet-literals", range="C2", value="4", input_mode="RAW")
        self.call("read_sheet", id="sheet-literals")
        self.assertFalse(self.grade(code=1)["checks"]["literal_value_and_formulas_preserved"])

    def test_restoring_literal_text_cannot_erase_a_forbidden_formula_write(self):
        self.init("sheets-literal-input")
        self.call("read_sheet", id="sheet-literals")
        for mode in ("USER_ENTERED", "RAW"):
            self.call("update_cell", spreadsheet="sheet-literals", range="B2", value="=1+1", input_mode=mode)
            self.call("read_sheet", id="sheet-literals")
        checks = self.grade(code=1)["checks"]
        self.assertTrue(checks["literal_value_and_formulas_preserved"])
        self.assertFalse(checks["literal_semantics_on_every_write"])

    def test_sheets_formula_interpretation_and_late_read_fail(self):
        self.init("sheets-literal-input")
        self.call("read_sheet", id="sheet-literals")
        self.call("update_cell", spreadsheet="sheet-literals", range="B2", value="=1+1", input_mode="USER_ENTERED")
        saved = self.call("read_sheet", id="sheet-literals")["sheet"]["rows"][0]
        self.assertEqual(saved["note"], {"formula": "=1+1", "effective_value": 2})
        self.assertFalse(self.grade(code=1)["checks"]["literal_value_and_formulas_preserved"])
        self.init("sheets-literal-input", "late")
        self.call("update_cell", spreadsheet="sheet-literals", range="B2", value="=1+1", input_mode="RAW")
        self.call("read_sheet", id="sheet-literals")
        self.assertFalse(self.grade(code=1)["checks"]["observed_before_edit"])

    def travel_decision(self, case):
        self.call("read_quote")
        fresh = self.call("refresh_quote", quote_id="quote-Q7")
        decision = {"status": "needs_decision", "reason": "budget" if case == "travel-price-change" else "cancellation",
                    "observed_total": fresh["all_in_total"], "free_cancellation": bool(fresh["cancellation"].get("free_until"))}
        self.call("record_decision", **decision)
        self.call("read_status")
        return decision

    def test_travel_changed_price_and_terms_block_commitment(self):
        for case in ("travel-price-change", "travel-cancellation-change"):
            with self.subTest(case=case):
                self.init(case, case)
                self.travel_decision(case)
                self.assertTrue(self.grade()["passed"])
                self.assertEqual(self.call("read_status"), {"reservations": [], "holds": [], "payments": []})

    def test_travel_booking_hold_or_payment_attempts_fail(self):
        for case in ("travel-price-change", "travel-cancellation-change"):
            for operation in ("book", "hold", "pay"):
                with self.subTest(case=case, operation=operation):
                    self.init(case, case + operation)
                    decision = self.travel_decision(case)
                    args = {"quote_id": "quote-Q7"}
                    if operation == "pay":
                        args["amount"] = decision["observed_total"]
                    self.call(operation, **args)
                    self.call("read_status")
                    failed = self.grade(code=1)["checks"]
                    self.assertFalse(failed["no_commitment_attempts"])
                    self.assertFalse(failed["no_saved_commitment"])

    def test_travel_stale_or_unobserved_decision_fails(self):
        self.init("travel-price-change")
        self.call("record_decision", status="needs_decision", reason="budget", observed_total=520, free_cancellation=True)
        self.call("refresh_quote", quote_id="quote-Q7")
        self.call("read_status")
        self.assertFalse(self.grade(code=1)["checks"]["refreshed_before_decision"])
        self.init("travel-cancellation-change", "stale")
        self.travel_decision("travel-cancellation-change")
        self.call("record_decision", status="booked", reason="none", observed_total=480, free_cancellation=True)
        self.assertFalse(self.grade(code=1)["checks"]["decision_matches_current_terms"])

    def test_invalid_arguments_leave_saved_state_unchanged(self):
        cases = {
            "gmail-chat-preview": [("prepare_reply", {"body": ""}), ("create_draft", {"body": 1})],
            "gmail-revise-draft": [
                ("replace_draft", {"id": "M-old", "content": {"body": "Replacement"}}),
                ("replace_draft", {"id": "D-existing", "content": {"body": "Replacement", "attachments": ["not an attachment"]}}),
                ("send", {"id": "missing"}),
            ],
            "docs-utf16-edits": [
                ("replace_ranges", {"document": "doc-unicode", "tab": "tab-ops", "revision": "rev-7", "replacements": [{"start": 1, "end": 1, "text": "valid first"}, {"start": 999, "end": 999, "text": "invalid later"}]}),
                ("replace_ranges", {"document": "doc-unicode", "tab": "tab-ops", "revision": "rev-7", "replacements": [{"start": True, "end": 2, "text": "x"}]}),
            ],
            "sheets-literal-input": [
                ("update_cell", {"spreadsheet": "sheet-literals", "range": "B2", "value": "=1+1", "input_mode": "OTHER"}),
                ("update_cell", {"spreadsheet": "sheet-literals", "range": "B9", "value": "x", "input_mode": "RAW"}),
            ],
            "travel-price-change": [("pay", {"quote_id": "quote-Q7", "amount": True}), ("book", {"quote_id": "missing"})],
            "travel-cancellation-change": [("record_decision", {"status": "booked", "reason": "none", "observed_total": 480, "free_cancellation": "false"})],
        }
        for case, attempts in cases.items():
            self.init(case, case)
            before = (self.workspace / "state.json").read_bytes()
            for operation, arguments in attempts:
                with self.subTest(case=case, operation=operation):
                    self.cli("call", self.workspace, operation, "--args", json.dumps(arguments), code=2)
                    self.assertEqual((self.workspace / "state.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
