import os
import gpxpy
import logging
from hashlib import sha256
from .gpx2dblib import Gpx2db

logger = logging.getLogger(__name__)


class GpxImport:

    def __init__(self, conn):

        self.conn = conn
        self.g2d = Gpx2db(conn)

        self.hashes = self.load_hashes_from_db()

    def does_file_exist_in_db(self, fname):

        hash = self.get_hash_from_file(fname)

        return hash in self.hashes

    def get_hash_from_file(self, gpx_file_name):

        with open(gpx_file_name, 'rb') as gpx_fd_bin:

            hasher = sha256()
            bytes = gpx_fd_bin.read()
            hasher.update(bytes)
            return hasher.hexdigest()

    def load_hashes_from_db(self):

        sql = "select id, hash from tracks"
        cur = self.conn.cursor()
        cur.execute(sql)
        r = cur.fetchall()
        return {item[1]: item[0] for item in r}

    def import_gpx_file(self, gpx_file_name, force_append=False):

        honor_hashes = not force_append
        if honor_hashes and self.does_file_exist_in_db(gpx_file_name):
            basename = os.path.basename(gpx_file_name)
            logger.info("File {} does exist in database".format(basename))
            return []

        else:

            hash = self.get_hash_from_file(gpx_file_name)

            # utf-8-sig used bacause
            # https://stackoverflow.com/a/44573867/4720160
            # and because openrouteservice creates utf 8 with bom
            with open(gpx_file_name, 'r', encoding='utf-8-sig') as gpx_fd:
                gpx_o = gpxpy.parse(gpx_fd)

            src_info = os.path.basename(gpx_file_name)
            logger.info("Loading {}".format(src_info))
            track_ids_created = self.g2d.load_gpx_file(
                gpx_o, hash, src=src_info)

            return track_ids_created
