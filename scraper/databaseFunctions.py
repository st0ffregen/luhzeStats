import MySQLdb
import os


def connectToDB():
    con = MySQLdb.connect(
        host=os.environ['DB_CONTAINER_NAME'],
        db=os.environ['MYSQL_DB'],
        user='root',
        passwd=os.environ['MYSQL_ROOT_PASSWORD']
    )
    con.set_character_set('utf8mb4')
    con.autocommit(False)
    cur = con.cursor()
    return con, cur


def closeConnectionToDB(con, cur):
    cur.close()
    con.close()


def executeSQL(sqlArray, con, cur):
    for statement in sqlArray:
        cur.execute(statement[0], statement[1])

    con.commit()
