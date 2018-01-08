
# length
select name, ST_Length(wkb_geometry), ST_LengthSpheroid(wkb_geometry, 'SPHEROID["WGS 84",6378137,298.257223563]') / 1000 as km from tracks;





---- insert intersections into tmpgeom
insert into tmpgeom (
    select 
    	nextval('intersections_id_seq'),
        (ST_Dump(ST_Intersection(tr.wkb_geometry, ci.wkb_geometry ))).geom AS the_geom
    from tracks tr, circles ci, track_points tp 
    where 
    	tp.ogc_fid = ci.ogc_fid
        and ST_NumGeometries(ST_Intersection(tr.wkb_geometry, ci.wkb_geometry )) > 0
        and tp.ogc_fid = 349
)

---or 

delete from tmpgeom;
insert into tmpgeom (
select
    	nextval('intersections_id_seq'),
        (ST_Dump(ST_Intersection(tr.wkb_geometry, ci.wkb_geometry ))).geom as geom
    from tracks tr, circles ci, track_points tp where tp.ogc_fid = ci.ogc_fid
    and  ci.ogc_fid = 406 and tr.ogc_fid = 3
)

---------------------------

DROP TABLE if exists public.tmpgeom;

CREATE TABLE public.tmpgeom
(
    ogc_fid integer NOT NULL,
    wkb_geometry geometry(Point,4326),
    CONSTRAINT tmpgeom2 PRIMARY KEY (ogc_fid)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.tmpgeom
    OWNER to postgres;

drop index if exists tmpgeom_wkb_geometry_geom_idx;
CREATE INDEX tmpgeom_wkb_geometry_geom_idx
    ON public.tmpgeom USING gist
    (wkb_geometry)
    TABLESPACE pg_default;

------
	select 
        nextval('intersections_id_seq'),
		ST_AsText((ST_Dump(ST_LineMerge(ST_Intersection(tr.wkb_geometry, ci.wkb_geometry )))).geom) as the_geom
    from tracks tr, circles ci, track_points tp 
    where 
        tr.wkb_geometry && ci.wkb_geometry
        and tp.ogc_fid = ci.ogc_fid
        and tp.ogc_fid in (269);

------
delete from tmpgeom;
insert into tmpgeom(
select 
        nextval('intersections_id_seq'),
		(ST_Dump(ST_Intersection(tr.wkb_geometry, ci.wkb_geometry ))).geom as the_geom
    from tracks tr, circles ci, track_points tp 
    where 
        tr.wkb_geometry && ci.wkb_geometry
        and tp.ogc_fid = ci.ogc_fid
        and tp.ogc_fid in (269)
)

---- merge 
select ST_AsText(ST_LineMerge(ST_GeomFromText('MULTILINESTRING((0 0, 1 0),(1 0, 2 0),(3 0,4 0))')))            
--- result 2
--- special points
406

     379 | LINESTRING(8.7278440552249 49.4038218743186,8.728182 49.403572,8.72819016737288 49.4036291716102)
     380 | LINESTRING(8.72819016737288 49.4036291716102,8.72822291098671 49.4038583769069)
     381 | LINESTRING(8.72821844336025 49.4038607520625,8.728062 49.403713,8.72819016737288 49.4036291716102)
     382 | LINESTRING(8.72819016737288 49.4036291716102,8.72825662148193 49.4035857070307)

select ST_AsText(c) from (select ST_Collect(wkb_geometry) as c from tmpgeom) as x

select d,i,s, sum(s) OVER ( order by i ROWS 1 PRECEDING) from e order by i ;

--- problempunkte in hires

939 / 940 - category_segment = 113
line frequency ist 5
punkt frequency ist 9 