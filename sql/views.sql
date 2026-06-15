-- Semantic views for the tool layer (Phase 2).
--
-- The required tools query these views, never reservations_hackathon directly.
-- vw_stay_night_base and vw_segment_stay_night are the brief's required views
-- (sql/VIEWS.example.sql, verbatim semantics). vw_stay_night_posted is an
-- "equivalent" supporting view (the brief permits equivalents): it keeps the
-- Posted-only grain but *retains* cancelled rows, so the point-in-time
-- (get_as_of_otb) and include-cancelled (get_otb_summary exclude_cancelled=False)
-- paths can still read a curated view instead of the raw fact table.

-- Default OTB universe: Posted, non-cancelled.
create or replace view public.vw_stay_night_base as
select r.*
from public.reservations_hackathon r
where r.reservation_status <> 'Cancelled'
  and r.financial_status = 'Posted';

-- Posted-only grain that *keeps* cancelled rows. Cancellation is applied as an
-- explicit predicate by the tool that needs the toggle / point-in-time view.
create or replace view public.vw_stay_night_posted as
select r.*
from public.reservations_hackathon r
where r.financial_status = 'Posted';

-- Stay-night grain with the stay-date-effective macro group resolved from
-- market_macro_group_history (falling back to the static lookup when no history
-- row covers the stay date).
create or replace view public.vw_segment_stay_night as
select
  b.*,
  coalesce(h.macro_group, m.macro_group) as effective_macro_group,
  m.market_name
from public.vw_stay_night_base b
join public.market_code_lookup m on m.market_code = b.market_code
left join lateral (
  select h.macro_group
  from public.market_macro_group_history h
  where h.market_code = b.market_code
    and b.stay_date >= h.valid_from
    and (h.valid_to is null or b.stay_date < h.valid_to)
  order by h.valid_from desc
  limit 1
) h on true;
