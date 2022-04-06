import argparse
import psycopg2 as pg2
from gpx2db.utils import (
    PG_ADMIN_DB,
    connect_nice,
    drop_db,
    create_db,
    setup_logging,
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

    logger = setup_logging(args.debug)
    logger.debug("Logger initialized")

    args.func(args)


def subcommand_cd(args):

    admin_connstring = create_connection_string(PG_ADMIN_DB, args)
    conn = connect_nice(admin_connstring)

    conn.set_isolation_level(
        pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore

    drop_db(args.database, admin_connstring)
    create_db(args.database, admin_connstring)


def subcommand_cs(args):
    admin_connstring = create_connection_string(args.database, args)
    conn = connect_nice(admin_connstring)

    conn.set_isolation_level(
        pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore

    schema = args.schema
    g2d = Gpx2db(conn, schema)
    g2d.create_schema()


def subcommand_cu():
    pass


def a_parse():
    """
    We have several subcommands

      cd - create a new db ( and drop existing db with same name )

      cs - create a new schema on existing db

      cu - create a user with write privileges on given schema in db

    Global parameters
        host, port, user, password

    """
    parser = argparse.ArgumentParser(
        description=(
            'Create a new trackmanager database, schema or user'
        ))

    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Enable debug output"
    )

    parser.add_argument(
        '-n',
        '--host',
        help="Database Host")

    parser.add_argument(
        '--port',
        help="Database Port")

    parser.add_argument(
        '-u',
        '--user',
        help=(
            "User to authenticate to db. "
            "This user should have privilege to create databases and users"))

    parser.add_argument(
        '-p',
        '--password',
        help="Password to authenticate to DB")

    # ---

    subparsers = parser.add_subparsers(
        help="Provide <subcommand> -h for further help.",
        required=True,
        )

    parser_cd = subparsers.add_parser('cd', help='Create database subcommand')
    parser_cd.add_argument('database')
    parser_cd.set_defaults(func=subcommand_cd)

    # ---
    parser_cs = subparsers.add_parser('cs', help='Create schema subcommand')
    parser_cs.add_argument(
        "database",
        help="Database where schema should be created")
    parser_cs.add_argument(
        'schema',
        help="Database Schema to be created (Do not use 'public')")
    parser_cs.set_defaults(func=subcommand_cs)

    # ---
    parser_cu = subparsers.add_parser('cu', help='Create user subcommand')
    parser_cu.add_argument(
        'username',
        help="Name of database user for new database to be created")
    parser_cu.add_argument(
        'userpassword',
        help="Password for new database user")
    parser_cu.set_defaults(func=subcommand_cu)

    args = parser.parse_args()

    return args

# --------------------------------


###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
