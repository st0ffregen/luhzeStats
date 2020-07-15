#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import sqlite3 as lite
import operator
import json
import datetime
import MySQLdb


minRessort=14
fileArray = []




def mainFunc(con):

	with con:
		try:
			cur = con.cursor()
			minAuthor=selfCalibrieren(cur)
			fileArray.append(['minAuthor',[minAuthor]])
			fileArray.append(['date',[datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]])
			articlesTimeline(cur, 'articlesTimeline')
			activeMembers(cur, 'activeMembers')
			ressortTopList(cur,'ressortTopList')
			ressortArticlesTimeline(cur,'ressortArticlesTimeline')
			topAuthorsPerRessort(cur,'topAuthorsPerRessort')
			timelineDataMin(cur,'timelineDataMin',minAuthor)
			mostArticlesPerTime(cur,'mostArticlesPerTime',minAuthor)
			authorAverage(cur,'authorAverage',minAuthor)
			averageCharactersPerDay(cur,'averageCharactersPerDay',minAuthor)
			ressortAverage(cur,'ressortAverage')
			authorTopList(cur,'list',minAuthor)
			ressortTimeline(cur,'ressortTimeline')
			oldestArticle(cur,'oldestArticle')
			newestArticle(cur,'newestArticle')
			writeToDB(cur,con)
			return 0
		except MySQLdb.Error as e:
	   		print(f"Error connecting to MariaDB Platform: {e}")
	   		return 1



def selfCalibrieren(cur):
	cur.execute('SELECT Author, count(distinct Link) FROM articles GROUP BY Author ORDER BY 2 DESC')
	entries = cur.fetchall()
	print(entries)
	minAuthor = entries[29][1] #makes sure that always 30 authors are shown
	print("minAuthor is: " + str(minAuthor))
	return minAuthor

def oldestArticle(cur,filename):
	cur.execute('SELECT MIN(Created) FROM articles')
	entries = cur.fetchall()
	fileArray.append([entries[0],filename])
	return entries[0]


def newestArticle(cur,filename):
	cur.execute('SELECT MAX(Created) FROM articles')
	entries = cur.fetchall()
	fileArray.append([entries[0],filename])
	return entries[0]

def articlesTimeline(cur,filename):
	cur.execute('SELECT Created FROM articles GROUP BY Link')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		arr.append(e[0].strftime('%Y-%m-%d'))
	fileArray.append([ arr[::-1], filename])
	return 0

def activeMembers(cur,filename):
	cur.execute('SELECT Author FROM articles GROUP BY Author')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		cur.execute('SELECT Created FROM articles WHERE Author ="' + e[0] + '" GROUP BY link')
		dates = cur.fetchall()
		dateArray = []
		for d in dates:
			dateArray.append(d[0].strftime('%Y-%m-%d'))
		arr.append([e[0],dateArray])
	fileArray.append([ arr,filename])
	return 0 

def ressortTopList(cur,filename):
	cur.execute('SELECT Ressorts, count(distinct link) FROM articles GROUP BY Ressorts HAVING count(distinct link)>=' + str(minRessort) + ' ORDER BY 2 DESC')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		arr.append([e[0],e[1]])
	fileArray.append([arr,filename])
	return 0

def ressortArticlesTimeline(cur,filename):
	cur.execute('SELECT Ressorts FROM articles GROUP BY Ressorts HAVING count(distinct link)>=' + str(minRessort))
	entries = cur.fetchall()
	arr = []
	for e in entries:
		cur.execute('SELECT Created FROM articles WHERE Ressorts ="' + e[0] + '" GROUP BY link')
		dates = cur.fetchall()
		dateArray = []
		for d in dates:
			dateArray.append(d[0].strftime('%Y-%m-%d'))
		arr.append([e[0],dateArray[::-1]])
	fileArray.append([ arr,filename])
	return 0 

