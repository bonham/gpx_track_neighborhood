import sys
import argparse
import psycopg2 as pg2
from gpx2db.utils import (
    setup_logging,
    getfiles,
    getDbParentParser,
    create_connection_string,
    connect_nice
    )
from gpx2db.gpximport import GpxImport
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
    connstring = create_connection_string(database_name, args)

    # get gpx filenames
    gpx_filelist = getfiles(args.dir_or_file)
    logger.info("Number of gpx files: {}".format(len(gpx_filelist)))
    logger.info("Appending to database {}".format(database_name))

    conn = connect_nice(connstring)

    conn.set_isolation_level(
        pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore

    # Loop over files and import
    gpximp = GpxImport(conn)

    exit_code = 0
    for fname in gpx_filelist:

        try:
            track_ids_created = gpximp.import_gpx_file(fname)
        except Exception:
            exit_code = 1
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
    sys.exit(exit_code)


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
