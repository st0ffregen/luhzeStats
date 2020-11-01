#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib.request import urlopen
from urllib import error
import string
import sys
import os
from bs4 import BeautifulSoup
import MySQLdb
from datetime import datetime
import traceback
import analyzeLuhze



directory = "/home/stoffregen/Documents/luhze/archive/"
maxPageCount = 106 # so many pages are currently on luhze.de 101
web = "https://www.luhze.de/page/"

sqlStatements = []


def connectToDB():
	try: 
		con = MySQLdb.connect(
			host='db', # was muss hier fuer ein host???
			db='luhze',
			user='gatherer',
			passwd='testGatherer'
		)
		con.set_character_set('utf8mb4')
		con.autocommit(False)
		return con
	except MySQLdb.Error as e:
		print(f"Error connecting to MariaDB Platform: {e}")
		print(sys.exc_info())
		sys.exit(1) #kann man eh stoppen, da constraints der db blockieren

def executeSQL(sqlArray, cur, con):

    if len(sqlArray) > 0:
        with cur:
            try:
                for statement in sqlArray:
                    #print(statement[0])
                    #print(statement[1])
                    cur.execute(statement[0],statement[1])
                print("commiting changes")
                con.commit()
                cur.close()
                return 0
            except MySQLdb.Error as e:
                print(f"Error while inserting sql statements: {e}")
                cur.close()
                print(sys.exc_info())
                sys.exit(1) #kann man eh stoppen, da constraints der db blockieren
    else:
        print("nothing to write to db")
        cur.close()
        return 1
	

def scrapeRessort(text):
	# find ressort
	try:
		footer = text.find("div", {'class': 'articleFooter'})
		ressorts = footer.find_all("a")
		#loop through all a to find a category
		ressortArray = []
		for r in ressorts:
			if "category" in r['href']:
				ressortArray.append(r.string)
		print("ressort: ")
		print(ressortArray)
		return ressortArray
	except Exception:
		traceback.print_exc()
		print("footer not found. ressort not found. date not found")
		print(sys.exc_info())
		sys.exit(1) #kann man eh stoppen, da constraints der db blockieren


def scrapeAuthor(text):
	# find authors
	try:
		div = text.find("div",{'class': 'authorStyle'})
		authors = div.find_all("a")
		#might be several authors
		authorsArray = []
		for a in authors:
			if a.string == None:  # if there is no author
				print("author not found")
				authorsArray = ["Anonym"]  # there is at least one article with no author on luhze.de
				break
			else: #split author in first and last name if there is both
				splitName = a.string.split(" ")
				if len(splitName)>1: # schauen wie viele zwischennamen es gibt und die zu vorname zählen
					firstName = splitName[0]
					for n in range(1,len(splitName)-2):
						firstName = firstName + " " + splitName[n]
					lastName = splitName[len(splitName)-1] #letzter name ist immer nachname
				else: #z.B. hastduzeit, dann nur nachname aufnehmen
					firstName = ""
					lastName = a.string
			authorsArray.append([firstName, lastName])
		print("author: ")
		print(authorsArray)
		return authorsArray
	except Exception:
		traceback.print_exc()
		print("author not found")
		print(sys.exc_info())
		sys.exit(1) #kann man eh stoppen, da constraints der db blockieren


def scrapeTitle(text):
	# find title
	try:
		title = text.find("h2", {'class':'titleStyle'}).string
		print("title: " + title)
		return title
	except Exception:
		traceback.print_exc()
		print("title not found")
		print(sys.exc_info())
		sys.exit(1) #kann man eh stoppen, da constraints der db blockieren


def scrapeDate(text):
	# find date
	try: 
		footer = text.find("div", {'class': 'articleFooter'})
		tmpDate = footer.find("span").string

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
			print(sys.exc_info())
			sys.exit(1) #kann man eh stoppen, da constraints der db blockieren

		date = year + "-" + month + "-" + day + " 00:00:00"
		print("date: " + date)
		return date
	except Exception:
		traceback.print_exc()
		print("date not found")
		print(sys.exc_info())
		sys.exit(1) #kann man eh stoppen, da constraints der db blockieren

def scrapeWordcountAndText(text, title):
	#get wordcount and text
	try:
		article = text.find("article", {'id':'mainArticle'})
		footer = text.find("div", {'class': 'articleFooter'})
		wordcount = 0
		document = ""
		if article is None: #very old article
			allP = text.find("div", {'class':'field-content'}).find_all("p")
			allPInFooter = footer.find_all("p") #ignore text in footer
			for p in allP:
				if p not in allPInFooter:
					wordcount = wordcount + len(p.get_text())
					document += p.get_text() + " "
			print("wordcount: " + str(wordcount))
		elif article.find_all("div",{'class':'field-content'}) is not None: #old article but not so old
			allP = article.find_all("p")
			allPInFooter = footer.find_all("p") #ignore text in footer
			for p in allP:
				if p.get_text() is not None and p.get('id') is None and p not in allPInFooter:
					wordcount = wordcount + len(p.get_text())
					document += p.get_text() + " "
			print("wordcount: " + str(wordcount))
		else:
			allP = article.find_all("p")
			allPInFooter = footer.find_all("p") #ignore text in footer
			for p in allP:
				if p.get_text() is not None and p.get('id') is None and 'contentWrapper' in p.find_parent('div')['class'] and p not in allPInFooter:
					wordcount = wordcount + len(p.get_text())
					document += p.get_text() + " "
			print("wordcount: " + str(wordcount))

		#add title to document
		document = title + " " + document
		return [wordcount, document]

	except Exception:
		traceback.print_exc()
		print("text and wordount not found")
		print(sys.exc_info())
		sys.exit(1) #kann man eh stoppen, da constraints der db blockieren

