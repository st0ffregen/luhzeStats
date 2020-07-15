from flask import Flask
import json
import MySQLdb

app = Flask(__name__)
path = "/usr/src/app/json/"


def connectToDB():
	con = MySQLdb.connect(
		host='db',
		db='luhze',
		user='admin',
		passwd='test'
	)
	con.set_character_set('utf8')
	return con

def readInGenericFile(filename):
	
	con = connectToDB()
	with con:
		cur = con.cursor()
		cur.execute('SELECT json FROM files WHERE filename="' + filename + '"')
		entries = cur.fetchall() #fetchone?
		if len(entries) < 1:
			print("no entries in db")
			return 1
		else:
			return entries[0]
	return 1


@app.route('/json/minAuthor')
def minAuthor():
	response = readInGenericFile("minAuthor")
	if response == 1:
		return "{NaN}"
	else:
		return readInGenericFile("minAuthor")


if(__name__ == "__main__"):
	app.run(host="0.0.0.0",port="8000",debug=True)

