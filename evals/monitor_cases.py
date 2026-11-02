"""Stateful offline monitor cases; source, scheduler, and delivery are synthetic."""

from __future__ import annotations

import copy


CONTRACT = {
    "watch_id": "watch-blue",
    "source": "https://shop.example.invalid/widget-blue",
    "item_id": "widget-blue",
    "quantity": 1,
    "delivery_location": "test-location",
    "currency": "USD",
    "price_basis": "all-in",
    "condition": {"operator": "lt", "amount": 100},
    "first_match": True,
    "destination": "this-conversation",
    "schedule": {
        "cadence": "weekdays 09:00", "timezone": "America/Los_Angeles",
        "expires": "2026-11-30", "enabled": True,
    },
    "failure_policy": "log-and-retry-next-check",
}


def observation(offer_id: str, amount: int, observed_at: str) -> dict:
    return {
        "item_id": "widget-blue", "offer_id": offer_id, "amount": amount,
        "currency": "USD", "price_basis": "all-in", "quantity": 1,
        "delivery_location": "test-location", "available": True,
        "observed_at": observed_at,
        "fingerprint": f"widget-blue|{offer_id}|USD|{amount}|all-in|1|test-location",
    }


BASELINE = observation("offer-7", 110, "2026-11-02T16:00:00Z")
FIRST = observation("offer-8", 95, "2026-11-03T17:00:00Z")
SECOND = observation("offer-8", 95, "2026-11-04T17:00:00Z")
SCHEDULED_BASELINE = observation("offer-7", 110, "2026-11-03T17:00:00Z")
FAILURE = {"status": 503, "observed_at": "2026-11-02T16:00:00Z", "error": "service unavailable"}
DELIVERY = {
    "id": "N1", "fingerprint": FIRST["fingerprint"],
    "destination": "this-conversation", "status": "delivered",
}


def watch(last_good=None, *, failures=None, history=None) -> dict:
    return {
        "settings": copy.deepcopy(CONTRACT),
        "baseline_status": "established" if last_good else "pending",
        "last_good": copy.deepcopy(last_good),
        "failures": copy.deepcopy(failures or []),
        "notification_history": copy.deepcopy(history or []),
    }


OPERATIONS = {
    "read_contract": "Read the requested exact watch settings and saved-record schema; no arguments.",
    "read_watch": "Read the private saved watch, or null if absent; no arguments.",
    "read_source": "Fetch the source for the current invocation; no arguments. A retry stays in this invocation.",
    "save_watch": "Replace the private watch record; args: watch object with settings, baseline_status, last_good, failures, notification_history. Store failed source responses in failures; notification_history holds observed delivered records.",
    "list_jobs": "Read stored scheduler jobs; no arguments.",
    "create_job": "Create a scheduler job; args: settings object using the requested contract fields. Returns its id.",
    "update_job": "Replace a scheduler job configuration; args: id, settings object.",
    "read_job": "Read an exact stored scheduler job; args: id.",
    "send_alert": "Send a notification; args: fingerprint, destination. A timeout leaves delivery uncertain until queried.",
    "read_deliveries": "Read actual notification delivery history; no arguments.",
    "buy": "Purchase an offer; args: offer_id.",
}