def fillSQLArray(link, title, authorArray, ressortArray, wordcount, document, date, isIn):
	sqlStatements = []
	
	if isIn == True:
		print("update rows")
		#delte all old rows with link
		sqlStatements.append(['DELETE FROM articles WHERE link=%s', [link]])
		# reinsert document
		sqlStatements.append(['INSERT IGNORE INTO documents VALUES(%s,%s,%s,%s,%s)', [None, document, wordcount, date, datetime.now().strftime('%Y-%m-%d %H:%M:%S')]])
		for a in authorArray:
			#insert author if not exitsts
			sqlStatements.append(['INSERT IGNORE INTO authors VALUES(%s,%s,%s,%s)', [None, a[0], a[1], None]]) 
			for r in ressortArray:
				sqlStatements.append(['INSERT INTO articles VALUES(%s,%s,%s,(SELECT id FROM authors WHERE firstName=%s and lastName=%s),%s,%s, (SELECT id FROM documents WHERE document=%s))', [None,link,title, a[0], a[1], r, date, document]])

	elif isIn == False: 
		print("insert rows")
		# reinsert document
		sqlStatements.append(['INSERT IGNORE INTO documents VALUES(%s,%s,%s,%s,%s)', [None, document, wordcount, date, datetime.now().strftime('%Y-%m-%d %H:%M:%S')]])
		for a in authorArray:
			#insert author if not exitsts
			sqlStatements.append(['INSERT IGNORE INTO authors VALUES(%s,%s,%s,%s)', [None, a[0], a[1], None]]) 
			for r in ressortArray:
				sqlStatements.append(['INSERT INTO articles VALUES(%s,%s,%s,(SELECT id FROM authors WHERE firstName=%s and lastName=%s),%s,%s, (SELECT id FROM documents WHERE document=%s))', [None,link,title, a[0], a[1], r, date, document]])
	else:
		print("wont update nor insert")


	return sqlStatements

def checkIfArticlesIsInDB(cur, link):
	#determine if link is already in db
	try:
		cur.execute('SELECT link FROM articles WHERE link="' + link + '"')
		entry = cur.fetchone() 
		if entry is not None:
			print("articles is already in db")
			return True
		else:
			return False
	except MySQLdb.Error as e:
		print(f"Error while checking if article is in db: {e}")
		cur.close()
		sys.exit(1)

def readInSite(url):
	print("reading in page " + url)
	try:
		text = urlopen(url).read()
	except error.URLError as e:
		traceback.print_exc()
		print("Cannot connect to " + url)
		print(sys.exc_info())
		sys.exit(1)

	return BeautifulSoup(text, 'html.parser')

def findElement(elementName, text, attribute):

	element = text.find(elementName)[attribute]
	if element is not None:
		return element
	else:
		print("cannot find element " + elementName)
		print(sys.exc_info())
		sys.exit(1)	

def findElements(elementName, text):
	
	elements = text.find_all(elementName)
	if len(elements) > 0:
		return elements
	else:
		print("cannot find elements " + elementName)
		print(sys.exc_info())
		sys.exit(1)	


def scrapeWebsite(con):

	if con == 1:
		return 1
	
	cur = con.cursor()


			
	for i in range(0,108)[::-1]: #3 as a random number to start looking for new articles, otherwise its max on luhze site +1
			
		soup = readInSite(web + str(i))
	
		articles = findElements('article', soup)

		for x in articles[::-1]:
			link = findElement("a", x, "href")

			print(link)
			isIn = checkIfArticlesIsInDB(cur, link)

			# I have to update on wordcount or other stuff because of livetickers and later changes
			articlesite = urlopen(link).read()
			soupArticle = BeautifulSoup(articlesite, 'html.parser')
			
			title = scrapeTitle(soupArticle)

			authorArray = scrapeAuthor(soupArticle)
				
			ressortArray = scrapeRessort(soupArticle)

			date = scrapeDate(soupArticle)

			textWordcountArray = scrapeWordcountAndText(soupArticle, title)

			wordcount = textWordcountArray[0]
			document = textWordcountArray[1]
			
			sqlStatements.extend(fillSQLArray(link, title, authorArray, ressortArray, wordcount, document, date, isIn))
		
	executeSQL(sqlStatements, cur, con)

	print("inserting sql statements done")

	return 0


def main():
	print("starting gathering")
	print(datetime.now())
	con = connectToDB()
	
	if scrapeWebsite(con) == 0:
		analyzeLuhze.mainFunc()
	else:
		print("exiting")
		sys.exit(1)
		return 1
	
if __name__ == "__main__":
	main()
