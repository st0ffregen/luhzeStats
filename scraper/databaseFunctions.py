import MySQLdb
import os


def connectToDB():
    con = MySQLdb.connect(
        host=os.environ['DB_CONTAINER_NAME'],
        db=os.environ['MYSQL_DB'],
        user=os.environ['MYSQL_SCRAPING_USER'],
        passwd=os.environ['MYSQL_SCRAPING_PASSWORD']
    )
    con.set_character_set('utf8mb4')
    con.autocommit(False)
    return con


def closeConnectionToDB(con, cur):
    cur.close()
    con.close()


def executeSQL(sqlArray, con, cur):
    for statement in sqlArray:
        cur.execute(statement[0], statement[1])
    con.commit()
