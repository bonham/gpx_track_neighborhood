import argparse
import psycopg2
import logging
from gpx2db import vac, getfiles
from gpx2db.proximity_calc import Transform
from gpx2db.gpximport import gpximport


# constants
PG_USER = "postgres"
RADIUS_DEFAULT = 30
TRACKS_TABLE = "tracks"
TRACKPOINTS_TABLE = "track_points"


def main():

    # parse args
    (
        directory,
        database_name,
        host,
        db_user,
        password,
        dbport,
        radius,
        delete_db,
        debug) = a_parse()

    if debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logging.basicConfig(level=loglevel)

    # get gpx filenames
    gpx_filelist = getfiles(directory)
    print("Number of gpx files: {}".format(len(gpx_filelist)))

    if delete_db:
        print("(Re-) creating database {}".format(database_name))
    else:
        print("Appending to database {}".format(database_name))

    gpximport(gpx_filelist, database_name, delete_db,
              host, db_user, password, dbport)

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

    print("\nCalculating categories")
    transform.calc_categories()

# --------------------------------


def a_parse():
    parser = argparse.ArgumentParser(
        description=(
            'Load GPX files from specified directory into postgis database'
        ))
    parser.add_argument('source_directory')
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
        '--createdb',
        action='store_true',
        help=(
            "Create the database. If it does already exist, "
            "the old db will be overwritten!"))
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Enable debug output"

    )
    args = parser.parse_args()

    return (
        args.source_directory,
        args.database,
        args.host,
        args.user,
        args.password,
        args.port,
        args.radius,
        args.createdb,
        args.debug
    )

# --------------------------------


###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
