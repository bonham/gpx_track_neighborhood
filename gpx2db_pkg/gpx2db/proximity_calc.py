import os
from .utils import ExecuteSQLFile
import logging


class Transform:

    def __init__(self, conn):

        self.conn = conn

        sqldir = os.path.join(os.path.dirname(
            __file__), 'sql', 'proximity-calc')
        self.executor = ExecuteSQLFile(conn, base_dir=sqldir)
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

    def joinsegments(self, track_id):

        self.executor.execFile(
            '0100_joinsegments_create_newpoints.sql',
            args=(track_id,))

        self.executor.execFile(
            '0250_insert_enriched_points.sql')

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

        self.executor.execFile('4000_calc_categories.sql')
        self.executor.execFile('4100_create_category_table.sql')

    def get_segment_ids(self, tracks=[]):
        "Get segment ids for all or given track"

        cur = self.conn.cursor()

        sql = "select segment_id from newsegments "
        if tracks:
            sql += "where track_id " + self.in_clause(tracks)

        cur.execute(sql)
        r = cur.fetchall()
        segment_id_list = [x[0] for x in r]

        return segment_id_list

    def get_point_ids(self, tracks=[]):
        "Get point ids for all or given tracks"

        cur = self.conn.cursor()

        sql = "select point_id from newpoints"

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
