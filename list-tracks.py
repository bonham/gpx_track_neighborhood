import sys
import re
import argparse
import psycopg2 as pg2
from gpx2db.utils import (
    setup_logging,
    getDbParentParser,
    create_connection_string)


def main():

    # parse args
    args = a_parse()

    logger = setup_logging(args.debug)

    connstring = create_connection_string(args.database, args)

    try:

        conn = pg2.connect(connstring)

    except pg2.OperationalError as e:
        errmsg = e.args[0]
        if re.search(r'database .* does not exist', errmsg):
            logger.error(
                "Database {} does not exist.")
            sys.exit(1)
        else:
            raise

    sql = 'select id, src, name from tracks order by id'
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()

    for row in result:

        # backward compatibilty for bug in database content if row[2] == "None"
        if row[2] == "None" or row[2] is None:
            name = ''
        else:
            name = row[2]

        print("{:<6d} {:60s} {:s}".format(
            row[0], row[1], name
        ))


def a_parse():
    parser = argparse.ArgumentParser(
        description=(
            'Delete gpx track with given id from all database tables'
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


###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
