#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import sqlite3 as lite
import operator
import json
from datetime import datetime

###########
#tickets
#in der ressort articles financial function wird der date array sortiert nachdem er zum string gemacht wurde, wonach wir da noch sortiert?
#rework timeline, einfach dummer redundanter return
###########


articleMin = 10
ressortMin = 14 #so that campus, kommentar und service is included

def getAllLegitAuthors():

	con = lite.connect('articles.db',detect_types=lite.PARSE_DECLTYPES)

	with con:
		cur = con.cursor()

		arrNamesTmp = {}	
		arrNames = {}

		cur.execute('SELECT Author, Created, Wordcount, Ressort FROM Articles')
		entries = cur.fetchall()

		#writes all authors to the list
		for entry in entries:
			e = entry[0].split(',')[:-1]
			
			if len(e) == 1 and e[0] not in arrNamesTmp:
				arrNamesTmp[e[0]] = 0
			#handle case cause there might be people who have only written articles in collab with others
			else:
				for name in e:
					if name not in arrNamesTmp:
						arrNamesTmp[name] = 0



		#get article count
		for entry in entries:
			e = entry[0].split(',')[:-1]
			if len(e) == 1:
				arrNamesTmp[e[0]] = arrNamesTmp[e[0]] + 1
			else:
				for name in e:
					arrNamesTmp[name] = arrNamesTmp[name] +1



		#filter people who have less than 10 articles
		for author in arrNamesTmp.keys():
			if arrNamesTmp[author] >= articleMin:
				arrNames[author] = arrNamesTmp[author]

		return [cur, entries, arrNames]

def activeMembers(var,file):
	

	con = lite.connect('articles.db',detect_types=lite.PARSE_DECLTYPES)

	with con:
		cur = con.cursor()

			
		arrNames = {}
		activeMembers = []

		cur.execute('SELECT Author, Created FROM Articles')
		entries = cur.fetchall()

		#writes all authors to the list
		for entry in entries:
			e = entry[0].split(',')[:-1]
			
			if len(e) == 1 and e[0] not in arrNames:
				arrNames[e[0]] = []
			#handle case cause there might be people who have only written articles in collab with others
			else:
				for name in e:
					if name not in arrNames:
						arrNames[name] = []
		
		for name in arrNames.keys():
			dateArray = []
			for entry in entries:
				if name in entry[0]:
					dateArray.append(entry[1].strftime('%Y-%m-%d'))
			activeMembers.append([name,dateArray])

		writeToJSON(var, activeMembers, file)




def articlesFinancial(var,file):

	
	con = lite.connect('articles.db',detect_types=lite.PARSE_DECLTYPES)

	with con:
		cur = con.cursor()

		dateArray = []
		

		cur.execute('SELECT Created FROM Articles')
		entries = cur.fetchall()

		entries.sort()

		for entry in entries[::-1]:
			dateArray.append(entry[0].strftime('%Y-%m-%d'))

		writeToJSON(var,dateArray,file)



def ressortArticlesFinancial(var,file):

	con = lite.connect('articles.db',detect_types=lite.PARSE_DECLTYPES)

	with con:
		cur = con.cursor()

		arrNamesTmp = {}	
		arrNames = {}
		ressortsWithDate=[]
		

		cur.execute('SELECT Ressorts, Created FROM Articles')
		entries = cur.fetchall()

		#writes all ressorts to the list
		for entry in entries:
			e = entry[0].split(',')[:-1]
			
			if len(e) == 1 and e[0] not in arrNamesTmp:
				arrNamesTmp[e[0]] = 0
			#handle case cause there might be ressorts which have only articles in collab with others (probably not)
			else:
				for name in e:
					if name not in arrNamesTmp:
						arrNamesTmp[name] = 0


		#get article count
		for entry in entries:
			e = entry[0].split(',')[:-1]
			if len(e) == 1:
				arrNamesTmp[e[0]] = arrNamesTmp[e[0]] + 1
			else:
				for name in e:
					arrNamesTmp[name] = arrNamesTmp[name] + 1


		#filter ressorts which have less than 14 articles
		for author in arrNamesTmp.keys():
			if arrNamesTmp[author] >= ressortMin:
				arrNames[author] = arrNamesTmp[author]

		
		
		for ressort in arrNames:

			dates = []
			for entry in entries:
				if ressort in entry[0]:
					dates.append(entry[1].strftime('%Y-%m-%d'))
			dates.sort() #nicht sicher wonach hier sortiert wird
			ressortsWithDate.append([ressort,dates[::-1]])



		writeToJSON(var,ressortsWithDate,file)





