import argparse
import psycopg2 as pg2
from gpx2db.utils import (
    drop_db,
    setup_logging,
    getDbParentParser,
    create_connection_string
    )
from gpx2db.gpx2dblib import Gpx2db

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
    logger.debug("Connection string: {}".format(connstring))

    drop_db(database_name, args) # delete and recreate
    # connect to newly created db
    conn = pg2.connect(connstring)

    conn.set_isolation_level(
        pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore

    g2d = Gpx2db(conn)

    g2d.init_db(drop=False)

# --------------------------------


def a_parse():
    parser = argparse.ArgumentParser(
        description=(
            'Create a new trackmanager database'
        ),
        parents=[getDbParentParser()])

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
