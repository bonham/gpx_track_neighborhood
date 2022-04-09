import argparse
from gpx2db.utils import (
    setup_logging,
    getDbParentParser,
    create_connection_string,
    connect_nice)


def main():

    # parse args
    args = a_parse()

    logger = setup_logging(args.debug)
    logger.debug("Starting")

    connstring = create_connection_string(args.database, args)

    conn = connect_nice(connstring)
    schema = args.schema

    sql = 'select id, src, name from {}.tracks order by id'.format(
        schema
    )
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
            'list gpx track with given id'
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


###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
