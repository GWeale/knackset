---
name: travel-reservation
description: Prepare or complete an explicitly requested travel booking, change, or cancellation while tracking exact travelers, total price, terms, payment, and reservation status. Use for reservation lifecycle work, not a generic shopping shortlist.
license: MIT
---

# Manage a travel reservation

Resolve travelers, destination, dates and local time zones, required itinerary or
room/fare class, accessibility constraints, budget/currency, cancellation terms,
and requested operation. Use only necessary traveler data through the host's secure
flows. Default to an itinerary with current quotations when no transaction is
requested; complete an explicitly authorized booking/change/cancellation rather
than stopping at a draft. Existing authorization and native host controls apply.

## Select the exact offer

Read current availability and pin the provider, traveler count, dates, room/fare,
connections, baggage or occupancy assumptions, and quote expiry. Compare the
all-in amount: base price, mandatory taxes/fees, extras, currency, amount due now,
and amounts due later. Include refundability, cancellation/change deadlines in
their local zone, penalties, and whether separate itinerary legs are protected.

A displayed quote is not a held inventory item. A hold has its own expiry and
may not include payment. A payment authorization is not necessarily a settled
charge. A reservation request is not confirmation. Preserve each provider status
independently rather than collapsing them into a generic success.

## Execute within the requested terms

Revalidate the chosen offer immediately before commitment. Present any unresolved
material choice or changed price/terms outside the user's authorized bounds; do
not silently add insurance, upgrades, donations, subscriptions, or guests. Use the
provider's available checkout and the host's credential/approval controls. This
skill cannot grant payment access or replace a required native confirmation.

For changes/cancellations, locate the existing booking and obtain the applicable
terms and resulting fee/refund before acting. Honor explicit authorized bounds;
do not cancel first to discover whether a replacement is available. Track each
booking independently when a trip has several providers or legs.

## Reconcile and verify

After a booking or payment timeout, query reservation and transaction status using
the original reference or documented lookup. A missing confirmation email alone
does not prove failure. Do not retry a charge or booking until its absence is
established or a supported idempotency mechanism makes the retry safe. Otherwise
report the unresolved status and the next check, including any hold expiry.

Independently read the saved reservation and payment/refund status. Verify provider
reference, travelers, dates/zones, exact offer, totals, terms, and the requested
change/cancellation. A cart or receipt does not establish every part of a trip.
Return a concise itinerary and status per leg, confirmation/reference links,
amount paid/due/refund pending, critical deadlines, and unresolved items. Keep
identity documents and payment data out of public artifacts.

Primary references checked 2026-11-01:
[Muse booking lifecycle and confirmation requirements](https://platform.muse.ai/docs),
[Grok secure computer and payment handoffs](https://docs.x.ai/grok-bot/computer-and-apps).

Package status and limits: [validation and provenance](VALIDATION.md).
