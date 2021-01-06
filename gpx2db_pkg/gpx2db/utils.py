import os


class ExecuteSQLFile:

    def __init__(self, connection, base_dir=''):

        self.base_dir = base_dir

        self.conn = connection
        self.cur = connection.cursor()

    def fpath(self, fname):

        p = os.path.join(
            self.base_dir,
            fname)

        return p

    def execFile(self, fname, sqlArgs=[], args=(), commit=True):

        fpath = self.fpath(fname)

        #print("Execute SQL file {}".format(fpath))

        with open(fpath, "r") as f:
            sqltemplate = f.read()
            sql = sqltemplate.format(args)
            self.cursor().execute(sql, sqlArgs)

        if commit:
            self.conn.commit()

    def cursor(self):
        return self.cur
