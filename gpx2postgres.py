import sys
import re
import argparse
import psycopg2 as pg2
from gpx2db.utils import (
    drop_db, setup_logging,
    getfiles, getDbParentParser)
from gpx2db.gpximport import GpxImport
from gpx2db.gpx2dblib import Gpx2db
import traceback

# constants
PG_USER = "postgres"
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
        drop_db(database_name, args)

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

    # Loop over files and import
    gpximp = GpxImport(conn)

    for fname in gpx_filelist:

        try:
            track_ids_created = gpximp.import_gpx_file(fname)
        except Exception:
            logger.error(
                "Exception occurred when trying to import {}".format(fname))
            logger.error(traceback.format_exc())
            continue
        else:
            track_ids_created_s = [str(i) for i in track_ids_created]
            if track_ids_created:
                s_or_not = "s" if len(track_ids_created) > 1 else ""
                logger.info(
                    "Created track id{:s} {:s}".format(
                        s_or_not,
                        " ".join(track_ids_created_s)
                    )
                )


# --------------------------------


def a_parse():
    parser = argparse.ArgumentParser(
        description=(
            'Load GPX files from specified directory into postgis database'
        ),
        parents=[getDbParentParser()])

    parser.add_argument('dir_or_file',
                        help="GPX file or directory of GPX files")
    parser.add_argument('database')

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
