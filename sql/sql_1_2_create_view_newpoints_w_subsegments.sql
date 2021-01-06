drop view if exists newpoints_w_subsegments;
create view newpoints_w_subsegments as 
with base as (
	-- current and last point of a segment
	select
		ogc_fid, track_id,
		segment_id,
		wkb_geometry as curpoint,
		lag(wkb_geometry)  over (partition by segment_id order by ogc_fid) as lastpoint
	from newpoints
)
-- split segments every 5000m 
-- by calculating cumulative distance within each segment
-- and classify each point to a subsegments by doing integer division of cumulated distance
select
	ogc_fid,
	track_id,
	segment_id,
	round(
		sum(
			ST_Distance(curpoint::geography, lastpoint::geography)
		) over (partition by segment_id order by ogc_fid)
	)::integer / 5000 as subseg
from base