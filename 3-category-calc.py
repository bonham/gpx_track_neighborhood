import sys
import argparse
import os
import psycopg2

if sys.version_info < (3, 6):
    raise RuntimeError("You must use python 3.6, You are using python {}.{}.{}".format(
        *sys.version_info[0:3]))

# constants

PG_USER = "postgres"


def main():

    # parse args
    (database_name, host, db_user, password) = a_parse()

    # connect to db
    conn = psycopg2.connect(
        "dbname={} host={} user={} password={}".format(
            database_name,
            host,
            db_user,
            password))
    cur = conn.cursor()

    # calc
    with open('sql/sql_40_calc_categories.sql', "r") as f:
        sql1 = f.read()
    cur.execute(sql1)

    with open('sql/sql_42_create_category_table.sql', "r") as f:
        sql2 = f.read()
    cur.execute(sql2)

    for notice in conn.notices:
        print(notice)

# --------------------------------


def a_parse():
    parser = argparse.ArgumentParser(
        description='Assign categories to track-lines'
    )
    parser.add_argument('database')

    parser.add_argument(
        '-n',
        '--host',
        default='localhost',
        help="Database Host")
    parser.add_argument(
        '-u',
        '--user',
        default=PG_USER,
        help="Database user")
    parser.add_argument(
        '-p',
        '--password',
        default='',
        help="Database Password")
    args = parser.parse_args()

    return (
        args.database,
        args.host,
        args.user,
        args.password,
    )


###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
