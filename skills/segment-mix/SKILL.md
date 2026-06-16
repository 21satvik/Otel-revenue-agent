---
name: segment-mix
description: "Explain the segment / market mix for a stay month and what is driving it. Use when the GM asks which segments drive a month, the share of corporate/leisure/retail/MICE, or how the mix is shifting. Calls get_segment_mix using stay-date-effective macro groups."
---

# Segment mix

**Tool:** `get_segment_mix(stay_month="YYYY-MM", macro_group=None)`

Use for "which segments are driving July?", "what share is corporate?", or any mix
question. Pass `macro_group` (e.g. `"Retail"`, `"Corporate"`, `"MICE"`,
`"Leisure"`, `"Leisure Group"`) to drill into one group.

## How to read the result
- Each segment carries `share_of_revenue` and `share_of_room_nights` against a
  single filtered denominator, so shares sum to 1.0 within scope.
- Revenue share and room-night share diverge when a segment runs above/below
  property ADR (each segment carries its own `adr`). Call that out: a segment with
  30% of revenue but 20% of room nights is a **high-rate** segment; the reverse is
  **rate-dilutive volume**.
- Macro groups are **stay-date-effective**, a market code reclassified mid-year
  (e.g. PROM) reports its correct group per month. Do not describe a segment by a
  stale classification.

## What to say
Name the two or three segments that drive the month by revenue, give their shares,
and contrast revenue share vs room-night share to show whether each is rate- or
volume-led. If one segment dominates, foreshadow concentration risk and suggest
loading `ota-dependency` or `block-concentration` for the deeper read.
