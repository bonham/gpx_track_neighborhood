--- This SQL file is doing two things:
---
--- A) Assign the frequency number to all lines (derived from point freqency )
--- B) Enumerate all points and identify segments by looking for consecutive 
----   lines in same track, with same frequency

-- first population
insert into {schema}.frequency_lines (
with fr as (
    select 
        np.point_id, 
        np.track_id, 
        np.segment_id, 
        f.freq 
      from {schema}.newpoints np
      join {schema}.count_circle_freq_all f on np.point_id = f.circle_id 
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
drop sequence if exists {schema}.category_segment_seq;
create sequence {schema}.category_segment_seq;
--select nextval('category_segment_seq');

update {schema}.frequency_lines tf set category_segment = 
(
select 
--f1.point_id_start, f1.point_id_end, f2.point_id_start f2_id, f1.track_id, f1.segment_id, f1.freq,
--f1.point_id_start,
case when
	(f1.freq != f2.freq) or 
    (f1.track_id != f2.track_id) or 
    (f1.segment_id != f2.segment_id) or 
    (f2.point_id_start is null) 
then nextval('{schema}.category_segment_seq')
else currval('{schema}.category_segment_seq') END as inc
from {schema}.frequency_lines f1
left join {schema}.frequency_lines f2 on f2.point_id_end = f1.point_id_start 
where tf.point_id_start = f1.point_id_start
) ;

-- Create strings for each segment and insert it into table

-- Dieses Art die Linestrings zu erzeugen ist nicht ganz zuverlässig. Eigentlich sollten nur Linestrings entstehen, aber ST_Linemerge schafft es in seltenen fällen nur einen MultiLineString zu erzeugen. Eigentlich sollte man nicht ST_Linemerge nutzen, sondern über die category_segment id's iterieren und mit ST_MakeLine alle vokommenden Punkte in der gegebenen Reihenfolge verketten.

insert into {schema}.track_segment_freq_categories (
select
    fl.category_segment,
    fl.freq,
    null,
    ST_Multi(ST_Linemerge(ST_Collect(ST_MakeLine(np1.wkb_geometry, np2.wkb_geometry))))
from
	{schema}.frequency_lines fl,
    {schema}.newpoints np1,
    {schema}.newpoints np2
where
	np1.point_id = fl.point_id_start  and
    np2.point_id = fl.point_id_end
group by fl.category_segment, fl.freq
order by fl.category_segment, fl.freq
);
commit;
-- insert logarithmic scale for 5 categories
update  {schema}.track_segment_freq_categories
set category = round(log((select power(max(freq), 1./4) from {schema}.track_segment_freq_categories), freq));

