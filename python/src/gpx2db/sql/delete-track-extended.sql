delete from circle_segment_intersections
where 
  segment_id in (
    select segment_id from newsegments
    where track_id = {0});

delete from circles
where circle_id in (
  select point_id from newpoints
  where track_id = {0}
);

delete from frequency_lines where track_id = {0};
delete from joined_points where track_id = {0};
delete from newpoints where track_id = {0};
delete from newsegments where track_id = {0};
