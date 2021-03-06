import os
import sys
import re
import argparse
import psycopg2 as pg2
from gpx2db.utils import (
    drop_db, setup_logging,
    vac, getfiles, getDbParentParser)
from gpx2db.proximity_calc import Transform
from gpx2db.gpximport import GpxImport
from gpx2db.gpx2dblib import Gpx2db


# constants
PG_USER = "postgres"
RADIUS_DEFAULT = 30
TRACKS_TABLE = "tracks"
TRACKPOINTS_TABLE = "track_points"


def main():

    # parse args
    args = a_parse()
    database_name = args.database

    logger = setup_logging(args.debug)

    # get gpx filenames
    gpx_filelist = getfiles(args.dir_or_file)
    logger.info("Number of gpx files: {}".format(len(gpx_filelist)))

    if args.createdb:
        logger.info("(Re-) creating database {}".format(database_name))
    else:
        logger.info("Appending to database {}".format(database_name))

    if args.createdb:
        drop_db(database_name, args.password, host=args.host, dbport=args.port)

#    gpximport(gpx_filelist, database_name, args.createdb,
#              host, db_user, password, dbport)
    # connect to newly created db
    try:
        conn = pg2.connect(
            "dbname={} host={} user={} password={} port={}".format(
                database_name, args.host, args.user,
                args.password, args.port))
    except pg2.OperationalError as e:
        errmsg = e.args[0]
        if re.search(r'database .* does not exist', errmsg):
            logger.error(
                "Database {} does not exist. "
                "Use the --create flag or choose existing DB")
            sys.exit(1)
        else:
            print(re)
            print(e)
            raise

    conn.set_isolation_level(
        pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore

    g2d = Gpx2db(conn)

    # TODO: move database initialization up
    if args.createdb:
        g2d.init_db(drop=True)

    # connection for vacuum
    conn_vac = pg2.connect(
        "dbname={} host={} user={} password={} port={}".format(
            database_name, args.host, args.user,
            args.password, args.port))

    conn_vac.set_isolation_level(
        pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore
    vac(conn_vac, TRACKS_TABLE)
    vac(conn_vac, TRACKPOINTS_TABLE)

    transform = Transform(conn)

    logger.info("Create tables and idexes")

    if args.createdb:
        transform.create_structure()

    # Loop over files and import
    gpximp = GpxImport(conn)
    totalfiles = len(gpx_filelist)

    for idx, fname in enumerate(gpx_filelist):

        fileno = idx + 1
        track_ids_created = gpximp.import_gpx_file(fname)
        track_basename = os.path.basename(fname)
        logger.info(
            "\n\n=== Processing file no {}/{}: {}".format(
                fileno,
                totalfiles,
                track_basename
            )
        )

        for new_track_id in track_ids_created:

            logger.info("Preparing track segments")
            transform.prepare_segments(new_track_id)
            vac(conn_vac, "newpoints")
            vac(conn_vac, "newsegments")

            all_point_ids = transform.get_point_ids()
            new_point_ids = transform.get_point_ids(tracks=[new_track_id])

            all_segment_ids = transform.get_segment_ids()
            new_segment_ids = transform.get_segment_ids([new_track_id])

            logger.info(
                "New track no {} has {} segments and {} points".format(
                    new_track_id,
                    len(new_segment_ids),
                    len(new_point_ids)
                ))
            logger.info(
                "Joining with a total of {} segments and {} points".format(
                    len(all_segment_ids),
                    len(all_point_ids)
                ))

            logger.info("Creating circles from points")
            transform.create_circles(args.radius, new_track_id)
            vac(conn_vac, "circles")

            logger.info("Do intersections")
            transform.do_intersection(new_track_id)

    logger.info("\n=== Calculating categories")
    transform.calc_categories()

# --------------------------------


def a_parse():
    parser = argparse.ArgumentParser(
        description=(
            'Add GPX files from specified file or directory to database and perform proximity calculation'
        ),
        parents=[getDbParentParser()])

    parser.add_argument('dir_or_file',
                        help="GPX file or directory of GPX files")
    parser.add_argument('database')

    parser.add_argument(
        '--radius',
        help=(
            "Radius in meters around a trackpoint, "
            "where we search for nearby tracks. "
            "Default is {}m").format(
            RADIUS_DEFAULT), default=RADIUS_DEFAULT)

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

    return args

# --------------------------------


###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
