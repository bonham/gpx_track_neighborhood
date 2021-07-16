import sys
import os
import re
import argparse
import psycopg2 as pg2
from gpx2db.utils import (
    ExecuteSQLFile,
    setup_logging,
    getDbParentParser,
    create_connection_string
    )


def main():

    # parse args
    args = a_parse()
    database_name = args.database

    logger = setup_logging(args.debug)
    connstring = create_connection_string(database_name, args)

    try:
        conn = pg2.connect(connstring)
    except pg2.OperationalError as e:
        logger.debug(e)
        if len(e.args) > 0:
            errmsg = e.args[0]
        else:
            errmsg = ""
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

    ex.execFile('delete-track-base.sql', args=(args.track_id,))
    try:
        ex.execFile('delete-track-extended.sql', args=(args.track_id,))
    except pg2.errors.UndefinedTable:
        logger.warning("Some of the extended tables not found")

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