def topAuthorsPerRessort(var,file):



	values = mostArticleCountPerRessort("","")  #returns [[Ressorts, Wordcount, Author], [Ressort, articleCount]]
	entries = values[0]
	ressortNames = values[1]
	arrNames = getAllLegitAuthors()[2]
	returnArray =[]
	print("topAuthorsPerRessort")

	for ressort in ressortNames.keys():

		ressortAuthorsArray = {}

		for name in arrNames.keys():
			ressortAuthorsArray[name] = 0
		

		
		for entry in entries:
			e = entry[2].split(',')[:-1]
			if len(e) == 1 and e[0] in ressortAuthorsArray and ressort in entry[0]:
				ressortAuthorsArray[e[0]] += 1
			elif ressort in entry[0]:
				for name in e:
					if name in ressortAuthorsArray:
						ressortAuthorsArray[name] += 1


		#filter top five
		sortedArray = sorted(ressortAuthorsArray.items(), key=operator.itemgetter(1))[::-1][:3] #only include best three
		for name in sorted(sortedArray,reverse=True): #sort it for deleting safly
			if name[1] <= 5:
				sortedArray.remove(name)


		returnArray.append([ressort, sortedArray])


	writeToJSON(var,returnArray,file)
	return returnArray

def timeline(var,file):

	values = getAllLegitAuthors()
	arrNames = values[2]
	cur = values[0]
	allDatasets = []

	for author in arrNames:
		cur.execute('SELECT Created FROM Articles WHERE Author LIKE "%' + author + '%"')
		entries = cur.fetchall()
		finalEntries = []
		for entry in entries:
			finalEntries.append([author, entry[0].strftime('%Y-%m-%d')])
		allDatasets.append(finalEntries)

	writeToJSON(var,allDatasets,file)

def ressortTimeline(var,file):

	con = lite.connect('articles.db',detect_types=lite.PARSE_DECLTYPES)

	with con:
		cur = con.cursor()

		arrNames = {}
		ressortsWithDate=[]
		

		cur.execute('SELECT Ressorts, Created FROM Articles')
		entries = cur.fetchall()

		#writes all ressorts to the list
		for entry in entries:
			e = entry[0].split(',')[:-1]
			
			if len(e) == 1 and e[0] not in arrNames:
				arrNames[e[0]] = 0
			#handle case cause there might be ressorts which have only articles in collab with others (probably not)
			else:
				for name in e:
					if name not in arrNames:
						arrNames[name] = 0
		
		#get oldest article
		oldestArticle = {}
		for ressort in arrNames.keys():
			firstArticle = [ressort, '2999-12-12']
			for entry in entries:
				if ressort in entry[0] and datetime.strptime(str(firstArticle[1]), '%Y-%m-%d') > datetime.strptime(str(entry[1]), '%Y-%m-%d'):
					firstArticle = entry
			oldestArticle[ressort] = firstArticle[1]

		#get newest article 
		newestArticle = {}
		for ressort in arrNames.keys():
			firstArticle=[ressort,'0001-12-12']
			for entry in entries:

				if ressort in entry[0] and datetime.strptime(str(firstArticle[1]), '%Y-%m-%d') < datetime.strptime(str(entry[1]), '%Y-%m-%d'):
					firstArticle = entry

			newestArticle[ressort] = firstArticle[1]


		#put them both to array
		returnArray = []
		for ressort in arrNames:
			returnArray.append([ressort, oldestArticle[ressort].strftime('%Y-%m-%d'),newestArticle[ressort].strftime('%Y-%m-%d')])

		writeToJSON(var,returnArray,file)
		return returnArray

		




