-- Statistics how  many points in segments
drop view if exists newpoints_seg_stats ;
create view newpoints_seg_stats as 
select track_id, segment_id, count(ogc_fid) as numpoints from newpoints group by track_id, segment_id order by segment_id
