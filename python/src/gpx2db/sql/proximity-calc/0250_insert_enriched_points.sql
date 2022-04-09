insert into {schema}.newpoints (
  point_id,
  segment_id,
  track_id,
  wkb_geometry
)
SELECT
  nextval('{schema}.newpoints_seq'),
  segment_id,
  track_id,
  wkb_geometry
FROM
  {schema}.enriched_points
where track_id = {}
order by
  segment_id,
  segment_point_number,
  multipoint_id
;
