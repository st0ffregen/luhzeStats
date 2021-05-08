import MySQLdb
import os
from flask import g
from flaskapi import app


def connectToDB():
    con = MySQLdb.connect(
        host=os.environ['DB_CONTAINER_NAME'],
        db=os.environ['MYSQL_DB'],
        user=os.environ['MYSQL_API_USER'],
        passwd=os.environ['MYSQL_API_PASSWORD']
    )
    con.set_character_set('utf8mb4')
    con.autocommit(False)
    return con


def closeConnectionToDB():
    g.con.close()
    g.cur.close()


@app.before_request
def before_request():
    if 'cur' not in g:
        g.con = connectToDB()
        g.cur = g.con.cursor()


@app.teardown_request
def teardown_request(exception):
    if hasattr('g', 'cur'):
        closeConnectionToDB()

