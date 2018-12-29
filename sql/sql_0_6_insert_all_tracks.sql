insert into all_tracks 
select 
    nextval('all_tracks_track_id_seq'),
    %s,
    *
from tracks;
