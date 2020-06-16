#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import sqlite3 as lite
import operator
import json
import datetime


minRessort=14

#aufm pi liegt noch ein direc var damit das funst

def mainFunc():

	con = lite.connect('articles.db',detect_types=lite.PARSE_DECLTYPES)

	with con:
		cur = con.cursor()
		minAuthor=selfCalibrieren(cur)
		writeToJSON('minAuthor',[minAuthor],'minAuthor.js')
		writeToJSON('date',[datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],'date.js')
		articlesTimeline(cur, 'articlesTimeline','articlesTimeline.js')
		activeMembers(cur, 'activeMembers','activeMembers.js')
		ressortTopList(cur,'ressortTopList','ressortTopList.js')
		ressortArticlesTimeline(cur,'ressortArticlesTimeline','ressortArticlesTimeline.js')
		topAuthorsPerRessort(cur,'topAuthorsPerRessort','topAuthorsPerRessort.js')
		timelineDataMin(cur,'timelineDataMin','timelineDataMin.js',minAuthor)
		mostArticlesPerTime(cur,'mostArticlesPerTime','mostArticlesPerTime.js',minAuthor)
		authorAverage(cur,'authorAverage','authorAverage.js',minAuthor)
		averageCharactersPerDay(cur,'averageCharactersPerDay','averageCharactersPerDay.js',minAuthor)
		ressortAverage(cur,'ressortAverage','ressortAverage.js')
		authorTopList(cur,'list','authorTopList.js',minAuthor)
		ressortTimeline(cur,'ressortTimeline','ressortTimeline.js')
		oldestArticle(cur,'oldestArticle','oldestArticle.js')
		newestArticle(cur,'newestArticle','newestArticle.js')
		return 0

def selfCalibrieren(cur):
	cur.execute('SELECT Author, count(distinct Link) FROM Articles GROUP BY Author ORDER BY 2 DESC')
	entries = cur.fetchall()
	minAuthor = entries[29][1] #makes sure that always 30 authors are shown
	print("minAuthor is: " + str(minAuthor))
	return minAuthor

def oldestArticle(cur,var,file):
	cur.execute('SELECT MIN(Created) FROM Articles')
	entries = cur.fetchall()
	writeToJSON(var,entries[0],file)
	return entries[0]


def newestArticle(cur,var,file):
	cur.execute('SELECT MAX(Created) FROM Articles')
	entries = cur.fetchall()
	writeToJSON(var,entries[0],file)
	return entries[0]

def articlesTimeline(cur,var,file):
	cur.execute('SELECT Created FROM Articles GROUP BY Link')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		arr.append(e[0].strftime('%Y-%m-%d'))
	writeToJSON(var, arr[::-1], file)
	return 0

def activeMembers(cur,var,file):
	cur.execute('SELECT Author FROM Articles GROUP BY Author')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		cur.execute('SELECT Created FROM Articles WHERE Author ="' + e[0] + '" GROUP BY link')
		dates = cur.fetchall()
		dateArray = []
		for d in dates:
			dateArray.append(d[0].strftime('%Y-%m-%d'))
		arr.append([e[0],dateArray])
	writeToJSON(var, arr,file)
	return 0 

def ressortTopList(cur,var,file):
	cur.execute('SELECT Ressorts, count(distinct link) FROM Articles GROUP BY Ressorts HAVING count(distinct link)>=' + str(minRessort) + ' ORDER BY 2 DESC')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		arr.append([e[0],e[1]])
	writeToJSON(var,arr,file)
	return 0

def ressortArticlesTimeline(cur,var,file):
	cur.execute('SELECT Ressorts FROM Articles GROUP BY Ressorts HAVING count(distinct link)>=' + str(minRessort))
	entries = cur.fetchall()
	arr = []
	for e in entries:
		cur.execute('SELECT Created FROM Articles WHERE Ressorts ="' + e[0] + '" GROUP BY link')
		dates = cur.fetchall()
		dateArray = []
		for d in dates:
			dateArray.append(d[0].strftime('%Y-%m-%d'))
		arr.append([e[0],dateArray[::-1]])
	writeToJSON(var, arr,file)
	return 0 

