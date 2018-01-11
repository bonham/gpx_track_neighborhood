--- This sql does join the tracksegments of a track if the gap between the segments is below a threshold. Threshold should be aligned and should be not much bigger than the circle radius

DROP TABLE if exists public.track_joinsegments;
CREATE TABLE public.track_joinsegments
(
    ogc_fid integer NOT NULL,
    wkb_geometry geometry(MultiLineString,4326),
    CONSTRAINT track_joinsegments2 PRIMARY KEY (ogc_fid)
);
CREATE INDEX track_joinsegments_wkb_geometry_geom_idx
    ON public.track_joinsegments USING gist
    (wkb_geometry);
 
--------------------------------

insert into track_joinsegments

--- 'track' consists of multilinestrings:One linestring per track segment. Split this into sets of LINESTRING elements, one per track segment.

--- unique identifier is ogcfid + p
with dump as (
    SELECT 
    	ogc_fid, 
    	name,  
    	(ST_Dump(wkb_geometry)).geom as geom,
    	(ST_Dump(wkb_geometry)).path[1] as p
	FROM public.tracks ),

completeset as 
(( select
	ogc_fid,
    p,
    1 as linecategory, --- original track segments have line category 1 ( for ordering the segments and connecting points later)
    geom
from dump
union
---- make connecting line between track segments, but only if distance is below threshold
select
	d1.ogc_fid,
	d1.p, 
    2 as linecategory, --- connecting lines have category 2 
	ST_MakeLine(ST_EndPoint(d1.geom), ST_StartPoint(d2.geom)) as geom
from dump d1, dump d2 
where
	d1.ogc_fid = d2.ogc_fid and
	d1.p = d2.p - 1 and
   ST_Distance(ST_EndPoint(d1.geom)::geography, ST_StartPoint(d2.geom)::geography) < {}
)

-- correct order is important: first order by tracks then by path number of 
-- linestrings. The path number of the connecting line 
-- has same path number of starting segment, but with linecategory 2
 order by ogc_fid, p, linecategory
)
select ogc_fid, ST_Multi(ST_LineMerge(ST_Collect(geom))) as wkb_geometry
from completeset 
group by ogc_fid
having not ST_IsEmpty(ST_LineMerge(ST_Collect(geom))) -- ST_LineMerge returns empty if Linestring is single point
order by ogc_fid



