#!/usr/bin/env python
# -*- coding: utf-8 -*-
import operator
import json
import datetime
import MySQLdb


minRessort=14
fileArray = []



def connectToDB():
	try: 
		con = MySQLdb.connect(
			host='db', # was muss hier fuer ein host???
			db='luhze',
			user='gatherer',
			passwd='testGatherer'
		)
		con.set_character_set('utf8mb4')
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
			fileArray.append([json.dumps({'minAuthor':minAuthor}),'minAuthor'])
			fileArray.append([json.dumps({'date':datetime.datetime.now()}, default = str),'date']) #treats datetime as string
			articlesTimeline(cur, 'articlesTimeline')
			activeMembers(cur, 'activeMembers')
			ressortTopList(cur,'ressortTopList')
			ressortArticlesTimeline(cur,'ressortArticlesTimeline')
			topAuthorsPerRessort(cur,'topAuthorsPerRessort')
			authorTimeline(cur,'authorTimeline',minAuthor)
			mostArticlesPerTime(cur,'mostArticlesPerTime',minAuthor)
			authorAverage(cur,'authorAverage',minAuthor)
			averageCharactersPerDay(cur,'averageCharactersPerDay',minAuthor)
			ressortAverage(cur,'ressortAverage')
			authorTopList(cur,'authorTopList',minAuthor)
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
	fileArray.append([json.dumps({'oldestArticle':entries[0][0]}, default = str),filename])
	return entries[0]


def newestArticle(cur,filename):
	cur.execute('SELECT MAX(created) FROM articles')
	entries = cur.fetchall()
	fileArray.append([json.dumps({'newestArticle':entries[0][0]}, default = str),filename])
	return entries[0]

def articlesTimeline(cur,filename):
	cur.execute('select cast(date_format(created,"%Y-%m-01") as date),count(distinct link) as countPerMonth from articles group by year(created),month(created) order by 1 asc')
	entries = cur.fetchall()
	fileArray.append([json.dumps(adjustFormatDate(entries)[::-1], default = str),filename])
	return 0

def activeMembers(cur,filename):
	cur.execute('SELECT author FROM articles GROUP BY author')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		cur.execute('SELECT created FROM articles WHERE author ="' + e[0] + '" GROUP BY link')
		dates = cur.fetchall()
		dateArray = []
		for d in dates:
			dateArray.append(d[0].strftime('%Y-%m-%d'))
		arr.append({"name": e[0],"articles":dateArray})
	fileArray.append([ json.dumps(arr),filename])
	return 0 

def ressortTopList(cur,filename):
	cur.execute('SELECT ressort, count(distinct link) FROM articles GROUP BY ressort HAVING count(distinct link) >= ' + str(minRessort) + ' ORDER BY 2 DESC')
	entries = cur.fetchall()
	fileArray.append([json.dumps(adjustFormatName(entries)),filename])
	return 0

def ressortArticlesTimeline(cur,filename):
	cur.execute('SELECT ressort, cast(date_format(created,"%Y-%m-01") as date),count(distinct link) as countPerMonth from articles where ressort in (select ressort from articles group by ressort having count(distinct link) >= ' + str(minRessort) + ') group by ressort, year(created), month(created)')
	entries = cur.fetchall()
	arr = [] # [{ressort: hopo, articles: [{date: some month, 5},{date: some month, 4}]}]
	ressort = entries[0][0] #set ressort to first in fetched list
	monthArray = []
	for e in entries:
		if ressort == e[0]:
			monthArray.append({"date": e[1], "count": e[2]})
			if e == entries[len(entries)-1]: #if it is last element
				arr.append({"ressort": ressort, "countPerMonth": monthArray})
		else:
			arr.append({"ressort": ressort, "countPerMonth": monthArray})
			monthArray = [{"date": e[1], "count": e[2]}]
			ressort = e[0]
			if e == entries[len(entries)-1]: #if it is last element
				arr.append({"ressort": ressort, "countPerMonth": monthArray})
		
	fileArray.append([json.dumps(arr, default = str),filename])
	return 0 

