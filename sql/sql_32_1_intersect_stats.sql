--- count how many circles of a given track do intersect with other tracks
 select 
    count(ci.ogc_fid) as numpoints,
    tf.file_name,
    allt.name,
    se.track_fid as intersect_track_fid
        
    from newsegments se, circles ci, newpoints tp, all_tracks allt, track_files tf
    where 
        se.wkb_geometry && ci.wkb_geometry
        and tp.ogc_fid = ci.ogc_fid
        and se.track_fid = allt.track_id
        and allt.file_id = tf.file_id
        and tp.track_fid = {}
    group by se.track_fid, tf.file_name, allt.name
    order by se.track_fid
