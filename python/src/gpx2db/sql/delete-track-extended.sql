delete from {schema}.circle_segment_intersections
where 
  segment_id in (
    select segment_id from newsegments
    where track_id = {0});

delete from {schema}.circles
where circle_id in (
  select point_id from {schema}.newpoints
  where track_id = {0}
);

delete from {schema}.frequency_lines where track_id = {0};
delete from {schema}.joined_points where track_id = {0};
delete from {schema}.newpoints where track_id = {0};
delete from {schema}.newsegments where track_id = {0};
