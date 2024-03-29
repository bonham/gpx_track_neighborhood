import os
from .utils import ExecuteSQLFile, read_snip_coords
import logging

# others import these constants
RADIUS_DEFAULT = 30
TRACKS_TABLE = "tracks"
TRACKPOINTS_TABLE = "track_points"


class Transform:

    def __init__(self, conn, schema):

        self.conn = conn
        self.schema = schema

        sqldir = os.path.join(os.path.dirname(
            __file__), 'sql', 'proximity-calc')
        self.executor = ExecuteSQLFile(
            conn,
            base_dir=sqldir,
            schema=self.schema,
            )
        self.logger = logging.getLogger(__name__)

    def create_structure(self):

        self.executor.execFile(
            '0100_create_newpoints_table.sql')
        self.executor.execFile(
            '0200_create_segments_table.sql')
        self.executor.execFile(
            '0400_create_segments_table_idx.sql')
        self.executor.execFile(
            '1000_cr_intersections_table.sql')
        self.executor.execFile(
            '1200_create_intersect_table_idx.sql')
        self.executor.execFile(
            '1300_create_circles_table.sql')
        self.executor.execFile(
            '3000_view_gtype.sql')
        self.executor.execFile(
            '3100_view_ml_debug.sql')
        self.executor.execFile(
            '3200_view_count_ml_consecutive.sql')
        self.executor.execFile(
            '3300_view_count_linestrings.sql')
        self.executor.execFile(
            '3400_view_count_circle_freq_all.sql')
        self.executor.execFile(
            '4000_create_freq_table.sql')
        self.executor.execFile(
            '4100_create_category_table.sql')

    def prepare_segments(self, track_id):

        clip_coords = read_snip_coords()
        whereclause = gpx_clip_where_clause(clip_coords)

        self.executor.execFile(
            '0100_joinsegments_create_newpoints.sql',
            args=(whereclause, track_id,))

        self.executor.execFile(
            '0250_insert_enriched_points.sql',
            args=(track_id,))

        self.executor.execFile(
            '0300_insert_segments.sql',
            args=(track_id,))

    def create_circles(self, radius, track_id):

        self.executor.execFile(
            '1310_insert_circles.sql',
            args=(radius, track_id)
        )

    def do_intersection(self, new_track_id):

        where_new_points = "and np.track_id = {}".format(
            new_track_id
        )
        # all existing segments (including new ones) with circles of new track
        self.logger.info("... calc for new track")
        self.executor.execFile(
            '2000_insert_intersections.sql',
            args=(
                where_new_points,
            )
        )

        # all existing circles (excluding new ones) with segments of new track
        self.logger.info("... calc for existing tracks")
        where_new_segments = \
            " and se.track_id = {} and np.track_id != {}".format(
                new_track_id,
                new_track_id)
        self.executor.execFile(
            '2000_insert_intersections.sql',
            args=(
                where_new_segments,
            )
        )

    def calc_categories(self):

        self.executor.execFile('4300_calc_categories.sql')

    def get_segment_ids(self, tracks=[]):
        "Get segment ids for all or given track"

        cur = self.conn.cursor()

        sql = "select segment_id from {}.newsegments ".format(
            self.schema
        )
        if tracks:
            sql += "where track_id " + self.in_clause(tracks)

        cur.execute(sql)
        r = cur.fetchall()
        segment_id_list = [x[0] for x in r]

        return segment_id_list

    def get_point_ids(self, tracks=[]):
        "Get point ids for all or given tracks"

        cur = self.conn.cursor()

        sql = "select point_id from {}.newpoints".format(
            self.schema
        )

        if tracks:
            sql += " where track_id " + self.in_clause(tracks)

        cur.execute(sql)
        r = cur.fetchall()
        point_id_list = [x[0] for x in r]

        return point_id_list

    def in_clause(self, values_list):

        # convert to strings
        values_list = map(str, values_list)

        r = "IN (" + ",".join(values_list) + ")"
        return r


def gpx_clip_where_clause(latlon_pair_list):
    "Convert latlon pairs in a where clause"
    "To cut out all points 1km around the locations"

    clip_args = ["1 = 1"]  # pepare for missing latlon_pair_list

    for pair in latlon_pair_list:

        argstring = (
            """
                ST_Distance(
                    tp.wkb_geometry::geography,
                    ST_PointFromText('POINT({:s} {:s})', 4326)::geography
                ) >= 1000
            """
        ).format(
            pair[1], pair[0]
        )
        clip_args.append(argstring)

    return " AND ".join(clip_args)
