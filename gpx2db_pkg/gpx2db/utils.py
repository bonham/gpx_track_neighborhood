import os


class ExecuteSQLFile:

    def __init__(self, connection, relative_dir="sql"):

        SQL_RELATIVE_DIR = relative_dir

        self.sqlBase = os.path.join(
            os.path.dirname(__file__),
            SQL_RELATIVE_DIR
        )

        self.conn = connection
        self.cursor = connection.cursor()

    def fpath(self, fname):

        p = os.path.join(
            self.sqlBase,
            fname)

        return p

    def execFile(self, fname, sqlArgs=[], commit=True):

        fpath = self.fpath(fname)

        #print("Execute SQL file {}".format(fpath))

        with open(fpath, "r") as f:
            sql = f.read()
            self.cursor.execute(sql, sqlArgs)

        if commit:
            self.conn.commit()