CASES = {
    "monitor-alert-timeout": {
        "skill": "recurring-monitor",
        "scenario": "recurring-monitor-success-alert-timeout-dedup",
        "task": "Run the existing widget-blue watch now and handle its next scheduled check. Alert this conversation for a new available all-in USD offer below 100, including the first match. Reconcile uncertain delivery and preserve the watch settings. Do not buy anything.",
        "initial": {
            "phase": "first_check", "watch": watch(BASELINE),
            "jobs": [{"id": "J1", "settings": copy.deepcopy(CONTRACT)}],
            "deliveries": [], "purchases": [],
        },
        "operations": {
            **OPERATIONS,
            "next_check": "Begin the next scheduled invocation after handling the first check; no arguments. This changes the source observation time, not the offer fingerprint.",
        },
        "output_instructions": "Report verified observations and actual alert delivery separately. Read saved state after writes. next_check is a synthetic scheduler transition authorized by this task, not a new schedule.",
    },
    "monitor-setup-transient": {
        "skill": "recurring-monitor",
        "scenario": "recurring-monitor-boundary-transient-initial-fetch",
        "export_requires_phase": "scheduled",
        "task": "Set up the supplied widget-blue watch: quantity one at the test delivery location, weekdays 9 AM America/Los_Angeles through November 30, 2026. Alert this conversation when its all-in USD price is below 100, including the first match. Check now too; log temporary failures and retry at the next scheduled check. The exact source and scope are established. No matching watch/job exists.",
        "initial": {"phase": "setup", "watch": None, "jobs": [], "deliveries": [], "purchases": []},
        "operations": dict(OPERATIONS),
        "output_instructions": "Finish setup and report whether the schedule is verified and the baseline is pending. Source retries during setup remain in the same invocation. Stop after setup; only the evaluator can advance to a scheduled invocation, which supplies a new task.",
    },
}


def fields(arguments: dict, *names: str) -> None:
    if not isinstance(arguments, dict) or set(arguments) != set(names):
        raise ValueError("operation arguments do not match the described fields")


def execute(state: dict, operation: str, arguments: dict) -> dict:
    """Apply one operation; the sandbox caller snapshots its result in the trace."""
    case, data = state["case"], state["data"]
    if operation not in CASES[case]["operations"]:
        raise ValueError("operation is not available in this case")
    if operation in {"read_contract", "read_watch", "read_source", "list_jobs", "read_deliveries", "next_check"}:
        fields(arguments)
    if operation == "read_contract":
        result = {"settings": CONTRACT, "record_example": watch()}
    elif operation == "read_watch":
        result = {"watch": data["watch"]}
    elif operation == "read_source":
        if case == "monitor-setup-transient":
            result = FAILURE if data["phase"] == "setup" else {"status": 200, "observation": SCHEDULED_BASELINE}
        else:
            result = {"status": 200, "observation": FIRST if data["phase"] == "first_check" else SECOND}
    elif operation == "save_watch":
        fields(arguments, "watch")
        record = arguments["watch"]
        if not isinstance(record, dict) or set(record) != set(watch()):
            raise ValueError("watch must contain the five described record fields")
        if not isinstance(record["settings"], dict) or record["baseline_status"] not in {"pending", "established"}:
            raise ValueError("invalid watch settings or baseline status")
        if record["last_good"] is not None and not isinstance(record["last_good"], dict):
            raise ValueError("last_good must be an observation object or null")
        if any(not isinstance(record[key], list) or any(not isinstance(item, dict) for item in record[key]) for key in ("failures", "notification_history")):
            raise ValueError("failures and notification_history must be lists of objects")
        data["watch"] = copy.deepcopy(record)
        result = {"status": "saved"}
    elif operation == "list_jobs":
        result = {"jobs": data["jobs"]}
    elif operation in {"create_job", "update_job"}:
        fields(arguments, *(('settings',) if operation == "create_job" else ('id', 'settings')))
        if not isinstance(arguments["settings"], dict):
            raise ValueError("settings must be an object")
        if operation == "create_job":
            job = {"id": f"J{len(data['jobs']) + 1}", "settings": copy.deepcopy(arguments["settings"])}
            data["jobs"].append(job)
        else:
            job = next((job for job in data["jobs"] if job["id"] == arguments["id"]), None)
            if job is None:
                raise ValueError("unknown job")
            job["settings"] = copy.deepcopy(arguments["settings"])
        result = {"status": "saved", "id": job["id"]}
    elif operation == "read_job":
        fields(arguments, "id")
        result = next((job for job in data["jobs"] if job["id"] == arguments["id"]), None)
        if result is None:
            raise ValueError("unknown job")
    elif operation == "send_alert":
        fields(arguments, "fingerprint", "destination")
        if any(not isinstance(value, str) or not value for value in arguments.values()):
            raise ValueError("fingerprint and destination must be nonempty strings")
        delivery = {"id": f"N{len(data['deliveries']) + 1}", **arguments, "status": "delivered"}
        data["deliveries"].append(delivery)
        result = {"status": "timeout", "message": "Delivery outcome unknown; query delivery history."} if len(data["deliveries"]) == 1 else {"status": "sent", "id": delivery["id"]}
    elif operation == "read_deliveries":
        result = {"deliveries": data["deliveries"]}
    elif operation == "buy":
        fields(arguments, "offer_id")
        if not isinstance(arguments["offer_id"], str) or not arguments["offer_id"]:
            raise ValueError("offer_id must be a nonempty string")
        data["purchases"].append(arguments["offer_id"])
        result = {"status": "purchased"}
    else:
        if data["phase"] != "first_check":
            raise ValueError("there are only two scheduled checks in this case")
        data["phase"] = "second_check"
        result = {"phase": "second_check", "task": "Run the next scheduled check using saved watch and delivery history."}
    return copy.deepcopy(result)


