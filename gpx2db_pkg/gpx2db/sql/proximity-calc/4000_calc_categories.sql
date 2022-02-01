--- This SQL file is doing two things:
---
--- A) Assign the frequency number to all lines (derived from point freqency )
--- B) Enumerate all points and identify segments by looking for consecutive 
----   lines in same track, with same frequency

--- Create table
drop table if exists frequency_lines;
create table frequency_lines
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
create index on frequency_lines(point_id_end);

-- first population
insert into frequency_lines (
with fr as (
    select 
        np.point_id, 
        np.track_id, 
        np.segment_id, 
        f.freq 
      from newpoints np
      join count_circle_freq_all f on np.point_id = f.circle_id 
)
select 
    f1.point_id, 
    f2.point_id, 
    f1.track_id, 
    f1.segment_id, 
    LEAST(f1.freq,f2.freq) as cat
from fr f1
join fr f2 
on 
    f1.point_id = f2.point_id - 1 and 
    f1.track_id = f2.track_id and 
    f1.segment_id  = f2.segment_id
) ;
commit;

-- update last column with a segment counter
---
drop sequence if exists category_segment_seq;
create sequence category_segment_seq;
--select nextval('category_segment_seq');

update frequency_lines tf set category_segment = 
(
select 
--f1.point_id_start, f1.point_id_end, f2.point_id_start f2_id, f1.track_id, f1.segment_id, f1.freq,
--f1.point_id_start,
case when
	(f1.freq != f2.freq) or 
    (f1.track_id != f2.track_id) or 
    (f1.segment_id != f2.segment_id) or 
    (f2.point_id_start is null) 
then nextval('category_segment_seq')
else currval('category_segment_seq') END as inc
from frequency_lines f1
left join frequency_lines f2 on f2.point_id_end = f1.point_id_start 
where tf.point_id_start = f1.point_id_start
) ;


