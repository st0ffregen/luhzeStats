#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import sqlite3 as lite
import operator
import json
import datetime
import MySQLdb


minRessort=1
fileArray = []



def connectToDB():
	try: 
		con = MySQLdb.connect(
			host='db', # was muss hier fuer ein host???
			db='luhze',
			user='admin',
			passwd='test'
		)
		con.set_character_set('utf8')
		return con
	except MySQLdb.Error as e:
	   	print(f"Error connecting to MariaDB Platform: {e}")
		
	return 1

def mainFunc():
	print("start analyzing")
	print(datetime.datetime.now())
	con = connectToDB()

	with con:
		try:
			con.autocommit = False
			cur = con.cursor()
			minAuthor=selfCalibrieren(cur)
			fileArray.append([minAuthor,'minAuthor'])
			fileArray.append([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'date'])
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
		except MySQLdb.Error as e:
			print(f"Error connecting to MariaDB Platform: {e}")
			return 1
		else:
			writeToDB(cur,con)



def selfCalibrieren(cur):
	cur.execute('SELECT author, count(distinct Link) FROM articles GROUP BY author ORDER BY 2 DESC LIMIT 30')
	entries = cur.fetchall()
	minAuthor = entries[len(entries) - 1][1] #makes sure that always 30 authors are shown
	print("minAuthor is: " + str(minAuthor))
	return minAuthor

def oldestArticle(cur,filename):
	cur.execute('SELECT MIN(created) FROM articles')
	entries = cur.fetchall()
	fileArray.append([entries[0],filename])
	return entries[0]


def newestArticle(cur,filename):
	cur.execute('SELECT MAX(created) FROM articles')
	entries = cur.fetchall()
	fileArray.append([entries[0],filename])
	return entries[0]

def articlesTimeline(cur,filename):
	cur.execute('SELECT created FROM articles GROUP BY Link')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		arr.append(e[0].strftime('%Y-%m-%d'))
	fileArray.append([ arr[::-1], filename])
	return 0

def activeMembers(cur,filename):
	cur.execute('SELECT author FROM articles GROUP BY Author')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		cur.execute('SELECT created FROM articles WHERE author ="' + e[0] + '" GROUP BY link')
		dates = cur.fetchall()
		dateArray = []
		for d in dates:
			dateArray.append(d[0].strftime('%Y-%m-%d'))
		arr.append([e[0],dateArray])
	fileArray.append([ arr,filename])
	return 0 

def ressortTopList(cur,filename):
	cur.execute('SELECT ressort, count(distinct link) FROM articles GROUP BY ressort HAVING count(distinct link) >= ' + str(minRessort) + ' ORDER BY 2 DESC')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		arr.append([e[0],e[1]])
	fileArray.append([arr,filename])
	return 0

def ressortArticlesTimeline(cur,filename):
	cur.execute('SELECT ressort FROM articles GROUP BY ressort HAVING count(distinct link) >= ' + str(minRessort))
	entries = cur.fetchall()
	arr = []
	for e in entries:
		cur.execute('SELECT created FROM articles WHERE ressort ="' + e[0] + '" GROUP BY link')
		dates = cur.fetchall()
		dateArray = []
		for d in dates:
			dateArray.append(d[0].strftime('%Y-%m-%d'))
		arr.append([e[0],dateArray[::-1]])
	fileArray.append([ arr,filename])
	return 0 

def topAuthorsPerRessort(cur,filename):
	entries = cur.fetchall()
	arr = []
	for e in entries:
		cur.execute('SELECT author,count(distinct link) FROM articles WHERE ressort="' + e[0] + '" GROUP BY author HAVING count(link) >= 5 ORDER BY 2 DESC')
		arr.append([e[0],cur.fetchall()[:3]])
	fileArray.append([arr,filename])
	return 0

def timelineDataMin(cur,filename,minAuthor):
	cur.execute('SELECT author, MIN(created), MAX(created) FROM articles GROUP BY author HAVING count(distinct link) >= ' + str(minAuthor) + ' ORDER BY count(distinct link) DESC')
	entries = cur.fetchall()
	fileArray.append([entries, filename])
	return 0

def mostArticlesPerTime(cur,filename,minAuthor):
	cur.execute('SELECT author, ROUND(((DATEDIFF(MAX(created),MIN(created)))/count(distinct link)),1) FROM articles GROUP BY author HAVING count(distinct link) >= ' + str(minAuthor) + ' ORDER BY 2')
	entries = cur.fetchall()
	fileArray.append([entries,filename])
	return 0

def authorAverage(cur,filename,minAuthor):
	cur.execute('SELECT author FROM articles GROUP BY author HAVING count(distinct link) >= ' + str(minAuthor))
	entries = cur.fetchall()
	arr = {}
	for e in entries:
		cur.execute('SELECT "' + e[0] + '", ROUND(AVG(words)) FROM (SELECT wordcount as words FROM articles WHERE author="' + e[0] + '" GROUP BY link) as words')
		ent = cur.fetchall()
		arr[ent[0][0]] = ent[0][1]
	fileArray.append([sorted(arr.items(), key=operator.itemgetter(1))[::-1],filename])
	return 0

def averageCharactersPerDay(cur,filename,minAuthor):
	cur.execute('SELECT author,(DATEDIFF(MAX(created),MIN(created))) FROM articles GROUP BY author HAVING count(distinct link) >= ' + str(minAuthor) + ' ORDER BY 2')
	entries = cur.fetchall()
	arr = {}
	for e in entries:
		cur.execute('SELECT SUM(words) FROM (SELECT wordcount as words FROM articles WHERE author="' + e[0] + '" GROUP BY link) as words')
		res = cur.fetchall()
		arr[e[0]] = round(res[0][0]/(e[1]+1))
	fileArray.append([sorted(arr.items(), key=operator.itemgetter(1))[::-1],filename])
	return 0

def ressortAverage(cur,filename):
	cur.execute('SELECT ressort FROM articles GROUP BY ressort HAVING count(distinct link) >= ' + str(minRessort))
	entries = cur.fetchall()
	arr = {}
	for e in entries:
		cur.execute('SELECT "' + e[0] + '", ROUND(AVG(words)) FROM (SELECT wordcount as words FROM articles WHERE ressort="' + e[0] + '" GROUP BY link) as words')
		ent = cur.fetchall()
		arr[ent[0][0]] = ent[0][1]
	fileArray.append([sorted(arr.items(), key=operator.itemgetter(1))[::-1],filename])
	return 0

def authorTopList(cur,filename,minAuthor):
	cur.execute('SELECT author,count(distinct link) FROM articles GROUP BY author HAVING count(distinct link) >= ' + str(minAuthor) + ' ORDER BY 2 DESC')
	entries = cur.fetchall()
	fileArray.append([entries,filename])
	return 0

def ressortTimeline(cur,filename):
	cur.execute('SELECT ressort, MIN(created), MAX(created) FROM articles GROUP BY ressort ORDER BY count(distinct link) DESC')
	entries = cur.fetchall()
	fileArray.append([entries, filename])
	return 0

def writeToDB(cur,con):
	try:
		for file in fileArray:

			print("insertOrUpdate", [file[1],"{" + str(file[0]) + "}"])
			cur.callproc("insertOrUpdate", [file[1],"{" + str(file[0]) + "}"])
			#mit cursor.stored_results() results verarbeiten,falls gewünscht
	except MySQLdb.Error as e:
	   	print(f"Error inserting rows to MariaDB Platform: {e}")
	   	print("rollback")
	   	con.rollback() #rolled nur den letzten Eintrag back
	   	return 1
	else:
		print("commiting changes")
		con.commit()
		return 0

