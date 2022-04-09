drop table if exists {schema}.circle_segment_intersections cascade;
create table {schema}.circle_segment_intersections (
  circle_id integer not null,
  segment_id integer not null,
  wkb_geometry geometry(Geometry,4326), -- can be null
  CONSTRAINT ci_seg_intersections UNIQUE (circle_id, segment_id)
);