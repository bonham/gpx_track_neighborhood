import sys
import argparse
import glob
import os
import subprocess
import psycopg2

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

    # connection for vacuum
    conn_vac = psycopg2.connect(
                "dbname={} user={}".format(database_name, PG_USER))

    conn_vac.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    vac(conn_vac, "tracks")
    vac(conn_vac, "track_points")

    print("Expanding track segments")
    expand_tracksegments(conn)
    vac(conn_vac, "tracksegments")

    print("Creating circles from points")
    create_circles(conn)
    vac(conn_vac, "circles")

    print("Calculating frequency")
    calc_frequency(conn)
    vac(conn_vac, "frequency")
    


#--------------------------------
def a_parse():
    parser = argparse.ArgumentParser(
            description = 
                'Load GPX files in specified directory into postgis database'
            )
    parser.add_argument('database')
    args = parser.parse_args()

    database_name = args.database
    return database_name

#--------------------------------
def expand_tracksegments(conn):

    with open('sql/sql_1_expand_tracks.sql',"r") as f:
        sql = f.read()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

def create_circles(conn):

    with open('sql/sql_2_create_circles.sql',"r") as f:
        sql = f.read()
        cur = conn.cursor()
        print("Execute")
        cur.execute(sql)
        print("Commit")
        conn.commit()
        print("Commit done")

def calc_frequency(conn):

    cur = conn.cursor()

    # create table
    with open('sql/sql_30_create_freq_tab.sql',"r") as f:
        sql = f.read()
        cur.execute(sql)
        conn.commit()

    # read list of track ids
    sql2 = None

    with open('sql/sql_31_get_track_fid.sql',"r") as f:
        sql2 = f.read()
        
    cur.execute(sql2)
    tracks = cur.fetchall()
#    track_ids = [(x[0] for x in r]
    num_ids = len(tracks)

    # make intersections for each point

    sql3 = None
    with open('sql/sql_32_calcfreq_template.sql',"r") as f3:
        sql3 = f3.read()

    for (tid, name) in tracks:
        print("Intersecting for track id {}/{} {}".format(tid, num_ids, name))
        tsql = sql3.format(tid)
        cur.execute(tsql)
        conn.commit()

def vac(conn, table):
    cur = conn.cursor()
    cur.execute("vacuum analyze {}".format(table))
        


###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
