select
  ci.circle_id,
  se.segment_id,
  ST_Intersection(ci.wkb_geometry, se.wkb_geometry)
from
  circle_segment_intersections isec,
  circles ci,
  newsegments se
where
  ci.circle_id = isec.circle_id
  and
  se.segment_id = isec.segment_id
  and
  se.track_id = {}

  