def topAuthorsPerRessort(cur,filename):
	cur.execute('SELECT Ressorts FROM articles GROUP BY Ressorts HAVING count(distinct link)>=' + str(minRessort))
	entries = cur.fetchall()
	arr = []
	for e in entries:
		cur.execute('SELECT Author,count(distinct link) FROM articles WHERE Ressorts="' + e[0] + '" GROUP BY Author HAVING count(link)>=5 ORDER BY 2 DESC')
		arr.append([e[0],cur.fetchall()[:3]])
	fileArray.append([arr,filename])
	return 0

def timelineDataMin(cur,filename,minAuthor):
	cur.execute('SELECT Author, MIN(Created), MAX(Created) FROM articles GROUP BY Author HAVING count(distinct link)>=' + str(minAuthor) + ' ORDER BY count(distinct link) DESC')
	entries = cur.fetchall()
	fileArray.append([entries, filename])
	return 0

def mostArticlesPerTime(cur,filename,minAuthor):
	cur.execute('SELECT Author, ROUND(((julianday(MAX(Created))-julianday(MIN(Created)))/count(distinct link)),1) FROM articles GROUP BY Author HAVING count(distinct link)>=' + str(minAuthor) + ' ORDER BY 2')
	entries = cur.fetchall()
	fileArray.append([entries,filename])
	return 0

def authorAverage(cur,filename,minAuthor):
	cur.execute('SELECT Author FROM articles GROUP BY Author HAVING count(distinct link)>=' + str(minAuthor))
	entries = cur.fetchall()
	arr = {}
	for e in entries:
		cur.execute('SELECT "' + e[0] + '", CAST(AVG(words) AS INT) FROM (SELECT Wordcount AS words FROM articles WHERE Author="' + e[0] + '" GROUP BY Link)')
		ent = cur.fetchall()
		arr[ent[0][0]] = ent[0][1]
	fileArray.append([sorted(arr.items(), key=operator.itemgetter(1))[::-1],filename])
	return 0

def averageCharactersPerDay(cur,filename,minAuthor):
	cur.execute('SELECT Author,(julianday(MAX(Created))-julianday(MIN(Created))) FROM articles GROUP BY Author HAVING count(distinct link)>=' + str(minAuthor) + ' ORDER BY 2')
	entries = cur.fetchall()
	arr = {}
	for e in entries:
		cur.execute('SELECT SUM(words) FROM (SELECT Wordcount AS words FROM articles WHERE Author="' + e[0] + '" GROUP BY Link)')
		res = cur.fetchall()
		arr[e[0]] = round(res[0][0]/e[1])
	fileArray.append([sorted(arr.items(), key=operator.itemgetter(1))[::-1],filename])
	return 0

def ressortAverage(cur,filename):
	cur.execute('SELECT Ressorts FROM articles GROUP BY Ressorts HAVING count(distinct link)>=' + str(minRessort))
	entries = cur.fetchall()
	arr = {}
	for e in entries:
		cur.execute('SELECT "' + e[0] + '", CAST(AVG(words) AS INT) FROM (SELECT Wordcount AS words FROM articles WHERE Ressorts="' + e[0] + '" GROUP BY Link)')
		ent = cur.fetchall()
		arr[ent[0][0]] = ent[0][1]
	fileArray.append([sorted(arr.items(), key=operator.itemgetter(1))[::-1],filename])
	return 0

def authorTopList(cur,filename,minAuthor):
	cur.execute('SELECT Author,count(distinct link) FROM articles GROUP BY Author HAVING count(distinct link)>=' + str(minAuthor) + ' ORDER BY 2 DESC')
	entries = cur.fetchall()
	fileArray.append([entries,filename])
	return 0

def ressortTimeline(cur,filename):
	cur.execute('SELECT Ressorts, MIN(Created), MAX(Created) FROM articles GROUP BY Ressorts ORDER BY count(distinct link) DESC')
	entries = cur.fetchall()
	fileArray.append([entries, filename])
	return 0

def writeToDB(cur,con):

	print("write to db")
	for file in fileArray:
		cur.callproc("insertOrUpdate", [None,"{" + file[1] + "}",file[0]])
	con.commit()
	return 0


mainFunc()