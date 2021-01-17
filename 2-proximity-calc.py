import sys
import argparse
import os
import psycopg2
import logging
from gpx2db import ExecuteSQLFile, vac


if sys.version_info < (3, 6):
    raise RuntimeError(
        "You must use python 3.6, You are using python {}.{}.{}".format(
            *sys.version_info[0:3]))

# constants

PG_USER = "postgres"
RADIUS_DEFAULT = 30
TRACKS_TABLE = "tracks"
TRACKPOINTS_TABLE = "track_points"


def main():

    # parse args
    (database_name, host, db_user, password, dbport, radius, debug) = a_parse()

    if debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logging.basicConfig(level=loglevel)

    # connect to db
    conn = psycopg2.connect(
        "dbname={} host={} user={} password={} port={}".format(
            database_name,
            host,
            db_user,
            password,
            dbport))

    # connection for vacuum
    conn_vac = psycopg2.connect(
        "dbname={} host={} user={} password={} port={}".format(
            database_name,
            host,
            db_user,
            password,
            dbport))

    conn_vac.set_isolation_level(
        psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore
    vac(conn_vac, TRACKS_TABLE)
    vac(conn_vac, TRACKPOINTS_TABLE)

    transform = Transform(conn)

    print("Create tables and idexes")
    transform.create_structure()

    # change later and integrate with gpx file loading
    track_list = transform.get_tracks()

    for new_track_id in track_list:

        print("Joining track segments")
        transform.joinsegments(new_track_id)
        vac(conn_vac, "newpoints")
        vac(conn_vac, "newsegments")

        all_point_ids = transform.get_point_ids()
        new_point_ids = transform.get_point_ids(tracks=[new_track_id])

        all_segment_ids = transform.get_segment_ids()
        new_segment_ids = transform.get_segment_ids([new_track_id])

        print("\n== New track no {} has {} segments and {} points".format(
            new_track_id,
            len(new_segment_ids),
            len(new_point_ids)
        ))
        print("Joining with a total of {} segments and {} points".format(
            len(all_segment_ids),
            len(all_point_ids)
        ))

        print("Creating circles from points")
        transform.create_circles(radius, new_track_id)
        vac(conn_vac, "circles")

        print("Do intersections")
        transform.do_intersection(new_track_id)

        print("Count frequencies")
        transform.count_frequency()

    # print("Calculating frequency")
    # transform.calc_frequency()
    # vac(conn_vac, "frequency")


# --------------------------------


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
            '3400_view_count_circle_freq.sql')

    def joinsegments(self, track_id):

        self.executor.execFile(
            '0100_joinsegments_create_newpoints.sql',
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

    def count_frequency(self):
        cur = self.conn.cursor()
        cur.execute('select * from count_circle_freq_all')
        r = cur.fetchall()
        return r

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

    def get_tracks(self):
        "Get all track ids"

        cur = self.conn.cursor()

        sql = "select id from tracks order by id"
        cur.execute(sql)
        r = cur.fetchall()
        track_id_list = [x[0] for x in r]
        return track_id_list

    def in_clause(self, values_list):

        # convert to strings
        values_list = map(str, values_list)

        r = "IN (" + ",".join(values_list) + ")"
        return r


def a_parse():
    parser = argparse.ArgumentParser(
        description=(
            'Load GPX files in specified directory into postgis database'
        ))
    parser.add_argument('database')
    parser.add_argument(
        '--radius',
        help=(
            "Radius in meters around a trackpoint, "
            "where we search for nearby tracks. "
            "Default is {}m").format(
            RADIUS_DEFAULT), default=RADIUS_DEFAULT)

    parser.add_argument(
        '-n',
        '--host',
        default='localhost',
        help="Database Host")
    parser.add_argument(
        '-u',
        '--user',
        default=PG_USER,
        help="Database user")
    parser.add_argument(
        '-p',
        '--password',
        default='',
        help="Database Password")
    parser.add_argument(
        '--port',
        default='5432',
        help="Database Port")
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Enable debug output"

    )
    args = parser.parse_args()

    return (
        args.database,
        args.host,
        args.user,
        args.password,
        args.port,
        args.radius,
        args.debug
    )

# --------------------------------


###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
