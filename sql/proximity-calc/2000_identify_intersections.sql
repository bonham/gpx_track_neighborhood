-- identify pairs of intersections , but not do the intersection right now
-- the wkb_geometry column will be empty first
insert into circle_segment_intersections (
  circle_id,
  segment_id
) select
  ci.circle_id,
  se.segment_id
from
  circles as ci,
  newsegments as se
where
  ST_Intersects(ci.wkb_geometry, se.wkb_geometry)
  and
  se.track_id = {}
