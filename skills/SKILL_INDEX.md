---
name: revenue-manager-pack
description: "Revenue Manager skill pack revenue-manager-v2. Index of the on-demand skills the agent loads to answer hotel GM questions about on-the-books revenue, segment mix, booking pace, OTA dependency, group/block concentration, cancellations, and point-in-time snapshots. Load the specific skill whose description matches the question; never query the database directly, always go through the five named tools."
---

# Revenue Manager skill pack, `revenue-manager-v2`

This pack teaches the agent to think like an experienced hotel revenue manager,
not to read a dashboard aloud. Each skill below is a separate `SKILL.md` loaded on
demand (progressive disclosure). Recognise which one applies, read it in full,
then call the tool it names.

| Skill | Use when the GM asks… | Primary tool(s) | Judgment? |
|-------|----------------------|-----------------|-----------|
| `otb-summary` | "What revenue is on the books for July?" | `get_otb_summary` | No |
| `segment-mix` | "Which segments are driving July?" | `get_segment_mix` | No |
| `pickup-pace` | "What changed in the last 7 days?" | `get_pickup_delta` | Yes |
| `ota-dependency` | "Are we too dependent on OTA?" | `get_segment_mix` | Yes |
| `block-concentration` | "Is our business concentrated in a few bookings?" | `get_block_vs_transient_mix` | Yes |
| `cancellation-risk` | "How much was cancelled? Is attrition a risk?" | `get_otb_summary` | Yes |
| `point-in-time-otb` | "Where were we as of 1 May?" / pace vs last year | `get_as_of_otb` | No |
| `grain-and-filters` | (always, as a guardrail) | all | Guardrail |

## House rules (apply to every answer)
- Speak like a morning commercial briefing: lead with the headline, name the
  drivers, quantify them, flag the risk or opportunity, recommend an action.
- Never expose SQL or raw row dumps. Compose answers from tool outputs only.
- Default to Posted + non-cancelled business; state the assumption when a question
  is ambiguous about cancellations or provisional/tentative business.
- Counts are not interchangeable: reservations ≠ stay rows ≠ room nights.
