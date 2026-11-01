---
name: calendar-coordination
description: Find meeting times or create, reschedule, and cancel scoped calendar events while preserving recurrence and invitations. Use for calendar coordination, not a general daily briefing or inbox review.
license: MIT
---

# Coordinate calendar events

Use the host's available calendar integration or authorized browser. Resolve the
calendar, operation, participants, date window, duration, time zone, and recurrence
scope from the request and current event. Default to a short slot list for a
planning request; complete an explicitly requested event change when authorized.
Do not replace a requested update with a proposal merely because it is a write.

## Identify the event and constraints

Read the exact calendar and event, not just a matching title. Check organizer and
edit rights, current attendees, location/conference link, reminders, and status.
For availability, inspect only the relevant calendars and time window. Free/busy
access supports conflict checking without exposing private event descriptions.

Use named time zones for local-time schedules across daylight-saving changes.
Distinguish timed events from date-only all-day events. In the Google Calendar
API, `end.date` is exclusive. In a browser or another integration, follow the
displayed control or documented field semantics. Before saving a multi-day event,
read the current date-field labels and help or the integration's documentation;
do not infer whether the last day is included from a tool argument's name. Preserve
duration unless the request changes it. Clarify a repeated wall-clock time when its offset is
ambiguous and the intended instant matters.

For a recurring event, distinguish one occurrence, the series, and this-and-future
occurrences. In Google Calendar, `recurringEventId` identifies the series while
`originalStartTime` identifies an occurrence even after it moves. Target the
instance for a single-occurrence edit. Do not create many exceptions to simulate
a series change; use the host's supported series operation.

## Change and verify

Apply only the requested fields. Preserve conference data and unmentioned guests;
an API array replacement can otherwise remove attendees. Consider invitation and
cancellation notifications as effects of the operation. Honor the user's requested
notification scope and host controls; if the available tool cannot express a
material constraint, explain that limitation before performing an incompatible edit.

Use fresh event state and a supported concurrency guard when available. After
creating or changing an event, independently reopen/query its saved identity and
check date, time zone, duration, participants, and recurrence scope. For a moved
instance, check a neighboring occurrence to establish the series was preserved.
After cancellation, verify the relevant event/instance status rather than treating
its absence from one filtered view as sufficient proof.

If a write times out, look up the intended event or occurrence before retrying.
Do not create a second invite because confirmation was lost. Stop an unreconciled
write and report uncertainty; report missing rights without copying the event to
another calendar as a workaround. Return the event link, saved change or proposed
slots, notification effects, and any remaining conflict.

Primary references checked 2026-11-01:
[recurring events](https://developers.google.com/workspace/calendar/api/guides/recurringevents),
[event fields and update semantics](https://developers.google.com/workspace/calendar/api/v3/reference/events),
[event notifications](https://developers.google.com/workspace/calendar/api/v3/reference/events/update).
