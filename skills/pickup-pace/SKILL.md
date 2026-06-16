---
name: pickup-pace
description: "Judge booking pace and recent pickup for future stays, and recommend pricing/distribution action. Use when the GM asks what changed in the last 7/14/30 days, whether pace is ahead or behind, or how recently business booked. Calls get_pickup_delta on the create_datetime booking window."
---

# Pickup & pace (judgment)

**Tool:** `get_pickup_delta(booking_window_days=N, future_stay_from="YYYY-MM-DD")`

The booking window is defined on **`create_datetime`** (when reservations were
made), not stay date, this measures *new* business, not existing OTB. Use it for
"what booked in the last 7 days?", "are we pacing ahead?", or pickup by segment.

**Reading the result, do not misinterpret the window.** `booking_window_start_utc`
and `booking_window_end_utc` are the **booking** bounds (the trailing N days ending
roughly *now*), they are when reservations were *created*, never stay dates, and
never in the future. For an in-progress month the window simply ends today; that is
correct, not a data error. The figures are valid output from a tested tool, report
them, don't second-guess them as "future" or "unusable". `future_stay_from` is the
only stay-date filter (it bounds which stays count, e.g. today onward).

## Judgment thresholds and actions
Pace is best read as recent pickup relative to the room nights still to sell. As a
working rule for a trailing 7-day window against the next 30-90 days of stays:

- **Strong pace:** 7-day pickup ≥ **3%** of remaining room nights for the period →
  demand is firm. **Action:** hold or **raise BAR**, tighten/close the lowest
  discounted rate plans and OTA promotions, protect availability for higher-rated
  segments.
- **Soft pace:** 7-day pickup **< 1%** of remaining room nights, or pickup
  **down > 20%** versus the prior comparable window → demand is stalling.
  **Action:** stimulate, open a tactical promotion, extend OTA visibility,
  lengthen booking windows, and review restrictions (min-stay, closeouts).
- **On track:** between those bounds → no rate change; keep watching.

Always segment the pickup: if a single segment (e.g. OTA) is carrying the gain,
treat it as a distribution signal and cross-check with the `ota-dependency` skill.

## What to say
State whether pace is ahead, on track, or behind, quantify the pickup (reservations,
room nights, revenue) and which segments drove it, then give one concrete pricing or
distribution recommendation tied to the thresholds above.