def timelineMin(var,file):

		values = getAllLegitAuthors()
		arrNames = values[2]
		entries = values[1]

		#determine start and end of authors career
		#get oldest article 
		oldestArticle = {}
		for author in arrNames.keys():
			firstArticle=[author,'2999-12-12']
			for entry in entries:

				if author in entry[0] and datetime.strptime(str(firstArticle[1]), '%Y-%m-%d') > datetime.strptime(str(entry[1]), '%Y-%m-%d'):
					firstArticle = entry

			oldestArticle[author] = firstArticle[1]

		#get newest article 
		newestArticle = {}
		for author in arrNames.keys():
			firstArticle=[author,'0001-12-12']
			for entry in entries:

				if author in entry[0] and datetime.strptime(str(firstArticle[1]), '%Y-%m-%d') < datetime.strptime(str(entry[1]), '%Y-%m-%d'):
					firstArticle = entry

			newestArticle[author] = firstArticle[1]


		#put them both to array
		returnArray = []
		for author in arrNames:
			returnArray.append([author, oldestArticle[author].strftime('%Y-%m-%d'), newestArticle[author].strftime('%Y-%m-%d')])

		writeToJSON(var,returnArray,file)
		return returnArray



def bestArticlesPerTime(var,file):

		values = getAllLegitAuthors()
		arrNames = values[2]
		entries = values[1]
		
		
		#determine start and end of authors career
		#get oldest article 
		oldestArticle = {}
		for author in arrNames.keys():
			firstArticle=[author,'2999-12-12']
			for entry in entries:
				e = entry[0].split(',')[:-1]

				if author in e and datetime.strptime(str(firstArticle[1]), '%Y-%m-%d') > datetime.strptime(str(entry[1]), '%Y-%m-%d'):
					firstArticle = entry

			oldestArticle[author] = firstArticle[1]

		#get newest article 
		newestArticle = {}
		for author in arrNames.keys():
			firstArticle=[author,'0001-12-12']
			for entry in entries:
				e = entry[0].split(',')[:-1]

				if author in e and datetime.strptime(str(firstArticle[1]), '%Y-%m-%d') < datetime.strptime(str(entry[1]), '%Y-%m-%d'):
					firstArticle = entry

			newestArticle[author] = firstArticle[1]

		#calculate amount of days per author
		daysAuthors = {}
		for author in oldestArticle.keys():
			daysAuthors[author] = (newestArticle[author]-oldestArticle[author]).days+1 # add one so that authors with only one article have a duration of 1
		
		

		returnArray = {}
		for author in arrNames.keys():
			#get how many days for one article avarage
			returnArray[author] = round(daysAuthors[author]/arrNames[author],1)
		arr=sorted(returnArray.items(), key=operator.itemgetter(1))


		writeToJSON(var,arr,file)
		return daysAuthors
		
def mostWordCount(var,file):


		values = getAllLegitAuthors()
		arrNames = values[2]
		entries = values[1]

		wordCountArray = {}
		for author in arrNames.keys():
			wordcount = 0
			for entry in entries:
				e = entry[0].split(',')[:-1]
				if author in e:
					wordcount = wordcount + entry[2]

			wordCountArray[author] = wordcount

		writeToJSON(var,sorted(wordCountArray.items(), key=operator.itemgetter(1))[::-1],file)
		return wordCountArray

def averageCharactersPerDay(var,file):
	#how much the authors write per day

	returnArray={}
	daysAuthors = bestArticlesPerTime("","")
	wordCountArray = mostWordCount("","")

	for author in daysAuthors.keys():
		returnArray[author] = round(wordCountArray[author]/daysAuthors[author])

	
	writeToJSON(var,sorted(returnArray.items(), key=operator.itemgetter(1))[::-1],file)
	return 0

