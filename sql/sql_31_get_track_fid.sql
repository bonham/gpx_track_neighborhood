select track_id, name, file_name
from all_tracks allt, track_files tf
where tf.file_id = allt.file_id
order by track_id
