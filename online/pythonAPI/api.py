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
		result = []

		with con:

			cur = con.cursor()
			if "+++" in word:
				wordsToFetchArray = word.split("+++")

				for w in wordsToFetchArray:

					if w == "": #passiert gerade dann wenn nach dem +++ nichts eingegeben wurde
						continue

					cur.execute(
						'SELECT yearAndQuarter, occurencePerWords, occurence FROM wordOccurenceOverTheQuarters WHERE word = %s',
						[w])
					occurences = cur.fetchall()

					if occurences is None or len(occurences) == 0:
						continue

					for entry in occurences:
						if len(result) > 1:
							#wenn es den result array schon mit werten gibt search in result array for same yearAndQuarter
							# wenn aber das spezifische yearAndQuarter noch nicht gibt wird es neu hinzugefügt -> found variable
							found = False
							for yearAndQuarterEntry in result:
								if yearAndQuarterEntry['yearAndQuarter'] == entry[0]:
									found = True
									yearAndQuarterEntry['occurencePerWords'] += entry[1] # aufaddieren
									yearAndQuarterEntry['occurence'] += entry[2] # aufaddieren
							if not found:
								# muss dann im frontend nach datum sortiert werden
								result.append(
									{'yearAndQuarter': entry[0], 'occurencePerWords': entry[1], 'occurence': entry[2]})
						else:
							result.append(
								{'yearAndQuarter': entry[0], 'occurencePerWords': entry[1], 'occurence': entry[2]})

			else:

				cur.execute('SELECT yearAndQuarter, occurencePerWords, occurence FROM wordOccurenceOverTheQuarters WHERE word = %s', [word])
				occurences = cur.fetchall()

				if occurences is None or len(occurences) == 0:
					return jsonify("Error. The word " + word + " does not exist.")

				for entry in occurences:
					result.append({'yearAndQuarter': entry[0], 'occurencePerWords': entry[1], 'occurence': entry[2]})

			return Response(json.dumps(sorted(result, key=lambda x: x['yearAndQuarter'])),  mimetype='application/json')
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
			cur.execute('SELECT word, occurencePerWords, occurence, totalWordCount FROM totalWordOccurence WHERE BINARY word like CONCAT(%s,\'%%\') order by occurencePerWords desc limit 5', [ecscapeSpecialCharacters(word)]) # escape das % mit einem weiteren %
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


def ecscapeSpecialCharacters(wordToEscapeCharactersIn):
    # die methode escapet im string special charcters in der mysql like funktion
    # das ist % welches wildcard fuer mehrere zeichen ist und _ was fuer ein zeichen ist
    specialCharactersInMySQL = ['_', '%']
    if wordToEscapeCharactersIn is not None and wordToEscapeCharactersIn != "":
        return wordToEscapeCharactersIn.replace("_","\_").replace("%", "\%")

if __name__ == "__main__":
	app.run(host="0.0.0.0", port="5001", debug=True)

