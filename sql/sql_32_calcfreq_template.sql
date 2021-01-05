insert into frequency( 
--
-- First intersect all circles with all tracksegments
-- and split all intersection multilinestrings into linestrings
with dump as (
    select 
        tp.ogc_fid, 
        tp.track_id, 
    	se.segment_id as trackseg_id,
		-- Split the multilinestrings
    	(ST_Dump(ST_Multi(ST_Intersection(se.wkb_geometry, ci.wkb_geometry )))).path[1] as path,
        (ST_Dump(ST_Multi(ST_Intersection(se.wkb_geometry, ci.wkb_geometry )))).geom as linestring,
        tp.wkb_geometry
    from newsegments se, circles ci, newpoints tp 
    where 
        -- only overlapping boundary box
        se.wkb_geometry && ci.wkb_geometry
        -- assign circles to the points
        and tp.ogc_fid = ci.ogc_fid
        -- only intersect for a single track at once ( to be able for calling code to print progress )
		and tp.track_id = {}
) 
-- Now analyze all consecutive intersections for a given circle and tracksegment. If the lines do not touch we count them. 
-- We also count the last intersection (=dump2.linestring is null because of left join and because dump2.path-1 does not exist because sequence is at its end)
select
	dump1.ogc_fid,
    dump1.track_id,
	count(
        case
            when (dump2.linestring is null) or 
            not (ST_EndPoint(dump1.linestring) = ST_StartPoint(dump2.linestring )) THEN 1 
        END
    ),
    dump1.wkb_geometry
from dump as dump1 
left join dump as dump2 on 
    -- startpoint of second linestring needs to be endpoint of first linestring 
    dump1.path = dump2.path-1 and 
    -- only compare linestrings in same segment
    dump1.trackseg_id = dump2.trackseg_id
    -- also it should be an intersection of the same circle: ( see tp.ogc_fid = ci.ogc_fid clause in definition of 'dump' view)
    dump1.ogc_fid = dump2.ogc_fid and
group by
	dump1.ogc_fid,
    dump1.track_id,
    -- center of circle:
    dump1.wkb_geometry
order by
	dump1.ogc_fid
)
