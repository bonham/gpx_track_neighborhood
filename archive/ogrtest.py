import ogr
import sys

databaseServer = "localhost"
databaseName = "gistest"
databaseUser = "postgres"
databasePW = "an3fang"


connString = "PG: host=%s dbname=%s user=%s password=%s" %(databaseServer,databaseName,databaseUser,databasePW)

########

def GetPGLayer( lyr_name ):
    conn = ogr.Open(connString)

    lyr = conn.GetLayer( lyr_name )
    if lyr is None:
        print >> sys.stderr, '[ ERROR ]: layer name = "%s" could not be found in database "%s"' % ( lyr_name, databaseName )
        sys.exit( 1 )

    featureCount = lyr.GetFeatureCount()
    print "Number of features in %s: %d" % ( lyr_name , featureCount )

    layerDefn = lyr.GetLayerDefn()
    print("LayerName: "+ layerDefn.GetName())
    print("Layer fid column:" + lyr.GetFIDColumn())
    feature = ogr.Feature(layerDefn)

    print("Assigning point to feature")
    wkt = "POINT (1120351.5712494177 741921.4223245403)"
    point = ogr.CreateGeometryFromWkt(wkt)

    

    feature.SetGeometry(point)

    layer = lyr
    layer.StartTransaction()
#    layer.CreateFeature(feature)
    feature = None
    layer.CommitTransaction()

    # Close connection
    conn = None


if __name__ == '__main__':

    if len( sys.argv ) < 2:
        print >> sys.stderr, '[ ERROR ]: you must pass at least one argument -- the layer name argument'
        sys.exit( 1 )

    lyr_name = sys.argv[1]
    GetPGLayer( lyr_name )


