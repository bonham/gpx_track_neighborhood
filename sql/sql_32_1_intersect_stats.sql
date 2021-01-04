--- count how many circles of a given track do intersect with other tracks
 select 
    count(ci.ogc_fid) as numpoints,
    src,
    tracks.name,
    se.track_id as intersect_track_id
        
    from newsegments se, circles ci, newpoints tp, tracks
    where 
        se.wkb_geometry && ci.wkb_geometry
        and tp.ogc_fid = ci.ogc_fid
        and se.track_id = tracks.id
        and tp.track_id = {}
    group by se.track_id, src, tracks.name
    order by se.track_id
