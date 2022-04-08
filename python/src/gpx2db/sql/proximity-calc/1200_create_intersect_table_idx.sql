drop index if exists intersect_table_idx_cid;
drop index if exists intersect_table_idx_segid;
drop index if exists intersect_table_idx_geom;

create index intersect_table_idx_cid on {schema}.circle_segment_intersections (circle_id);
create index intersect_table_idx_segid on {schema}.circle_segment_intersections (segment_id);
CREATE INDEX intersect_table_idx_geom ON {schema}.circle_segment_intersections USING gist(wkb_geometry);