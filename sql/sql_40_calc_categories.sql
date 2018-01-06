--- Create structures

drop table if exists public.frequency_lines;
create table public.frequency_lines
(
    ogc_fid_start integer not NULL,
    ogc_fid_end integer not NULL,
    track_fid integer not null,
    track_seg_id integer not null,
    freq integer not null,
    category_segment integer,
    constraint freq_lines_pk primary key (ogc_fid_start )
)
tablespace pg_default;

-- first population

insert into public.frequency_lines (
with fr as (select tp.ogc_fid, tp.track_fid, tp.track_seg_id, f.freq 
      from track_points tp
      join frequency f on tp.ogc_fid = f.ogc_fid 
)
select f1.ogc_fid, f2.ogc_fid, f1.track_fid, f1.track_seg_id, LEAST(f1.freq,f2.freq) as cat
from fr f1
join fr f2 on f1.ogc_fid = f2.ogc_fid - 1 and f1.track_fid = f2.track_fid and f1.track_seg_id  = f2.track_seg_id
) ;

-- update last column
drop sequence if exists category_segment_seq;
create sequence category_segment_seq;
--select nextval('category_segment_seq');

update frequency_lines tf set category_segment = 
(
select 
--f1.ogc_fid_start, f1.ogc_fid_end, f2.ogc_fid_start f2_id, f1.track_fid, f1.track_seg_id, f1.freq,
--f1.ogc_fid_start,
case when
	(f1.freq != f2.freq) or 
    (f1.track_fid != f2.track_fid) or 
    (f1.track_seg_id != f2.track_seg_id) or 
    (f2.ogc_fid_start is null) 
then nextval('category_segment_seq')
else currval('category_segment_seq') END as inc
from frequency_lines f1
left join frequency_lines f2 on f2.ogc_fid_end = f1.ogc_fid_start 
where tf.ogc_fid_start = f1.ogc_fid_start
) 


