--- 2 new tables and one view for points

--- Table 1/3: Joining segments nearby:
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

--- View 2/3: Simplifying the track:
drop view if exists simplified_segments;
create view simplified_segments as
SELECT
    track_id,
    track_segment_id_old,
    segment_id,
  	ST_Simplify(
          ST_MakeLine(wkb_geometry order by point_id),
          0.00001
      ) as wkb_geometry
from joined_points
group by
    track_id,
    track_segment_id_old,
    segment_id
;

drop view if exists simplified_points;
create view simplified_points as
select
    track_id,
    track_segment_id_old,
    segment_id,
    (ST_Dump(wkb_geometry)).path[1] as segment_point_number,
	(ST_Dump(wkb_geometry)).geom as wkb_geometry
from simplified_segments
;

--- Table 3/3: Enriching track and filling gaps between points
drop table if exists newpoints cascade;
create table newpoints
(
    point_id integer not NULL,
    track_id integer not null,
    track_segment_id_old integer not null,
    segment_id integer not null,
    wkb_geometry geometry(Point,4326) not null,
    constraint newpoints_pk primary key (point_id )
);
create index newpoints_seg_idx on newpoints(segment_id);
create index newpoints_tr_idx on newpoints(track_id);
CREATE INDEX newpoints_geom_idx
    ON newpoints USING gist(wkb_geometry);

-- TODO: crate statistics view

