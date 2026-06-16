---
name: ota-dependency
description: "Judge whether the hotel is over-dependent on OTA distribution and recommend a shift to direct. Use when the GM asks 'are we too dependent on OTA?', about channel cost, commission leakage, or direct-vs-OTA balance. Calls get_segment_mix and reads the OTA share_of_revenue."
---

# OTA dependency (judgment)

**Tool:** `get_segment_mix(stay_month="YYYY-MM")`, read the `OTA` segment's
`share_of_revenue` and `share_of_room_nights`.

OTA volume is useful demand but it is **commissionable** (typically 15-25% of
revenue leaks to commission) and it weakens direct relationships and rate control.
The question is balance, not elimination.

## Judgment thresholds and actions
Read OTA `share_of_revenue` for the month:

- **Healthy (< 25%):** OTA is a supplementary channel. **Action:** maintain;
  no intervention.
- **Watch (25-35%):** dependency building. **Action:** strengthen the direct path -
  rate parity checks, a best-rate-guarantee/direct perk, loyalty enrolment at
  check-in, retargeting, and avoid widening OTA promotions.
- **Over-dependent (> 35%):** material margin and pricing-power risk. **Action:**
  actively **shift share to direct**: cap or close OTA promotions in high-demand
  periods, pull back OTA allotments, push metasearch direct, and run a direct
  campaign for the affected months.

Sharpen the read with two checks: compare OTA `share_of_revenue` against its
`share_of_room_nights` (revenue share well below room-night share means OTA is also
**rate-dilutive**, strengthening the case to shift); and look at whether OTA is the
segment carrying recent pickup (`pickup-pace`), growing dependency is more urgent
than a stable high base.

## What to say
Give the OTA revenue share, place it in the band above, name the margin/pricing-power
implication, and recommend the matching action with the months to target.
