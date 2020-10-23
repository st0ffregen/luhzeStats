from flask import Flask
from flask import jsonify
from flask import Response
from flask import request
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
	con.set_character_set('utf8mb4')
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

@app.route('/json/rankingDefault', methods=['GET'])
def ranking():
	return readInGenericFile("rankingDefault")

@app.route('/json/rankingMonth', methods=['GET'])
def rankingMonth():
	return readInGenericFile("rankingMonth")

@app.route('/json/rankingYear', methods=['GET'])
def rankingYear():
	return readInGenericFile("rankingYear")

@app.route('/json/rankingTwoYears', methods=['GET'])
def rankingTwoYears():
	return readInGenericFile("rankingTwoYears")

@app.route('/json/rankingFiveYears', methods=['GET'])
def rankingFiveYears():
	return readInGenericFile("rankingFiveYears")

@app.route('/json/wordOccurence', methods=['GET'])
def wordOccurence():
	# read in word
	if 'word' in request.args:
		word = request.args['word'].upper()
		con = connectToDB()
		with con:
			cur = con.cursor()
			cur.execute('SELECT wholeTableName FROM createdTables')
			tableNames = cur.fetchall()
			#craft result with all table names and entries
			result = []
			for table in tableNames:
				#translate table name back to a date
				initQuarter = ((( - 1) // 3) + 1)  # gib quarter von 1 bis 4
				month = str((int(table[0][-1:]) * 3) -2)
				if int(month)<10:
					month = "0" + month
				year = table[0].split("e")[2][:4]
				date = year + "-" + month + "-01"

				# prepare statement here
				cur.execute('SELECT occurencePerWords, occurence FROM ' + table[0] + ' WHERE word = "' + word + '"') # so auf jeden fall nicht xD
				occurences = cur.fetchone()
				contentArray = []
				if occurences is None:  # das wort existiert nicht
					result.append({'table': date, 'occurencePerWords': 0, 'occurence': 0})
				else: # das wort existiert in der tabelle
					result.append({'table': date, 'occurencePerWords': occurences[0], 'occurence': occurences[1]})

			if len(result) == 0:
				return Response(json.dumps(result),  mimetype='application/json')
			else:
				return Response(json.dumps(result),  mimetype='application/json')
	else:
		return jsonify("Error. No word filed provided. Please specify a word")
	return jsonify("Error. No word filed provided. Please specify a word")



if(__name__ == "__main__"):
	app.run(host="0.0.0.0",port="5001",debug=True)

