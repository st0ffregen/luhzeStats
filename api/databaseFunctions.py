import MySQLdb
import os
from api import app
from flask import g

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


def closeConnectionToDB():
    g.con.close()
    g.cur.close()


def get_cur():
    if 'cur' not in g:
        g.con = connectToDB()
        g.cur = g.con.cursor()


@app.teardown_appcontext
def teardownDB(exception):
    cur = g.pop('cur', None)

    if cur is not None:
        closeConnectionToDB()