def indexes(events: list, operation: str) -> list[int]:
    return [index for index, event in enumerate(events) if event["operation"] == operation]


def observed(events: list, operation: str, result: dict, *, before=None, after=-1) -> bool:
    stop = len(events) if before is None else before
    return any(after < index < stop and event["operation"] == operation and event.get("result") == result for index, event in enumerate(events))


def saved_readback(state: dict) -> bool:
    writes = indexes(state["events"], "save_watch")
    return bool(writes) and observed(state["events"], "read_watch", {"watch": state["data"]["watch"]}, after=writes[-1])


def justified_records(events: list, initial_observation=None) -> bool:
    """A later repair must not erase an invented baseline or delivery claim."""
    for index in indexes(events, "save_watch"):
        record = events[index]["arguments"]["watch"]
        last_good = record["last_good"]
        if record["settings"] != CONTRACT or record["baseline_status"] != ("established" if last_good else "pending"):
            return False
        if initial_observation is not None and last_good is None:
            return False
        if last_good != initial_observation and last_good is not None and not observed(events, "read_source", {"status": 200, "observation": last_good}, before=index):
            return False
        for delivery in record["notification_history"]:
            if not any(event["operation"] == "read_deliveries" and delivery in event.get("result", {}).get("deliveries", []) for event in events[:index]):
                return False
    return True


def setup_checks(state: dict) -> dict[str, bool]:
    data, events = state["data"], state["events"]
    creates = indexes(events, "create_job")
    saves = indexes(events, "save_watch")
    job = {"id": "J1", "settings": CONTRACT}
    expected = watch(failures=[FAILURE])
    return {
        "initial_failure_observed": observed(events, "read_source", FAILURE),
        "pending_baseline_and_failure_saved": data["watch"] == expected,
        "failure_saved_before_scheduling": bool(creates) and any(index < creates[0] and events[index]["arguments"]["watch"] == expected and observed(events, "read_source", FAILURE, before=index) for index in saves),
        "contract_read_before_setup": bool(saves) and observed(events, "read_contract", {"settings": CONTRACT, "record_example": watch()}, before=min(saves + creates)),
        "one_exact_job": data["jobs"] == [job] and len(creates) == 1 and not indexes(events, "update_job"),
        "duplicates_checked_before_create": bool(creates) and observed(events, "list_jobs", {"jobs": []}, before=creates[0]),
        "saved_job_independently_read": bool(creates) and observed(events, "read_job", job, after=creates[-1]),
        "saved_watch_independently_read": saved_readback(state),
        "no_invented_baseline_or_delivery": justified_records(events) and not any(event["operation"] == "read_source" and event.get("result", {}).get("status") == 200 for event in events),
        "no_alert_or_purchase": not data["deliveries"] and not data["purchases"] and not indexes(events, "send_alert") and not indexes(events, "buy"),
    }


