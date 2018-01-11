insert into frequency( 
--
-- First intersect all circles with all tracksegments
-- and split all intersection multilinestrings into linestrings
with dump as (
    select 
        tp.ogc_fid, 
        tp.track_fid, 
    	tr.ogc_fid as track_id,
		-- Split the multilinestrings
    	(ST_Dump(ST_Multi(ST_Intersection(tr.wkb_geometry, ci.wkb_geometry )))).path[1] as path,
        (ST_Dump(ST_Multi(ST_Intersection(tr.wkb_geometry, ci.wkb_geometry )))).geom as linestring,
        tp.wkb_geometry
    from track_joinsegments tr, circles ci, track_points tp 
    where 
        tr.wkb_geometry && ci.wkb_geometry
        and tp.ogc_fid = ci.ogc_fid
		and tp.track_fid = {}
) 
-- Now analyze all consecutive intersections for a given circle and tracksegment. If the lines do not touch we count it. 
-- We also count the last intersection (=dump2.linestring is null because of left join and because dump2.path-1 does not exist because sequence is at its end)
select
	dump1.ogc_fid,
    dump1.track_fid,
	count(
        case
            when (dump2.linestring is null) or 
            not (ST_EndPoint(dump1.linestring) = ST_StartPoint(dump2.linestring )) THEN 1 
        END
    ),
    dump1.wkb_geometry
from dump as dump1 
left join dump as dump2 on 
    dump1.path = dump2.path-1 and 
    dump1.ogc_fid = dump2.ogc_fid and
    dump1.track_id = dump2.track_id
group by
	dump1.ogc_fid,
    dump1.track_fid,
    dump1.wkb_geometry
order by
	dump1.ogc_fid
)
