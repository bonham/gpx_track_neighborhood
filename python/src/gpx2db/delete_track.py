import os
import argparse
import psycopg2 as pg2
from gpx2db.utils import (
    ExecuteSQLFile,
    setup_logging,
    getDbParentParser,
    create_connection_string,
    connect_nice
    )


def main():

    # parse args
    args = a_parse()
    database_name = args.database
    schema = args.schema

    logger = setup_logging(args.debug)
    connstring = create_connection_string(database_name, args)

    conn = connect_nice(connstring)

    sqldir = os.path.join(
        os.path.dirname(__file__),
        'sql')
    ex = ExecuteSQLFile(conn, sqldir, schema=schema)

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
    parser.add_argument('schema')
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
