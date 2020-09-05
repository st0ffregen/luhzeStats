#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3 as lite
from urllib.request import urlopen
import string
import sys
import os
from bs4 import BeautifulSoup
import MySQLdb
from datetime import datetime
import traceback
import analyzeLuhze



directory = "/home/stoffregen/Documents/luhze/archive/"
maxPageCount = 102 # so many pages are currently on luhze.de 101
web = "https://www.luhze.de/page/"

sqlStatements = []


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

def executeSQL(sqlArray, cur, con):
	
	if len(sqlArray) > 0:
		with cur:
			try:
				for statement in sqlArray:
					#print(statement[0])
					#print(statement[1])
					cur.execute(statement[0],statement[1])

				con.commit()
				cur.close()
				return 0
			except:
				print("error while inserting sql statements")
				print("exiting")
				cur.close()
				print(sys.exc_info())
				return 1

	else:
		print("nothing to write to db")
		cur.close()
		return 1
		



def scrapeWebsite(con):


	if con == 1:
		return 1
	try:
	#cur.execute("CREATE TABLE articles(Id Integer PRIMARY KEY, Link TEXT, Title TEXT, Author TEXT, Ressorts TEXT, Created DATE, Wordcount INTEGER)")
		cur = con.cursor()
			
		for i in range(1,4)[::-1]: #3 as a random number to start looking for new articles
			print("reading page " + str(i))
			site = None
			
			try:
				site = urlopen(web + str(i)).read()
			except:
				print("Cannot connect to " + web + str(i))
				print(sys.exc_info())

			soup = BeautifulSoup(site, 'html.parser')

			try:
				articles = soup.find_all('article')


				for x in articles[::-1]:
					link = x.find("a")['href']
					#sometimes wordpress provides another format

					print(link)
					#determine if link is already in db
					cur.execute('SELECT * FROM articles WHERE Link="' + link + '"')
					entries = cur.fetchall() 
					isIn=False
					if len(entries) > 0:
						print("articles is already in db")
						isIn=True

					# I have to update on wordcount or other stuff because of livetickers
						

					articlesite = urlopen(link).read()
					soupArticle = BeautifulSoup(articlesite, 'html.parser')
					# find title
					try:
						title = soupArticle.find("h2", {'class':'titleStyle'}).string
						print("title: " + title)
					except:
						print("title not found")
						title =""
						print(sys.exc_info())

					# find authors
					try:
						div = soupArticle.find("div",{'class': 'authorStyle'})
						authors = div.find_all("a")
						#might be several authors
						authorsString = []
						for a in authors:
							authorsString.append(a.string)
						print("author: ")
						print(authorsString)
					except:
						print("author not found")
						print(sys.exc_info())
						

					# find ressort

					try:
						div = soupArticle.find("div", {'class': 'articleFooter'})
						ressorts = div.find_all("a")
						#loop through all a to find a category
						ressortsString = []
						for r in ressorts:
							if "category" in r['href']:
								ressortsString.append(r.string)
						print("ressort: ")
						print(ressortsString)
					except:
						print("ressort not found")
						print(sys.exc_info())

					# find date
					try: 
						div = soupArticle.find("div", {'class': 'articleFooter'})
						tmpDate = div.find("span").string

						#translate date to timestamp
						split = tmpDate.split(" ")
						year = split[2]
						tmpMonth = split[1]
						tmpDay = split[0][:-1]
						if len(str(tmpDay)) == 1:
							day = "0" + tmpDay
						else:
							day = tmpDay
						#get the month
						if tmpMonth == "Januar":
							month = "01"
						elif tmpMonth == "Februar":
							month = "02"
						elif tmpMonth == "März":
							month = "03"
						elif tmpMonth == "April":
							month = "04"
						elif tmpMonth == "Mai":
							month = "05"
						elif tmpMonth == "Juni":
							month = "06"
						elif tmpMonth == "Juli":
							month = "07"
						elif tmpMonth == "August":
							month = "08"
						elif tmpMonth == "September":
							month = "09"
						elif tmpMonth == "Oktober":
							month = "10"
						elif tmpMonth == "November":
							month = "11"
						elif tmpMonth == "Dezember":
							month = "12"
						else:
							print("can't determine month!")

						date = year + "-" + month + "-" + day
						print("date: " + date)
					except:
						print("date not found")
						date=""
						print(sys.exc_info())


					#get wordcount
					wordcount = 0
					article = soupArticle.find("article", {'id':'mainArticle'})
					if article is None: #very old article
						allP = soupArticle.find("div", {'class':'field-content'}).find_all("p")
						for p in allP:
							wordcount = wordcount + len(p.get_text())
						print("wordcount: " + str(wordcount))
					elif article.find_all("div",{'class':'field-content'}) is not None: #old article but not so old
						allP = article.find_all("p")
						for p in allP:
							if p.get_text() is not None and p.get('id') is None:
								wordcount = wordcount + len(p.get_text())
						print("wordcount: " + str(wordcount))
					else:
						allP = article.find_all("p")
						for p in allP:
							if p.get_text() is not None and p.get('id') is None and 'contentWrapper' in p.find_parent('div')['class']:
								wordcount = wordcount + len(p.get_text())
						print("wordcount: " + str(wordcount))
					
					#print(entries[0])
					if isIn and (title != entries[0][2] or date != entries[0][5].strftime('%Y-%m-%d') or wordcount != entries[0][6]): # only checks first tupel
						#for setting a new author/ressort a whole update of the table is needed
						print("update rows")
						sqlStatements.append(['UPDATE articles SET Title=%s,Created=%s,Wordcount=%s WHERE Link=%s', [title,date,wordcount,link]])
					elif isIn == False: 
						print("insert rows")
						for a in authorsString:
							for r in ressortsString:
								sqlStatements.append(['INSERT INTO articles VALUES(%s,%s,%s,%s,%s,%s,%s)', [None,link,title, a, r, date, wordcount]])
					else:
						print("wont update nor insert")


			except Exception:
				traceback.print_exc()
				print("something went wrong")
				print(sys.exc_info())
				sys.exit(1)
				#return 1 irgendwie macht er trotzdem weiter

		
		## execute sql
		if executeSQL(sqlStatements, cur, con) == 0:
			print("inserting sql statements done")

		
	except MySQLdb.Error as e:
	   print(f"Error connecting to MariaDB Platform: {e}")
	   return 1

	#con.close() why??
	#print("start analyzing") own microservice now
	#os.system("python analyze.py")
	return 0


def main():
	print("starting gathering")
	#print(datetime.now())
	#con = connectToDB()
	#scrapeWebsite(con)
	return analyzeLuhze.mainFunc()
	


if __name__ == "__main__":
	main()
