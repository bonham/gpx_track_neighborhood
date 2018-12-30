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
RADIUS_DEFAULT=30
TRACKS_TABLE="all_tracks"
TRACKPOINTS_TABLE="all_track_points"

def main():

    # parse args
    (database_name, radius) = a_parse()

    # connect to db
    conn = psycopg2.connect(
                "dbname={} user={}".format(database_name, PG_USER))
    cur = conn.cursor()

    # connection for vacuum
    conn_vac = psycopg2.connect(
                "dbname={} user={}".format(database_name, PG_USER))

    conn_vac.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    vac(conn_vac, TRACKS_TABLE)
    vac(conn_vac, TRACKPOINTS_TABLE)

    print("Joining track segments")
    joinsegments(conn, radius)
    vac(conn_vac, "newpoints")
    vac(conn_vac, "newsegments")

    print("Creating circles from points")
    create_circles(conn, radius)
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
    parser.add_argument('--radius',help="Radius in meters around a trackpoint, where we search for nearby tracks. Default is {}m".format(RADIUS_DEFAULT), default=RADIUS_DEFAULT )
    args = parser.parse_args()

    return args.database, args.radius

#--------------------------------
def joinsegments(conn, distance):

    with open('sql/sql_1_joinsegments.sql',"r") as f:
        sql = f.read()
        cur = conn.cursor()
        cur.execute(sql.format(distance))
        conn.commit()

def create_circles(conn, radius):

    with open('sql/sql_2_create_circles.sql',"r") as f:
        sql = f.read()
        cur = conn.cursor()
        print("Execute")
        cur.execute(sql.format(radius))
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