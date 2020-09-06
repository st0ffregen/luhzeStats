from flask import Flask
from flask import jsonify
from flask import Response
import MySQLdb
import json

app = Flask(__name__)
path = "/usr/src/app/json/"


def connectToDB():
	con = MySQLdb.connect(
		host='db',
		db='luhze',
		user='api',
		passwd='testApi'
	)
	con.set_character_set('utf8')
	print(con)
	return con

def readInGenericFile(filename):
	
	con = connectToDB()
	with con:
		cur = con.cursor()
		cur.execute('SELECT json FROM files WHERE filename="' + filename + '"') # durch prepared statement ersetzen , security
		entries = cur.fetchall() #fetchone?
		
		if len(entries) < 1:
			print("no entries in db for "  + filename)
			return jsonify("NaN")
		else:
			return Response(entries[0],  mimetype='application/json')
	return jsonify("NaN")


@app.route('/json/minAuthor',methods=['GET'])
def minAuthor():
	return readInGenericFile("minAuthor")

@app.route('/json/date',methods=['GET'])
def date():
	return readInGenericFile("date")

@app.route('/json/activeMembers',methods=['GET'])
def activeMembers():
	return readInGenericFile("activeMembers")

@app.route('/json/ressortTopList',methods=['GET'])
def ressortTopList():
	return readInGenericFile("ressortTopList")

@app.route('/json/ressortArticlesTimeline',methods=['GET'])
def ressortArticlesTimeline():
	return readInGenericFile("ressortArticlesTimeline")

@app.route('/json/topAuthorsPerRessort',methods=['GET'])
def topAuthorsPerRessort():
	return readInGenericFile("topAuthorsPerRessort")

@app.route('/json/authorTimeline',methods=['GET'])
def authorTimeline():
	return readInGenericFile("authorTimeline")

@app.route('/json/articlesTimeline',methods=['GET'])
def articlesTimeline():
	return readInGenericFile("articlesTimeline")

@app.route('/json/mostArticlesPerTime',methods=['GET'])
def mostArticlesPerTime():
	return readInGenericFile("mostArticlesPerTime")

@app.route('/json/authorAverage',methods=['GET'])
def authorAverage():
	return readInGenericFile("authorAverage")

@app.route('/json/averageCharactersPerDay',methods=['GET'])
def averageCharactersPerDay():
	return readInGenericFile("averageCharactersPerDay")

@app.route('/json/ressortAverage',methods=['GET'])
def ressortAverage():
	return readInGenericFile("ressortAverage")

@app.route('/json/authorTopList',methods=['GET'])
def authorTopList():
	return readInGenericFile("authorTopList")

@app.route('/json/ressortTimeline',methods=['GET'])
def ressortTimeline():
	return readInGenericFile("ressortTimeline")

@app.route('/json/oldestArticle',methods=['GET'])
def oldestArticle():
	return readInGenericFile("oldestArticle")

@app.route('/json/newestArticle',methods=['GET'])
def newestArticle():
	return readInGenericFile("newestArticle")
	


if(__name__ == "__main__"):
	app.run(host="0.0.0.0",port="5001",debug=True)

