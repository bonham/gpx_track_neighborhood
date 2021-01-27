--- tables and views for transforming points

--- 1/4: Joining segments nearby:
drop table if exists joined_points cascade;
create table joined_points
(
    point_id integer not NULL,
    track_id integer not null,
    track_segment_id_old integer not null,
    segment_id integer not null,
    wkb_geometry geometry(Point,4326) not null,
    constraint joined_points_pk primary key (point_id )
);
create index joined_points_seg_idx on joined_points(segment_id);
create index joined_points_tr_idx on joined_points(track_id);
CREATE INDEX joined_points_geom_idx
    ON joined_points USING gist(wkb_geometry);

--- sequences
drop sequence if exists joinsegments_seq;
create sequence joinsegments_seq;

--- View 2/4: Simplifying the track:
create or replace view simplified_segments as
SELECT
    segment_id,
    track_id,
  	ST_Simplify(
          ST_MakeLine(wkb_geometry order by point_id),
          0.00001
      ) as wkb_geometry
from joined_points
group by
    track_id,
    segment_id
;

create or replace view simplified_points as
select
    row_number() over (order by segment_id, segment_point_number) as tmp_id,
    track_id, segment_id, segment_point_number, wkb_geometry
from (
    select
        track_id,
        segment_id,
        (ST_DumpPoints(wkb_geometry)).path[1] as segment_point_number,
        (ST_DumpPoints(wkb_geometry)).geom as wkb_geometry
    from simplified_segments
) as base

;

--- 3/4 View: fill gaps between points

create or replace view enriched_points as
--- three layers to interpolate between simplified points
--- ( read from bottom up )

-- when selecting from this view then use order:
--    segment_id, segment_point_number, multipoint_id

-- Dump points from interpolated multipoints
select
  segment_id,
  segment_point_number,
  track_id,
  (ST_DumpPoints(interp_points)).path[1] as multipoint_id,
  (ST_DumpPoints(interp_points)).geom as wkb_geometry

from (
  select
    -- interpolate points in line ( leads to multipoints )
    segment_id,
    segment_point_number,
    track_id,
    distance,
    div(distance::numeric, 50) as needed,
    ST_LineInterpolatePoints(
      wkb_line,
      1.0 / (div(distance::numeric, 50) + 1)
    ) as interp_points

  from (
    -- calc distance and make line
    select
      segment_id,
      segment_point_number,
      track_id,
      round(
        ST_Distance(
          thispoint::geography,
          nextpoint::geography
      )) as distance,
      ST_MakeLine(thispoint, nextpoint) as wkb_line
    FROM (
      -- window function: this and next point
      select
        segment_id,
        segment_point_number,
        track_id,
        wkb_geometry as thispoint,
        lead(wkb_geometry) over (
          order by segment_id, segment_point_number) as nextpoint
      FROM
        simplified_points
    ) as base1
  ) as base2
) as base3
;


--- 4/4: Table Final result
drop table if exists newpoints cascade;
create table newpoints
(
    point_id integer not NULL,
    segment_id integer not null,
    track_id integer not null,
    wkb_geometry geometry(Point,4326) not null,
    constraint newpoints_pk primary key (point_id )
);
create index newpoints_seg_idx on newpoints(segment_id);
create index newpoints_tr_idx on newpoints(track_id);
CREATE INDEX newpoints_geom_idx
    ON newpoints USING gist(wkb_geometry);

--- newpoints sequences
drop sequence if exists newpoints_seq;
create sequence newpoints_seq;


-- 5/4 ;-) View: statistics view
create or replace view track_processing_stats as
select * from (
	select '1-track_points' as phase, track_id, count(track_id) from track_points group by track_id
	union all
	select '3-simplified_points' as phase, track_id, count(track_id) from simplified_points
	group by track_id
	union all
	select '2-joined_points' as phase, track_id, count(track_id) from joined_points group by track_id
	union all
	select '4-newpoints' as phase, track_id, count(track_id) from newpoints group by track_id

) as base
order by track_id, phase
;

