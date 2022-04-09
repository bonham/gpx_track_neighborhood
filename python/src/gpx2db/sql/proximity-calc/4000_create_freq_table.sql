drop table if exists {schema}.frequency_lines;
create table {schema}.frequency_lines
(
    point_id_start integer not NULL,
    point_id_end integer not NULL,
    track_id integer not null,
    segment_id integer not null,
    freq integer not null,
    category_segment integer,
    constraint freq_lines_pk primary key (point_id_start )
)
tablespace pg_default;
create index on {schema}.frequency_lines(point_id_end);



