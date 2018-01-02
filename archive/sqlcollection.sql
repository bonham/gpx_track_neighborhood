
# distance
select t1.ogc_fid, t1.wkb_geometry, t2.ogc_fid, t2.wkb_geometry, ST_Distance ( t1.wkb_geometry , t2.wkb_geometry ) as entfernung , ST_DistanceSphere(t1.wkb_geometry, t2.wkb_geometry) as e2 from track_points t1, track_points t2 where t2.ogc_fid = 3;  



# length
select name, ST_Length(wkb_geometry), ST_LengthSpheroid(wkb_geometry, 'SPHEROID["WGS 84",6378137,298.257223563]') / 1000 as km from tracks;

# schneide Kreis mit tracks
select ST_AsText(ST_Intersection(tr.wkb_geometry, ST_Buffer(tp.wkb_geometry::geography, 4000) )) from tracks tr, track_points tp where tp.ogc_fid = 3;

select tp.track_fid, tp.ogc_fid, sum(ST_NumGeometries(ST_AsText(ST_Intersection(tr.wkb_geometry, ST_Buffer(tp.wkb_geometry::geography, 20) )))) -1 from tracks tr, track_points tp  
group by tp.track_fid, tp.ogc_fid order by tp.ogc_fid;

---------------------------

DROP TABLE if exists public.circles;

CREATE TABLE public.circles
(
    ogc_fid integer NOT NULL,
    wkb_geometry geometry(Polygon,4326),
    CONSTRAINT circles2 PRIMARY KEY (ogc_fid)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.circles
    OWNER to postgres;

drop index if exists circles_wkb_geometry_geom_idx;
CREATE INDEX circles_wkb_geometry_geom_idx
    ON public.circles USING gist
    (wkb_geometry)
    TABLESPACE pg_default;

insert into circles (select ogc_fid, ST_Buffer(tp.wkb_geometry::geography, 20)::geometry from track_points as tp);

---------------------------

DROP TABLE if exists public.frequency;

CREATE TABLE public.frequency
(
    ogc_fid integer NOT NULL,
    track_fid integer NOT NULL,
    freq integer NOT NULL,
    wkb_geometry geometry(Point,4326),
    CONSTRAINT frequency2 PRIMARY KEY (ogc_fid)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.frequency
    OWNER to postgres;

drop index if exists frequency_wkb_geometry_geom_idx;
CREATE INDEX frequency_wkb_geometry_geom_idx
    ON public.frequency USING gist
    (wkb_geometry)
    TABLESPACE pg_default;

insert into frequency( 
    select 
        tp.ogc_fid, 
        tp.track_fid, 
        sum(ST_NumGeometries(ST_Intersection(tr.wkb_geometry, ci.wkb_geometry ))) -1 ,
        tp.wkb_geometry
    from tracksegments tr, circles ci, track_points tp where tp.ogc_fid = ci.ogc_fid
group by tp.track_fid, tp.ogc_fid order by tp.ogc_fid
)

--------

DROP TABLE if exists public.intersections;
Drop sequence if exists public.intersections_id_seq;
CREATE SEQUENCE public.intersections_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE public.intersections_id_seq
    OWNER TO postgres;


CREATE TABLE public.intersections
(
	intersect_id integer default nextval('intersections_id_seq'::regclass),
    trackpoint integer NOT NULL,
    trackpoint_belongsto integer not null,
    track_intersect integer NOT NULL,
    wkb_geometry geometry(Multilinestring,4326),
    numgeometries integer not null,
    CONSTRAINT intersections2 PRIMARY KEY (intersect_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.intersections
    OWNER to postgres;

drop index if exists intersections_wkb_geometry_geom_idx;
CREATE INDEX intersections_wkb_geometry_geom_idx
    ON public.intersections USING gist
    (wkb_geometry)
    TABLESPACE pg_default;

insert into intersections( 
    select 
    	nextval('intersections_id_seq'),
        tp.ogc_fid as trackpoint, 
        tp.track_fid as trackpoint_belongsto, 
        tr.ogc_fid as track_intersect,
        ST_Multi(ST_Intersection(tr.wkb_geometry, ci.wkb_geometry )),
        ST_NumGeometries(ST_Intersection(tr.wkb_geometry, ci.wkb_geometry )) 
    from tracks tr, circles ci, track_points tp 
    where 
    	tp.ogc_fid = ci.ogc_fid
        and ST_NumGeometries(ST_Intersection(tr.wkb_geometry, ci.wkb_geometry )) > 0
        and tp.track_fid = 3
)

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


----- create expanded track table

DROP TABLE if exists public.tracksegments;

Drop sequence if exists public.tracksegments_id_seq;
CREATE SEQUENCE public.tracksegments_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE public.tracksegments_id_seq
    OWNER TO postgres;


CREATE TABLE public.tracksegments
(
    tr_linestring_id integer NOT NULL,
    track_fid integer NOT NULL,
    wkb_geometry geometry(Linestring,4326),
    CONSTRAINT tracksegments2 PRIMARY KEY (tr_linestring_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.tracksegments
    OWNER to postgres;

drop index if exists tracksegments_wkb_geometry_geom_idx;
CREATE INDEX tracksegments_wkb_geometry_geom_idx
    ON public.tracksegments USING gist
    (wkb_geometry)
    TABLESPACE pg_default;

insert into tracksegments (
    select 
		nextval('tracksegments_id_seq'),
    	tr.ogc_fid,
    	(ST_Dump(tr.wkb_geometry)).geom as geom
	from tracks tr
)



--- special points
406


insert into frequency( 
    select 
        track_points.ogc_fid, 
        sum(ST_NumGeometries((ST_Intersection(tracks.wkb_geometry, circles.wkb_geometry ))) -1 
    from tracks, circles, track_points 
    where 
        track_points.ogc_fid = circles.ogc_fid
    group by
        track_points.ogc_fid order by track_points.ogc_fid
    )
