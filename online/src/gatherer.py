#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3 as lite
import urllib
import string
import sys
import os
from bs4 import BeautifulSoup

# date, ressort (maybe several), author (maybe several), title, wordcount

directory = "/home/stoffregen/Documents/luhze/archive/"
maxPageCount = 102 # so many pages are currently on luhze.de 101
web = "https://www.luhze.de/page/"




def checkDB():



	con = lite.connect('articles.db',detect_types=lite.PARSE_DECLTYPES)

	with con:
		cur = con.cursor()
		#cur.execute("CREATE TABLE Articles(Id Integer PRIMARY KEY, Link TEXT, Title TEXT, Author TEXT, Ressorts TEXT, Created DATE, Wordcount INTEGER)")
		
		
		for i in range(1,3)[::-1]: #3 as a random number to start looking for new articles
			print("reading page " + str(i))
			site = None
			
			try:
				site = urllib.urlopen(web + str(i)).read()
			except:
				print("Cannot connect to " + web + str(i))

			soup = BeautifulSoup(site, 'lxml')

			try:
				articles = soup.find_all('article')


				for x in articles[::-1]:
					link = x.find("a")['href']
					#sometimes wordpress provides another format

					print(link)
					#determine if link is already in db
					cur.execute('SELECT * FROM Articles WHERE Link="' + link + '"')
					entries = cur.fetchall()
					isIn=False
					if entries:
						print("articles is already in db")
						isIn=True

					# I have to update on wordcount or other stuff because of livetickers
						

					articleSite = urllib.urlopen(link).read()
					soupArticle = BeautifulSoup(articleSite, 'lxml')
					# find title
					try:
						title = soupArticle.find("h2", {'class':'titleStyle'}).string
						print("title: " + title)
					except:
						print("title not found")
						title =""

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

					# find date
					try: 
						div = soupArticle.find("div", {'class': 'articleFooter'})
						tmpDate = div.find("span").string

						#translate date to timestamp
						split = tmpDate.split(" ")
						year = split[2]
						tmpMonth = split[1].encode('utf-8')
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
					
					if isIn and (title != entries[0][2] or date != entries[0][5].strftime('%Y-%m-%d') or wordcount != entries[0][6]): # only checks first tupel
						#for setting a new author/ressort a whole update of the table is needed
						print("update rows")
						cur.execute('UPDATE Articles SET Title=?,Created=?,Wordcount=? WHERE Link=?', (title,date,wordcount,link))
					elif isIn == False: 
						print("insert rows")
						for a in authorsString:
							for r in ressortsString:
								cur.execute('INSERT INTO Articles VALUES(null,?,?,?,?,?,?)', (link,title, a, r, date, wordcount))
					else:
						print("wont update nor insert")


			except:
				print("something went wrong")
				print(sys.exc_info())
				return 1
	print("start analyzing")
	os.system("python analyze.py")
	return 0

checkDB()