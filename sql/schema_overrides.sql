-- Schema overrides, applied AFTER schema.sql, BEFORE the data load.
--
-- The source data cannot satisfy one foreign key in schema.sql: the rate_plan_code
-- FK. Reservations book against 16 granular rate codes (e.g. EXPP, BARCBB, BOOKBARB),
-- while rate_plan_lookup is a fixed 8-row reference dimension. A strict FK + an 8-row
-- lookup + loading every real rate code cannot all hold at once.
--
-- Decision: keep the real rate_plan_code on the fact table (it is needed for the
-- pricing/commercial questions the agent answers) and treat rate_plan_lookup as a
-- partial descriptive dimension rather than an enforced parent. We therefore drop
-- ONLY this one FK. The other three dimensions (space_type, market_code,
-- channel_code) reference their lookups cleanly and are left fully enforced.
-- See ARCHITECTURE.md for the rationale.

alter table public.reservations
  drop constraint if exists reservations_rate_plan_code_fkey;
