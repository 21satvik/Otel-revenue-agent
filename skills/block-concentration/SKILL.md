---
name: block-concentration
description: "Judge group/block vs transient balance and revenue concentration in a few large accounts, and recommend diversification or attrition management. Use when the GM asks how much group business there is, whether revenue is concentrated in a few bookings/companies, or about block risk. Calls get_block_vs_transient_mix and reads block_share_of_revenue and top-3 company concentration."
---

# Block / group concentration (judgment)

**Tool:** `get_block_vs_transient_mix(stay_month="YYYY-MM")`, read
`block_share_of_revenue`, `block_share_of_room_nights`, `top_companies` and
`top3_company_revenue_share`.

Group/block business gives base and certainty, but heavy reliance on a few accounts
is **concentration risk**: one cancellation or non-renewal moves the month, and
displaced transient (usually higher-rated) is hard to recover late.

## Judgment thresholds and actions
Read two dimensions for the month:

- **Block share of revenue**
  - **< 40%:** healthy base. **Action:** none.
  - **40-60%:** group-heavy. **Action:** protect transient space, review block
    cut-off dates, enforce attrition/wash clauses, and watch displacement on peak
    nights.
  - **> 60%:** over-reliant on group. **Action:** **diversify**, limit further
    block acceptance on already-grouped dates, requalify weak blocks, and grow
    transient/direct demand for those months.
- **Top-3 account concentration** (`top3_company_revenue_share`)
  - **> 50%** of month revenue in three companies → single-account exposure.
    **Action:** secure those accounts (early renewal, deposits, firm attrition
    terms) **and** broaden the account base so the month does not hinge on one
    booking.

Cross-check the returned `block_adr` vs `transient_adr`: if block runs well below
transient ADR, flag rate-dilutive group business and recommend tightening group
pricing/floors.

## What to say
State block vs transient shares, name the top accounts and their combined share,
place both in the bands above, and give a concrete diversification or
attrition-management recommendation.