def averageWordcountPerAuthor(var,file):

		values = getAllLegitAuthors()
		arrNames = values[2]
		entries = values[1]

		wordCountArray = {}
		for author in arrNames.keys():
			wordcount = 0
			for entry in entries:
				e = entry[0].split(',')[:-1]
				if author in e:
					wordcount = wordcount + entry[2]

			wordCountArray[author] = wordcount

		returnArray = {}
		for author in wordCountArray.keys():
			returnArray[author] = round(wordCountArray[author]/arrNames[author])

		writeToJSON(var,sorted(returnArray.items(), key=operator.itemgetter(1))[::-1],file)
		return 0

def mostArticleCountPerRessort(var,file):



	con = lite.connect('articles.db',detect_types=lite.PARSE_DECLTYPES)

	with con:
		cur = con.cursor()

		arrNamesTmp = {}	
		arrNames = {}

		cur.execute('SELECT Ressorts, Wordcount, Author FROM Articles')
		entries = cur.fetchall()

		#writes all ressorts to the list
		for entry in entries:
			e = entry[0].split(',')[:-1]
			
			if len(e) == 1 and e[0] not in arrNamesTmp:
				arrNamesTmp[e[0]] = 0
			#handle case cause there might be ressorts which have only articles in collab with others (probably not)
			else:
				for name in e:
					if name not in arrNamesTmp:
						arrNamesTmp[name] = 0





		#get article count
		for entry in entries:
			e = entry[0].split(',')[:-1]
			if len(e) == 1:
				arrNamesTmp[e[0]] = arrNamesTmp[e[0]] + 1
			else:
				for name in e:
					arrNamesTmp[name] = arrNamesTmp[name] + 1


		#filter ressorts which have less than 14 articles
		for author in arrNamesTmp.keys():
			if arrNamesTmp[author] >= ressortMin:
				arrNames[author] = arrNamesTmp[author]

		writeToJSON(var, sorted(arrNames.items(), key=operator.itemgetter(1))[::-1],file)
		return ([entries,arrNames])

	


def averageWordcountPerRessort(var, file):

		values = mostArticleCountPerRessort("","")
		arrNames = values[1]
		entries = values[0]

		ressortArray={}
		returnArray = {}


		for ressort in arrNames.keys():
			ressortArray[ressort] = 0
			for entry in entries:
				if ressort in entry[0]:
					ressortArray[ressort] += entry[1]


		for ressort in ressortArray.keys():
			returnArray[ressort] = round(ressortArray[ressort]/arrNames[ressort])

		writeToJSON(var, sorted(returnArray.items(), key=operator.itemgetter(1))[::-1],file)



def topListArticlesPerAuthor(var, file):

	arrNames = getAllLegitAuthors()[2];

	sortedNames = sorted(arrNames.items(), key=operator.itemgetter(1))
	
	writeToJSON(var, sortedNames[::-1],file)


	return 0

def writeToJSON(var, dict,file):

	if var != "" and file != "":
		print("write to file: "  + file)
		print("var " + var + " = " +  json.dumps(dict) + ";")
		f = open(file,"w")
		f.write("var " + var + " = " +  json.dumps(dict) + ";")
		f.close()
	return 0

#topListArticlesPerAuthor("list", "authorTopList.js")
#averageWordcountPerRessort("ressortAverage","ressortAverage.js")
#mostArticleCountPerRessort("ressortTopList","ressortTopList.js")
#averageWordcountPerAuthor("authorAverage","authorAverage.js")
#averageCharactersPerDay("averageCharactersPerDay","averageCharactersPerDay.js")
#mostWordCount("mostWordCount","mostWordCount.js")
#bestArticlesPerTime("mostArticlesPerTime","mostArticlesPerTime.js")
#timelineMin("timelineDataMin","timelineDataMin.js")
#ressortTimeline("ressortTimeline","ressortTimeline.js")
#timeline("authorTimeline","timelineData.js") needs a rework
#topAuthorsPerRessort("topAuthorsPerRessort","topAuthorsPerRessort.js")
#articlesFinancial("articlesTimeline","articlesTimeline.js")
#ressortArticlesFinancial("ressortArticlesTimeline","ressortArticlesTimeline.js")
#activeMembers("activeMembers","activeMembers.js")
print(getAllLegitAuthors()[2])