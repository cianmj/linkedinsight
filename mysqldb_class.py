import MySQLdb


class Database(object):

    def __init__(self,host,user,passwd,db):
        self.host = self
        self.user = user
        self.password=passwd
        self.db = db

        self.connection = MySQLdb.connect(self.host, self.user, self.password, self.db)
        self.cursor = self.connection.cursor()

    def insert(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except:
            self.connection.rollback()


    def query(self, query):
        cursor = self.connection.cursor( MySQLdb.cursors.DictCursor )
        cursor.execute(query)

        return cursor.fetchall()

    def __del__(self):
        self.connection.close()


if __name__ == "__main__":

    db = Database("localhost","root","","linkedinsight")

    #CleanUp Operation
    #del_query = "DELETE FROM basic_python_database"
    #db.insert(del_query)

    sql = """CREATE TABLE features (userid int(20) not null primary key, feature varchar(30))"""
    db.insert(sql)#cursor.execute(sql)

    sql = "INSERT INTO features VALUES (%s,%s)"
    db.insert(sql)#cursor.execute(sql,(1,"testing"))


