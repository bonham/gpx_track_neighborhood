import sys
import argparse
import os
import psycopg2
import json
import shutil

if sys.version_info < (3, 6):
    raise RuntimeError("You must use python 3.6, You are using python {}.{}.{}".format(
        *sys.version_info[0:3]))

# constants

PG_USER = "postgres"
METADATA_FNAME = "datasets.json"
BASEDIR = os.path.normpath("html/static/geojson")
MAXCATEGORIES = 5


def main():

    # parse args
    (database_name, host, db_user, password, dbport, outputDir, mode) = a_parse()

    # connect to db
    conn = psycopg2.connect(
        "dbname={} host={} user={} password={} port={}".format(
            database_name,
            host,
            db_user,
            password,
            dbport))
    cur = conn.cursor()

    geodir = os.path.join(BASEDIR, outputDir)

    cleanup(geodir)
    create_extend_metadata(BASEDIR, METADATA_FNAME, outputDir)

    (geometryList, categoryList) = (None, None)
    if mode == "category":

        (geometryList, categoryList) = queryCategoryMode(cur)

    elif mode == 'plain':

        (geometryList, categoryList) = queryPlainMode(cur, MAXCATEGORIES)

    legendFilePath = os.path.join(geodir, "legend.json")
    writeLegendFile(legendFilePath, categoryList)

    # print categories
    for item in categoryList:
        print(
            "Category {}: {:3} - {:3}".format(item["category"], item["min"], item["max"]))

    writeGeoJsonFiles(geometryList, geodir)

    numTrackFilePath = os.path.join(geodir, "numberOfTracks.json")
    writeNumTracksFile(numTrackFilePath, len(geometryList))


# --------------------------------
def a_parse():
    parser = argparse.ArgumentParser(
        description='Write gpx tracks as geojson to disk. The output directory will be "html/static/geojson/<dataset_label>/'
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
    parser.add_argument(
        'dataset_label', help="This should be a unique label of your gpx set. E.g '2019'")
    parser.add_argument(
        '-m',
        default="category",
        type=str,
        choices=('category', 'plain'),
        help="Extraction mode. Possible values: category|plain. If you omit the flag, the default is category")
    parser.add_argument(
        '--port',
        default='5432',
        help="Database Port")
    args = parser.parse_args()

    print("Mode is {}".format(args.m))
    return (
        args.database,
        args.host,
        args.user,
        args.password,
        args.port,
        args.dataset_label,
        args.m
    )


def cleanup(geodir):

    # remove directory if exists
    print("Removing {}".format(geodir))
    if os.path.exists(geodir) and os.path.isdir(geodir):
        shutil.rmtree(geodir)

    # recreate directory ( including parents )
    os.makedirs(geodir, exist_ok=True)


def create_extend_metadata(directory, filename, label):

    fpath = os.path.join(directory, filename)

    # Create file if it is not existing
    if os.path.exists(fpath):

        with open(fpath, 'r') as fp:
            mdata = json.load(fp)

    else:

        mdata = []

    # Insert label at beginning of list if not in list
    if label not in mdata:
        print("Adding {} to {}".format(label, fpath))
        mdata.insert(0, label)
    else:
        print("Label {} is already in {}".format(label, fpath))

    # write file
    print("Writing {}".format(fpath))
    with open(fpath, 'w') as fp:
        json.dump(mdata, fp)


def queryCategoryMode(cur):

    # read geojson
    cur.execute("select category, ST_AsGeoJSON(ST_Collect(wkb_geometry)), min(freq), max(freq) from track_segment_freq_categories group by category order by category")
    r = cur.fetchall()

    geometryList = []
    categoryList = []

    i = 0
    for row in r:
        (realcat, js, minfreq, maxfreq) = row
        geometryList.append(js)
        categoryList.append({"category": i, "min": minfreq, "max": maxfreq})
        i += 1

    return (geometryList, categoryList)


def queryPlainMode(cur, maxCategories):

    # read geojson
    cur.execute(
        "select id, ST_AsGeoJSON(wkb_geometry) from tracks order by id")
    r = cur.fetchall()

    geometryList = []
    categoryList = []

    i = 1
    for row in r:
        (track_id, js) = row
        geometryList.append(js)

        if i <= maxCategories:
            categoryList.append(
                {"category": i, "min": track_id, "max": track_id})
        i += 1

    return (geometryList, categoryList)


def writeGeoJsonFiles(geomList, geodir):

    i = 0
    for js in geomList:

        fname = os.path.join(geodir, "g_{}.json".format(i))
        print("Writing "+fname)
        with open(fname, "w") as f:
            f.write(js)

        i += 1


def writeNumTracksFile(fpath, num):

    # write file about how many tracks we have
    print("Writing {}".format(fpath))
    with open(fpath, "w") as fp:
        json.dump(
            {"numberOfTrackFiles": num},
            fp
        )


def writeLegendFile(fpath, cat_frequencies):

    # dump file for legend
    print("Writing {}".format(fpath))
    with open(fpath, "w") as legendfile:
        json.dump(cat_frequencies, legendfile)


###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
