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

    def test_blind_message_write_and_noop_thread_write_are_rejected(self):
        self.init("gmail-message")
        self.call("label_message", id="M1", label="Follow-up")
        self.call("read_message", id="M1")
        self.call("read_message", id="M2")
        self.assertFalse(self.cli("grade", self.workspace, code=1)["checks"]["target_observed_before_labels"])
        self.workspace = Path(self.temporary.name) / "thread-noop"
        self.init("gmail-message")
        self.call("read_thread", id="T1")
        self.call("label_message", id="M1", label="Follow-up")
        self.call("label_thread", id="T1", label="INBOX")
        self.call("read_message", id="M1")
        self.call("read_message", id="M2")
        failed = self.cli("grade", self.workspace, code=1)["checks"]
        self.assertFalse(failed["no_thread_label_operations"])
        self.assertTrue(failed["matching_message_labeled"])
        self.assertTrue(failed["starred_message_preserved"])

    def test_message_observations_cover_target_and_follow_the_last_write(self):
        self.init("gmail-message")
        self.call("search")
        self.call("read_message", id="M2")
        self.call("label_message", id="M1", label="Follow-up")
        self.call("read_thread", id="T1")
        self.assertFalse(self.cli("grade", self.workspace, code=1)["checks"]["target_observed_before_labels"])
        self.workspace = Path(self.temporary.name) / "readback"
        self.init("gmail-message")
        self.call("read_message", id="M1")
        self.call("label_message", id="M1", label="Follow-up")
        self.call("read_thread", id="T1")
        self.assertTrue(self.cli("grade", self.workspace)["passed"])
        self.call("label_message", id="M1", label="Follow-up")
        self.assertFalse(self.cli("grade", self.workspace, code=1)["checks"]["message_labels_independently_read"])

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

    def test_sheet_grader_rejects_missing_literal_and_wrong_reference_formulas(self):
        self.init("sheets-append-timeout")
        self.call("append", item_id="P-3", quantity=4)
        self.call("read_rows", item_id="P-3")
        self.assertTrue(self.cli("grade", self.workspace)["passed"])
        path = self.workspace / "state.json"
        original = json.loads(path.read_text())
        for formula in (None, "40", "=B3*10"):
            with self.subTest(formula=formula):
                state = json.loads(json.dumps(original))
                row = state["data"]["rows"][-1]
                if formula is None:
                    del row["total_formula"]
                else:
                    row["total_formula"] = formula
                path.write_text(json.dumps(state))
                self.assertFalse(self.cli("grade", self.workspace, code=1)["checks"]["exactly_one_requested_row"])

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

    def test_list_identifies_each_executable_case_and_scenario(self):
        result = self.cli("list")
        expected = {
            "form-autosave": ("web-form-update", "form-draft-on-autosave"),
            "gmail-message": ("gmail-triage", "gmail-message-thread-label-boundary"),
            "sheets-append-timeout": ("google-sheets-update", "sheets-append-timeout-reconcile-state"),
            "gmail-draft-timeout": ("gmail-draft-reply", "gmail-draft-reply-boundary-draft-create-timeout"),
            "calendar-inclusive-dates": ("calendar-coordination", "calendar-coordination-boundary-all-day-browser-dates"),
            "docs-suggestions-unavailable": ("google-docs-update", "google-docs-update-boundary-suggestions-unavailable"),
            "gmail-chat-preview": ("gmail-draft-reply", "gmail-draft-reply-boundary-conversation-only"),
            "gmail-revise-draft": ("gmail-draft-reply", "gmail-draft-reply-success-revise-existing-draft"),
            "docs-utf16-edits": ("google-docs-update", "google-docs-update-success-utf16-multiple-ranges"),
            "sheets-literal-input": ("google-sheets-update", "sheets-success-literal-equals-value"),
            "travel-price-change": ("travel-reservation", "travel-reservation-boundary-refreshed-price-over-budget"),
            "travel-cancellation-change": ("travel-reservation", "travel-reservation-boundary-refreshed-cancellation-removed"),
            "monitor-alert-timeout": ("recurring-monitor", "recurring-monitor-success-alert-timeout-dedup"),
            "monitor-setup-transient": ("recurring-monitor", "recurring-monitor-boundary-transient-initial-fetch"),
        }
        self.assertEqual(len(result["cases"]), len(expected))
        self.assertEqual({case["case"]: (case["skill"], case["scenario"]) for case in result["cases"]}, expected)
        self.assertTrue(all(isinstance(case["task"], str) and case["task"] for case in result["cases"]))
        self.assertIn("offline", result["scope"].lower())

    def test_calendar_requires_saved_target_readback_and_rejects_duplicates(self):
        self.init("calendar-inclusive-dates")
        self.assertFalse(self.cli("grade", self.workspace, code=1)["passed"])
        original = self.call("read_event", id="E0")
        form = self.call("read_form")
        self.assertEqual(form["fields"]["last_day"], "Last day (inclusive)")
        event = {"title": "Team offsite", "start_date": "2026-11-10", "last_day": "2026-11-12", "all_day": True, "guests": []}
        self.assertEqual(self.call("save_event", **event), {"status": "saved", "id": "E1"})
        self.assertFalse(self.cli("grade", self.workspace, code=1)["checks"]["saved_event_independently_read"])
        self.assertIn({"id": "E1", "title": "Team offsite"}, self.call("list_events")["events"])
        self.assertEqual(self.call("read_event", id="E0"), original)
        self.assertFalse(self.cli("grade", self.workspace, code=1)["checks"]["saved_event_independently_read"])
        self.assertEqual(self.call("read_event", id="E1"), {"id": "E1", **event})
        self.assertTrue(self.cli("grade", self.workspace)["passed"])

        self.assertEqual(self.call("save_event", **event)["id"], "E2")
        failed = self.cli("grade", self.workspace, code=1)["checks"]
        self.assertFalse(failed["one_requested_event"])
        self.assertFalse(failed["saved_event_independently_read"])
        self.assertTrue(failed["existing_events_preserved"])
        self.assertEqual(self.call("read_event", id="E0"), original)

    def test_calendar_grades_actual_dates_and_prewrite_form_observation(self):
        cases = [
            ("exclusive_end_applied_to_inclusive_form", {"last_day": "2026-11-13"}, True, "one_requested_event"),
            ("timed_event", {"all_day": False}, True, "one_requested_event"),
            ("unrequested_guest", {"guests": ["guest@example.invalid"]}, True, "one_requested_event"),
            ("form_read_after_save", {}, False, "observed_form_before_save"),
        ]
        for name, changes, observe_first, check in cases:
            with self.subTest(name=name):
                self.workspace = Path(self.temporary.name) / name
                self.init("calendar-inclusive-dates")
                if observe_first:
                    self.call("read_form")
                event = {"title": "Team offsite", "start_date": "2026-11-10", "last_day": "2026-11-12", "all_day": True, "guests": []}
                event.update(changes)
                self.assertEqual(self.call("save_event", **event)["status"], "saved")
                if not observe_first:
                    self.call("read_form")
                self.assertEqual(self.call("read_event", id="E1"), {"id": "E1", **event})
                self.assertFalse(self.cli("grade", self.workspace, code=1)["checks"][check])

    def test_docs_proposal_preserves_document_and_allows_identical_local_copies(self):
        self.init("docs-suggestions-unavailable")
        self.assertFalse(self.cli("grade", self.workspace, code=1)["passed"])
        observed = self.call("read_document", id="doc-plan")
        self.assertEqual(observed["capabilities"], {"direct_edits": True, "suggestions": False, "comments": False})
        original = observed["document"]
        paragraph = {"text": "Ship on Friday", "bold": True, "link": "https://example.invalid/delivery"}
        for tab in ("tab-summary", "tab-ops"):
            self.assertEqual(original["tabs"][tab]["sections"]["Delivery"], paragraph)
        proposal = {"document": "doc-plan", "tab": "tab-ops", "section": "Delivery", "old_text": "Ship on Friday", "new_text": "Ship on Monday"}
        prepared = self.call("prepare_proposal", **proposal)
        self.assertEqual(prepared["status"], "prepared")
        self.assertFalse(prepared["saved_to_document"])
        self.assertEqual(prepared["proposal"], proposal)
        self.assertEqual(self.call("read_document", id="doc-plan")["document"], original)
        self.assertTrue(self.cli("grade", self.workspace)["passed"])
        self.call("prepare_proposal", **proposal)
        self.assertTrue(self.cli("grade", self.workspace)["passed"])
        self.assertEqual(self.call("read_document", id="doc-plan")["document"], original)

    def test_docs_proposal_requires_correct_target_and_prior_document_read(self):
        cases = [
            ("same_heading_wrong_tab", {"tab": "tab-summary"}, True, "correct_local_proposal"),
            ("wrong_replacement", {"new_text": "Ship on Tuesday"}, True, "correct_local_proposal"),
            ("document_read_after_proposal", {}, False, "observed_document_before_proposal"),
        ]
        for name, changes, observe_first, check in cases:
            with self.subTest(name=name):
                self.workspace = Path(self.temporary.name) / name
                self.init("docs-suggestions-unavailable")
                if observe_first:
                    self.call("read_document", id="doc-plan")
                proposal = {"document": "doc-plan", "tab": "tab-ops", "section": "Delivery", "old_text": "Ship on Friday", "new_text": "Ship on Monday"}
                proposal.update(changes)
                self.assertFalse(self.call("prepare_proposal", **proposal)["saved_to_document"])
                self.call("read_document", id="doc-plan")
                failed = self.cli("grade", self.workspace, code=1)["checks"]
                self.assertFalse(failed[check])
                self.assertTrue(failed["document_unchanged"])
                self.assertTrue(failed["no_direct_edits"])

    def test_docs_direct_edit_is_forbidden_even_when_text_is_restored(self):
        self.init("docs-suggestions-unavailable")
        original = self.call("read_document", id="doc-plan")["document"]
        target = {"document": "doc-plan", "tab": "tab-ops", "section": "Delivery"}
        self.call("replace_text", **target, old_text="Ship on Friday", new_text="Ship on Monday")
        changed = self.call("read_document", id="doc-plan")["document"]
        self.assertEqual(changed["tabs"]["tab-ops"]["sections"]["Delivery"]["text"], "Ship on Monday")
        self.assertEqual(changed["tabs"]["tab-summary"], original["tabs"]["tab-summary"])
        self.call("replace_text", **target, old_text="Ship on Monday", new_text="Ship on Friday")
        self.assertEqual(self.call("read_document", id="doc-plan")["document"]["tabs"], original["tabs"])
        self.call("prepare_proposal", **target, old_text="Ship on Friday", new_text="Ship on Monday")
        self.assertFalse(self.cli("grade", self.workspace, code=1)["checks"]["no_direct_edits"])

    def test_new_case_invalid_arguments_do_not_persist_any_mutation(self):
        event = {"title": "Team offsite", "start_date": "2026-11-10", "last_day": "2026-11-12", "all_day": True, "guests": []}
        proposal = {"document": "doc-plan", "tab": "tab-ops", "section": "Delivery", "old_text": "Ship on Friday", "new_text": "Ship on Monday"}
        cases = {
            "calendar-inclusive-dates": [
                ("read_form", {"unexpected": True}),
                ("read_event", {"id": "missing"}),
                ("save_event", []),
                ("save_event", {**event, "title": ""}),
                ("save_event", {**event, "start_date": "2026-02-30"}),
                ("save_event", {**event, "all_day": 1}),
                ("save_event", {**event, "guests": "guest@example.invalid"}),
                ("save_event", {**event, "guests": [1]}),
                ("save_event", {**event, "unexpected": True}),
            ],
            "docs-suggestions-unavailable": [
                ("read_document", {"id": "missing"}),
                ("prepare_proposal", []),
                ("prepare_proposal", {**proposal, "new_text": ""}),
                ("prepare_proposal", {**proposal, "tab": "missing"}),
                ("prepare_proposal", {**proposal, "old_text": "Not the original paragraph"}),
                ("replace_text", {**proposal, "document": "missing"}),
                ("replace_text", {**proposal, "section": "missing"}),
                ("replace_text", {**proposal, "new_text": 1}),
                ("replace_text", {**proposal, "unexpected": True}),
            ],
        }
        for case, attempts in cases.items():
            self.workspace = Path(self.temporary.name) / case
            self.init(case)
            before = (self.workspace / "state.json").read_bytes()
            for operation, arguments in attempts:
                with self.subTest(case=case, operation=operation, arguments=arguments):
                    self.cli("call", self.workspace, operation, "--args", json.dumps(arguments), code=2)
                    self.assertEqual((self.workspace / "state.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
