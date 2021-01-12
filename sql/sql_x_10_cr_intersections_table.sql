drop table if exists circle_segment_intersections;
create table circle_segment_intersections (
  circle_id integer not null,
  segment_id integer not null,
  CONSTRAINT ci_seg_intersections UNIQUE (circle_id, segment_id)
);

insert into circle_segment_intersections
select
  ci.ogc_fid,
  se.segment_id
from
  circles as si,
  joined_segments as se
where
  ST_Intersects(ci.wkb_geometry, se.wkb_geometry)
  and
  se.track_id = {}
