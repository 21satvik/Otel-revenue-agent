---
name: otb-summary
description: "Report revenue on the books for a stay month. Use when the GM asks what revenue/rooms are on the books, how a month is shaping up, or for a monthly OTB headline. Calls get_otb_summary and reports reservations, room nights, room revenue and total revenue at the correct grain."
---

# On-the-books summary

**Tool:** `get_otb_summary(stay_month="YYYY-MM", exclude_cancelled=True)`

Use this for "what's on the books for July?", "how is Q3 looking?", or any monthly
revenue/volume headline. The month always filters on **`stay_date`** (revenue on
stay), never `property_date`.

## How to read the result
- `total_revenue` is the headline ("revenue on the books"); `room_revenue` is room
  only. Use `total_revenue` unless the GM specifically asks for room revenue.
- Report **reservations** (`reservation_count`), **room nights** (`room_nights`)
  and revenue together, they tell different stories. Never quote `row_count` to
  the GM; it is an internal stay-row tally, not a booking count.
- The tool returns `adr` (achieved room ADR), `occupancy`, and `revpar` directly,
  use those fields rather than dividing by hand.

## What to say
Give the headline number, then one line of texture: how many distinct reservations
and room nights sit behind it, and the implied ADR. If the GM did not specify
cancellations, state that the figure is Posted, non-cancelled business and offer to
include provisional/tentative on request. Keep it to the numbers that matter, a
GM wants the shape of the month, not every field.
