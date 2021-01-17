--- new table for points
drop index if exists newpoints_seg_idx;
drop index if exists newpoints_tr_idx;
drop index if exists newpoints_geom_idx;

drop table if exists public.newpoints cascade;
create table public.newpoints
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


--- sequences
drop sequence if exists joinsegments_seq;
create sequence joinsegments_seq;

