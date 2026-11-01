# Gmail API scope and batch behavior

Read this reference when using Gmail API-backed tools and the query or mutation
depends on dates, aliases, conversations, or batching. Discover what the actual
connector exposes; these API details are not invented callable tool names.

- Calendar dates in Gmail API search queries are interpreted as midnight PST.
  For an exact interval in another timezone, derive the intended instants and
  use supported timestamp query values. Do not silently change a user's local
  date window to the worker's timezone.
- Gmail's web UI expands account aliases in ways the API does not. If sender
  identity includes aliases, include the authorized identities explicitly rather
  than assuming identical UI/API matches.
- The UI supports thread-wide matching; the API does not have identical search
  behavior. Read message IDs and thread context before deciding which messages
  meet the condition. A displayed thread is not permission to modify every member.
- Snapshot the bounded target IDs before applying changes that remove items from
  the query. Respect newly arrived messages and exclusions instead of continually
  expanding the mutation set while paginating.
- The API's message batch-modify operation accepts at most 1,000 IDs; a connector
  may impose a smaller limit. It changes labels on the listed messages and returns
  an empty successful body. Reread relevant state to establish the actual result;
  an empty response is not a record-by-record verification.
- Archive removes inbox membership. Removing an inbox label and deleting a
  message are different operations; use the operation matching the request.

Checked 2026-11-01 against [search and filter differences](https://developers.google.com/workspace/gmail/api/guides/filtering),
[message batch modification](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/batchModify),
and [Gmail label semantics](https://developers.google.com/workspace/gmail/api/guides/labels).
The instructions above are independently authored summaries, not copied API text.
