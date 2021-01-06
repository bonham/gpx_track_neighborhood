drop view if exists newpoints_w_subsegments;
create view newpoints_w_subsegments as 

with base as (
	-- current and last point of a segment
	select
		ogc_fid, track_id,
		segment_id,
		wkb_geometry,
		lag(wkb_geometry)  over (partition by segment_id order by ogc_fid) as lastpoint
	from newpoints
),
-- split segments every 5000m 
-- by calculating cumulative distance within each segment
-- and classify each point to a subsegments by doing integer division of cumulated distance
sub1 as (
	select
		ogc_fid,
		track_id,
		segment_id,
		round(
			sum(
				ST_Distance(wkb_geometry::geography, lastpoint::geography)
			) over (partition by segment_id order by ogc_fid)
		)::integer / 5000 as subseg,
		wkb_geometry
	from base
)
-- subseg can be 'null' for first point.
-- If yes then assign subseg of next point  in same segment.
select
	ogc_fid,
	track_id,
	segment_id,
	coalesce(
		subseg,
		lead(subseg) over (partition by segment_id order by ogc_fid)
	) as subseg,
	wkb_geometry
from sub1
order by ogc_fid
-- still it can be that subseg is null - in case there is only one point in segment_id