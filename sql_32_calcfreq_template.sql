insert into frequency( 
    select 
        tp.ogc_fid, 
        tp.track_fid, 
        sum(ST_NumGeometries(ST_Intersection(tr.wkb_geometry, ci.wkb_geometry ))),
        tp.wkb_geometry
    from tracksegments tr, circles ci, track_points tp 
    where 
        tp.ogc_fid = ci.ogc_fid
        and tp.track_fid = {}
    group by tp.track_fid, tp.ogc_fid
)


