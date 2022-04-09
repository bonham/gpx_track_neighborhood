import os
import argparse
import psycopg2 as pg2
from gpx2db.utils import (
    setup_logging,
    vac, getfiles, getDbParentParser,
    create_connection_string,
    connect_nice)
from gpx2db.Transform import (
    Transform,
    RADIUS_DEFAULT,
    TRACKS_TABLE,
    TRACKPOINTS_TABLE)
from gpx2db.gpximport import GpxImport

# constants
PG_USER = "postgres"


def main():

    # parse args
    args = a_parse()
    database_name = args.database
    schema = args.schema

    logger = setup_logging(args.debug)
    connstring = create_connection_string(database_name, args)

    # get gpx filenames
    gpx_filelist = getfiles(args.dir_or_file)
    logger.info("Number of gpx files: {}".format(len(gpx_filelist)))

    logger.info("Appending to database {}".format(database_name))

    # connect to newly created db
    conn = connect_nice(connstring)
    conn.set_isolation_level(
        pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore

    # connection for vacuum
    conn_vac = connect_nice(connstring)
    conn_vac.set_isolation_level(
        pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore
    vac(conn_vac, "{}.{}".format(schema, TRACKS_TABLE))
    vac(conn_vac, "{}.{}".format(schema, TRACKPOINTS_TABLE))

    transform = Transform(conn, schema)

    # Loop over files and import
    gpximp = GpxImport(conn, schema)
    totalfiles = len(gpx_filelist)

    for idx, fname in enumerate(gpx_filelist):

        fileno = idx + 1
        track_ids_created = gpximp.import_gpx_file(fname)
        track_basename = os.path.basename(fname)
        logger.info(
            "\n\n=== Processing file no {}/{}: {}".format(
                fileno,
                totalfiles,
                track_basename
            )
        )

        for new_track_id in track_ids_created:

            logger.info("Preparing track segments")
            transform.prepare_segments(new_track_id)
            vac(conn_vac, "{}.newpoints".format(schema))
            vac(conn_vac, "{}.newsegments".format(schema))

            all_point_ids = transform.get_point_ids()
            new_point_ids = transform.get_point_ids(tracks=[new_track_id])

            all_segment_ids = transform.get_segment_ids()
            new_segment_ids = transform.get_segment_ids([new_track_id])

            logger.info(
                "New track no {} has {} segments and {} points".format(
                    new_track_id,
                    len(new_segment_ids),
                    len(new_point_ids)
                ))
            logger.info(
                "Joining with a total of {} segments and {} points".format(
                    len(all_segment_ids),
                    len(all_point_ids)
                ))

            logger.info("Creating circles from points")
            transform.create_circles(args.radius, new_track_id)
            vac(conn_vac, "{}.circles".format(
                schema
            ))

            logger.info("Do intersections")
            transform.do_intersection(new_track_id)

    logger.info("\n=== Calculating categories")
    transform.calc_categories()

# --------------------------------


def a_parse():
    parser = argparse.ArgumentParser(
        description=(
            'Add GPX files from specified file or directory '
            'to database and perform proximity calculation'
        ),
        parents=[getDbParentParser()])

    parser.add_argument('dir_or_file',
                        help="GPX file or directory of GPX files")
    parser.add_argument('database')

    parser.add_argument(
        '--radius',
        help=(
            "Radius in meters around a trackpoint, "
            "where we search for nearby tracks. "
            "Default is {}m").format(
            RADIUS_DEFAULT), default=RADIUS_DEFAULT)

    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Enable debug output"
    )
    parser.add_argument('schema')

    args = parser.parse_args()

    return args

# --------------------------------


###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
