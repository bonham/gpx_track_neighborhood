import sys
import argparse
import glob
import os
import subprocess
import psycopg2
import pandas as pd
import pandas.io.sql as pdsql

if sys.version_info < (3,6):
    raise RuntimeError("You must use python 3.6, You are using python {}.{}.{}".format(*sys.version_info[0:3]))

# constants

PG_USER="postgres"

def main():

    # parse args
    database_name = a_parse()

    # connect to db
    conn = psycopg2.connect(
                "dbname={} user={}".format(database_name, PG_USER))
    cur = conn.cursor()

    # read ids and frequencies 
    df = pdsql.read("select * from tracks",conn)
    df = psql.read_sql("select ogc_fid,freq from frequency",conn)
    


#--------------------------------
def a_parse():
    parser = argparse.ArgumentParser(
            description = 
                'Assign categories to track-lines'
            )
    parser.add_argument('database')
    args = parser.parse_args()

    database_name = args.database
    return database_name



###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
