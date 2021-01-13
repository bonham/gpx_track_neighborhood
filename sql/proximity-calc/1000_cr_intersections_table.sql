drop table if exists circle_segment_intersections;
create table circle_segment_intersections (
  circle_id integer not null,
  segment_id integer not null,
  wkb_geometry geometry(MultiLineString,4326), -- can be null
  CONSTRAINT ci_seg_intersections UNIQUE (circle_id, segment_id)
);