def topAuthorsPerRessort(cur,filename):
	cur.execute('SELECT ressort, author, count(link) as count from articles where ressort in (select ressort from articles group by ressort having count(distinct link) >= ' + str(minRessort) + ') group by ressort, author having count >= 5 order by 1 asc,3 desc')
	entries = cur.fetchall()
	arr = [] # should by filled with [{ressort: hopo, authors: [{name: theresa, count:5},{name: someone, count:2}]}] with min count >= 2 (in this example)
	ressort = entries[0][0] #set ressort to first in fetched list
	authorArray = []
	for e in entries:
		if ressort == e[0]:
			authorArray.append({"name": e[1], "count": e[2]})
			if e == entries[len(entries)-1]: #if it is last element
				arr.append({"ressort": ressort, "authors": authorArray[:3]})
		else:
			arr.append({"ressort": ressort, "authors": authorArray[:3]})
			authorArray = [{"name": e[1], "count": e[2]}]
			ressort = e[0]
			if e == entries[len(entries)-1]: #if it is last element
				arr.append({"ressort": ressort, "authors": authorArray[:3]})

	fileArray.append([json.dumps(arr),filename])
	return 0

def authorTimeline(cur,filename,minAuthor):
	cur.execute('SELECT author, MIN(created), MAX(created) FROM articles GROUP BY author HAVING count(distinct link) >= ' + str(minAuthor) + ' ORDER BY count(distinct link) DESC')
	entries = cur.fetchall()
	arr = [] #adjustFormat function only takes array with 2-tupel (2 entries in tupel)
	for e in entries:
		arr.append({"name":e[0],"min":e[1],"max":e[2]})
	fileArray.append([json.dumps(arr, default = str), filename])
	return 0

def mostArticlesPerTime(cur,filename,minAuthor):
	cur.execute('SELECT author, ROUND(((DATEDIFF(MAX(created),MIN(created)))/count(distinct link)),1) FROM articles GROUP BY author HAVING count(distinct link) >= ' + str(minAuthor) + ' ORDER BY 2')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		arr.append({'name':e[0],'count':str(e[1])})
	fileArray.append([json.dumps(arr),filename]) #decimal output from sql is not serializeable, cast to float
	return 0

def authorAverage(cur,filename,minAuthor):
	cur.execute('SELECT author, round(avg(wordcount)) as count from (select distinct(link), wordcount, author from articles where author in (select author from articles group by author having count(distinct link) >=' + str(minAuthor) + ')) as sub group by author order by count desc')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		arr.append({'name':e[0],'count':str(e[1])})
	fileArray.append([json.dumps(arr),filename])
	return 0

def averageCharactersPerDay(cur,filename,minAuthor):
	cur.execute('SELECT author, sum(wordcount) as count from (select distinct(link), wordcount, author from articles where author in (select author from articles group by author having count(distinct link) >=' + str(minAuthor) + ')) as sub group by author order by count desc')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		cur.execute('SELECT DATEDIFF(MAX(created),MIN(created))+1 as average from articles where author="' + e[0] + '"')
		res = cur.fetchone()
		arr.append({"name": e[0], "count": round(e[1]/res[0])})
	fileArray.append([json.dumps(sorted(arr, key=lambda x: x['count'], reverse=True)),filename])
	return 0

def ressortAverage(cur,filename):
	cur.execute('SELECT ressort, round(avg(wordcount)) as count from (select distinct(link), wordcount, ressort from articles where ressort in (select ressort from articles group by ressort having count(distinct link) >=' + str(minRessort) + ')) as sub group by ressort order by count desc')
	entries = cur.fetchall()
	arr = []
	for e in entries:
		arr.append({'name':e[0],'count':str(e[1])})
	fileArray.append([json.dumps(arr),filename])
	return 0

def authorTopList(cur,filename,minAuthor):
	cur.execute('SELECT author,count(distinct link) FROM articles GROUP BY author HAVING count(distinct link) >= ' + str(minAuthor) + ' ORDER BY 2 DESC')
	entries = cur.fetchall()
	fileArray.append([json.dumps(adjustFormatName(entries)),filename])
	return 0

def ressortTimeline(cur,filename):
	cur.execute('SELECT ressort, MIN(created), MAX(created) FROM articles GROUP BY ressort ORDER BY count(distinct link) DESC')
	entries = cur.fetchall()
	arr = [] #adjustFormat function only takes array with 2-tupel (2 entries in tupel)
	for e in entries:
		arr.append({"name":e[0],"min":e[1],"max":e[2]})
	fileArray.append([json.dumps(arr, default = str), filename])
	return 0

def writeToDB(cur,con):
	try:
		for file in fileArray:

			print("insertOrUpdate", [file[1],"{" + str(file[0]) + "}"])
			cur.callproc("insertOrUpdate", [file[1],str(file[0])])
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


def adjustFormatDate(entries):
	arr = []
	for e in entries:
		arr.append({'date':e[0],'count':e[1]})
	return arr

def adjustFormatName(entries):
	arr = []
	for e in entries:
		arr.append({'name':e[0],'count':e[1]})
	return arr