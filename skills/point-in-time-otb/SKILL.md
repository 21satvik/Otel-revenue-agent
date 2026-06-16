---
name: point-in-time-otb
description: "Reconstruct on-the-books as it stood at a past instant, for pace-versus-prior and 'where were we as of' questions. Use when the GM asks where the book stood on a given date, or wants a like-for-like comparison versus a prior point. Calls get_as_of_otb, which is human-approval gated."
---

# Point-in-time OTB

**Tool:** `get_as_of_otb(stay_month="YYYY-MM", as_of_utc="YYYY-MM-DDThh:mm:ssZ")`

Use when the GM asks "where were we as of 1 May?" or wants pace versus a prior
instant (e.g. same-time-last-month). The tool rebuilds the book at `as_of_utc`:
it includes only reservations created on or before that instant and excludes any
cancelled on or before it, Posted-only.

## Human-in-the-loop (important)
`get_as_of_otb` is **gated behind an automatic approval interrupt** in the agent
runtime: the moment you call it, execution pauses and the GM is shown an approval
prompt before the expensive rebuild runs. That interrupt **is** the human-in-the-loop.
So **call `get_as_of_otb` directly** with the requested instant, do **not** ask the
GM to confirm the timestamp in conversation first; that would bypass the gate the
brief requires. Use the `as_of_utc` the GM gave, or the obvious instant their
question implies (e.g. midnight UTC of the named date), and let the approval
interrupt handle confirmation. Only ask a clarifying question if the intended date
is genuinely ambiguous (no date stated at all).

## How to read the result
Compare the as-of figures to current OTB (`get_otb_summary`) to express pace: the
delta is net bookings (minus cancellations) since `as_of_utc`. Always state the
exact instant you reconstructed to, in UTC, so the GM can see what was rebuilt.

## What to say
Report the book as of the instant, then the change to today (reservations, room
nights, revenue) as the pace story, noting the timestamp you used.