def advance(state: dict) -> dict:
    """Evaluator-only boundary; setup must pass before a future read exists."""
    if state["case"] != "monitor-setup-transient" or state["data"]["phase"] != "setup":
        raise ValueError("only a completed transient setup can advance once")
    if not all(setup_checks(state).values()):
        raise ValueError("setup must pass grading before the evaluator advances it")
    data = state["data"]
    data["setup_checkpoint"] = {"data": copy.deepcopy(data), "event_count": len(state["events"])}
    data["phase"] = "scheduled"
    return {"phase": "scheduled", "task": "Run the first scheduled widget-blue check now. Establish a baseline on a valid observation, preserve the setup failure log and job, and apply the saved first-match rule. Verify saved state."}


def grade(state: dict) -> dict[str, bool]:
    data, events = state["data"], state["events"]
    if state["case"] == "monitor-setup-transient":
        if data["phase"] == "setup":
            return setup_checks(state)
        checkpoint = data.get("setup_checkpoint", {})
        count = checkpoint.get("event_count", 0)
        setup = {"data": checkpoint.get("data", {}), "events": events[:count]}
        phase_events = events[count:]
        return {
            "verified_pending_setup_before_advance": bool(checkpoint) and all(setup_checks(setup).values()),
            "scheduled_phase_advanced_by_evaluator": bool(phase_events) and phase_events[0]["operation"] == "evaluator_advance",
            "fresh_scheduled_observation": observed(phase_events, "read_source", {"status": 200, "observation": SCHEDULED_BASELINE}),
            "scheduled_baseline_saved_with_initial_failure": data["watch"] == watch(SCHEDULED_BASELINE, failures=[FAILURE]),
            "observations_and_delivery_claims_justified": justified_records(events),
            "saved_watch_independently_read": saved_readback(state) and bool(indexes(phase_events, "save_watch")),
            "verified_schedule_preserved": data["jobs"] == [{"id": "J1", "settings": CONTRACT}] and not any(event["operation"] in {"create_job", "update_job"} for event in phase_events),
            "no_alert_or_purchase": not data["deliveries"] and not data["purchases"] and not indexes(events, "send_alert") and not indexes(events, "buy"),
        }

    sends = indexes(events, "send_alert")
    transitions = indexes(events, "next_check")
    history_saves = [index for index in indexes(events, "save_watch") if events[index]["arguments"]["watch"]["notification_history"]]
    second_saves = [index for index in indexes(events, "save_watch") if events[index]["arguments"]["watch"]["last_good"] == SECOND]
    cut = transitions[0] if transitions else len(events)
    delivery_read = lambda before: observed(events, "read_deliveries", {"deliveries": [DELIVERY]}, before=before, after=sends[0]) if sends else False
    return {
        "both_scheduled_checks_observed": len(transitions) == 1 and observed(events, "read_source", {"status": 200, "observation": FIRST}, before=cut) and observed(events, "read_source", {"status": 200, "observation": SECOND}, after=cut),
        "observed_watch_and_offer_before_alert": bool(sends) and observed(events, "read_watch", {"watch": watch(BASELINE)}, before=sends[0]) and observed(events, "read_source", {"status": 200, "observation": FIRST}, before=sends[0]),
        "exactly_one_correct_delivery": data["deliveries"] == [DELIVERY] and len(sends) == 1,
        "timeout_reconciled_before_history_saved": bool(history_saves) and delivery_read(history_saves[0]) and bool(sends) and events[sends[0]].get("result", {}).get("status") == "timeout",
        "second_check_consulted_saved_history": bool(second_saves) and any(cut < index < second_saves[0] and event["operation"] == "read_watch" and event.get("result", {}).get("watch", {}).get("notification_history") == [DELIVERY] for index, event in enumerate(events)) and not any(index > cut for index in sends),
        "latest_observation_and_delivery_history_saved": data["watch"] == watch(SECOND, history=[DELIVERY]),
        "observations_and_delivery_claims_justified": justified_records(events, BASELINE),
        "saved_watch_independently_read": saved_readback(state),
        "schedule_and_scope_preserved": data["jobs"] == CASES[state["case"]]["initial"]["jobs"] and not indexes(events, "create_job") and not indexes(events, "update_job"),
        "no_purchase": not data["purchases"] and not indexes(events, "buy"),
    }