def topAuthorsPerRessort(cur,var,file):
	cur.execute('SELECT Ressorts FROM Articles GROUP BY Ressorts HAVING count(distinct link)>=' + str(minRessort))
	entries = cur.fetchall()
	arr = []
	for e in entries:
		cur.execute('SELECT Author,count(distinct link) FROM Articles WHERE Ressorts="' + e[0] + '" GROUP BY Author HAVING count(link)>=5 ORDER BY 2 DESC')
		arr.append([e[0],cur.fetchall()[:3]])
	writeToJSON(var,arr,file)
	return 0

def timelineDataMin(cur,var,file,minAuthor):
	cur.execute('SELECT Author, MIN(Created), MAX(Created) FROM Articles GROUP BY Author HAVING count(distinct link)>=' + str(minAuthor) + ' ORDER BY count(distinct link) DESC')
	entries = cur.fetchall()
	writeToJSON(var,entries, file)
	return 0

def mostArticlesPerTime(cur,var,file,minAuthor):
	cur.execute('SELECT Author, ROUND(((julianday(MAX(Created))-julianday(MIN(Created)))/count(distinct link)),1) FROM Articles GROUP BY Author HAVING count(distinct link)>=' + str(minAuthor) + ' ORDER BY 2')
	entries = cur.fetchall()
	writeToJSON(var,entries,file)
	return 0

def authorAverage(cur,var,file,minAuthor):
	cur.execute('SELECT Author FROM Articles GROUP BY Author HAVING count(distinct link)>=' + str(minAuthor))
	entries = cur.fetchall()
	arr = {}
	for e in entries:
		cur.execute('SELECT "' + e[0] + '", CAST(AVG(words) AS INT) FROM (SELECT Wordcount AS words FROM Articles WHERE Author="' + e[0] + '" GROUP BY Link)')
		ent = cur.fetchall()
		arr[ent[0][0]] = ent[0][1]
	writeToJSON(var,sorted(arr.items(), key=operator.itemgetter(1))[::-1],file)
	return 0

def averageCharactersPerDay(cur,var,file,minAuthor):
	cur.execute('SELECT Author,(julianday(MAX(Created))-julianday(MIN(Created))) FROM Articles GROUP BY Author HAVING count(distinct link)>=' + str(minAuthor) + ' ORDER BY 2')
	entries = cur.fetchall()
	arr = {}
	for e in entries:
		cur.execute('SELECT SUM(words) FROM (SELECT Wordcount AS words FROM Articles WHERE Author="' + e[0] + '" GROUP BY Link)')
		res = cur.fetchall()
		arr[e[0]] = round(res[0][0]/e[1])
	writeToJSON(var,sorted(arr.items(), key=operator.itemgetter(1))[::-1],file)
	return 0

def ressortAverage(cur,var,file):
	cur.execute('SELECT Ressorts FROM Articles GROUP BY Ressorts HAVING count(distinct link)>=' + str(minRessort))
	entries = cur.fetchall()
	arr = {}
	for e in entries:
		cur.execute('SELECT "' + e[0] + '", CAST(AVG(words) AS INT) FROM (SELECT Wordcount AS words FROM Articles WHERE Ressorts="' + e[0] + '" GROUP BY Link)')
		ent = cur.fetchall()
		arr[ent[0][0]] = ent[0][1]
	writeToJSON(var,sorted(arr.items(), key=operator.itemgetter(1))[::-1],file)
	return 0

def authorTopList(cur,var,file,minAuthor):
	cur.execute('SELECT Author,count(distinct link) FROM Articles GROUP BY Author HAVING count(distinct link)>=' + str(minAuthor) + ' ORDER BY 2 DESC')
	entries = cur.fetchall()
	writeToJSON(var,entries,file)
	return 0

def ressortTimeline(cur,var,file):
	cur.execute('SELECT Ressorts, MIN(Created), MAX(Created) FROM Articles GROUP BY Ressorts ORDER BY count(distinct link) DESC')
	entries = cur.fetchall()
	writeToJSON(var,entries, file)
	return 0

def writeToJSON(var, dict,file):

	if var != "" and file != "":
		print("write to file: "  + file)
		print("var " + var + " = " +  json.dumps(dict) + ";")
		f = open(file,"w")
		f.write("var " + var + " = " +  json.dumps(dict) + ";")
		f.close()
	return 0


mainFunc()