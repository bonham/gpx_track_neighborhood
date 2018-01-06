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

    # calc
    with open('sql/sql_40_calc_categories.sql',"r") as f:
       sql1 = f.read()
    cur.execute(sql1) 

    with open('sql/sql_42_create_category_table.sql',"r") as f:
       sql2 = f.read()
    cur.execute(sql2) 

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
