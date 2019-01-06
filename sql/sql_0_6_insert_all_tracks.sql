insert into all_tracks ( track_id, file_id, ogc_fid, name, wkb_geometry )
select 
    nextval('all_tracks_track_id_seq'),
    %s,
    ogc_fid,
    name,
    wkb_geometry
from tracks;
