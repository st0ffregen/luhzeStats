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
		cur.execute('SELECT json FROM files WHERE filename=%s', [filename])
		entries = cur.fetchone() #fetchone?
		
		if entries is None or len(entries) == 0:
			print("no entries in db for "  + filename)
			return jsonify("NaN")
		else:
			return Response(entries[0],  mimetype='application/json')

@app.route('/json/date',methods=['GET'])
def date():
	con = connectToDB()
	with con:
		cur = con.cursor()
		cur.execute('SELECT lastModifiedFiles from lastmodified')
		return Response(json.dumps({'date': cur.fetchone()[0].strftime('%Y-%m-%d %H:%M:%S')}), mimetype='application/json')


@app.route('/json/minAuthor',methods=['GET'])
def minAuthor():
	return readInGenericFile("minAuthor")

#@app.route('/json/date',methods=['GET'])
#def date():
#	return readInGenericFile("date")

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

@app.route('/json/minAndMaxYearAndQuarter', methods=['GET'])
def minYearAndQuarter():
	con = connectToDB()
	with con:
		cur = con.cursor()
		cur.execute('SELECT MIN(yearAndQuarter), MAX(yearAndQuarter) from wordOccurenceOverTheQuarters')
		res = cur.fetchone()
		return Response(json.dumps({'minYearAndQuarter': res[0], 'maxYearAndQuarter': res[1]}), mimetype='application/json')

@app.route('/json/maxYearAndQuarter', methods=['GET'])
def maxYearAndQuarter():
	con = connectToDB()
	with con:
		cur = con.cursor()
		cur.execute('SELECT MAX(yearAndQuarter) from wordOccurenceOverTheQuarters')
		return Response(json.dumps({'maxYearAndQuarter': cur.fetchone()[0]}), mimetype='application/json')

@app.route('/json/wordOccurence', methods=['GET'])
def wordOccurence():
	# read in word
	if 'word' in request.args:
		word = request.args['word'].upper()
		con = connectToDB()
		with con:

			cur = con.cursor()
			"""
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
				"""
			result = []
			# prepare statement here
			cur.execute('SELECT yearAndQuarter, occurencePerWords, occurence FROM wordOccurenceOverTheQuarters WHERE word = %s', [word])
			occurences = cur.fetchall()

			if occurences is None or len(occurences) == 0:
				return jsonify("Error. The word does not exists.")

			for entry in occurences:
				result.append({'yearAndQuarter': entry[0], 'occurencePerWords': entry[1], 'occurence': entry[2]})

			return Response(json.dumps(result),  mimetype='application/json')
	else:
		return jsonify("Error. No word provided. Please specify a word")


@app.route('/json/autocomplete', methods=['GET'])
def totalWordOccurence():
	# read in word
	if 'word' in request.args:
		word = request.args['word'].upper()
		con = connectToDB()
		with con:
			cur = con.cursor()
			cur.execute('SELECT word, occurencePerWords, occurence, totalWordCount FROM totalWordOccurence WHERE word like "' + word + '%" order by occurencePerWords desc limit 5')
			occ = cur.fetchall()

			result = []
			restOfResult = [] # gibt quasi ein first result das ist das wort was eigeben wurde, falls vorhanden in der db, nach oben zu schieben auch wenn es weniger treffer als andere hat

			for w in occ:
				if w[0] == word:
					result = [{'word': w[0], 'occurencePerWords': w[1], 'occurence': w[2]}]
				else:
					restOfResult.append({'word': w[0], 'occurencePerWords': w[1], 'occurence': w[2]})

			result.extend(restOfResult)
			cur.close()
			return Response(json.dumps(result),  mimetype='application/json')

	else:
		return jsonify("Error. No word filed provided. Please specify a word")


if __name__ == "__main__":
	app.run(host="0.0.0.0", port="5001", debug=True)

