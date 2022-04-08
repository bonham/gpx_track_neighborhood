import argparse
import psycopg2 as pg2
from gpx2db.utils import (
    setup_logging,
    getDbParentParser,
    create_connection_string,
    connect_nice
)
from gpx2db.proximity_calc import (
    Transform
)


def main():

    # parse args
    args = a_parse()
    database_name = args.database
    logger = setup_logging(args.debug)
    logger.debug("Args parsed")
    connstring = create_connection_string(database_name, args)
    conn = connect_nice(connstring)
    conn.set_isolation_level(
        pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore
    # TODO: check where we do vacuuming
    transform = Transform(conn, args.schema)
    transform.create_structure()


def a_parse():
    parser = argparse.ArgumentParser(
        description=(
            'Add proximator extension to gpxdb'
        ),
        parents=[getDbParentParser()])

    parser.add_argument('database')
    parser.add_argument('schema')

    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Enable debug output"
    )
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    # execute only if run as a script
    main()
