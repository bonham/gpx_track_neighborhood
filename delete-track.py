import sys
import os
import re
import argparse
import psycopg2 as pg2
from gpx2db.utils import (
    ExecuteSQLFile, setup_logging,
    getDbParentParser)


def main():

    # parse args
    args = a_parse()
    database_name = args.database

    logger = setup_logging(args.debug)

    try:
        conn = pg2.connect(
            "dbname={} host={} user={} password={} port={}".format(
                database_name, args.host, args.user,
                args.password, args.port))
    except pg2.OperationalError as e:
        errmsg = e.args[0]
        if re.search(r'database .* does not exist', errmsg):
            logger.error(
                "Database {} does not exist.")
            sys.exit(1)
        else:
            raise
    sqldir = os.path.join(
        os.path.dirname(__file__),
        'gpx2db_pkg',
        'gpx2db',
        'sql')
    ex = ExecuteSQLFile(conn, sqldir)
    ex.execFile('delete-track.sql', args=(args.track_id,))

    logger.info("Track deleted")


def a_parse():
    parser = argparse.ArgumentParser(
        description=(
            'Delete gpx track with given id from all database tables'
        ),
        parents=[getDbParentParser()])

    parser.add_argument('database')
    parser.add_argument('track_id',
                        help="id of track",
                        type=int)

    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Enable debug output"
    )
    args = parser.parse_args()

    return args


###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
