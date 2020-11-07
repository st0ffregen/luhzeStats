#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from datetime import datetime
import MySQLdb
import math
import re
import sys

minRessort = 14
limitAuthors = 25
fileArray = []

# szenario: wenig aktive Person: ZeitZumLetztenArtikel=120*-0.5=-60, ArtikelAnzahl=10*5=50, CPD=150*1=150, insgesamt = 140
# szenario: sehr aktive Person: ZeitZumLetztenArtikel=15*-0.5=-7, ArtikelAnzahl=35*5=175, CPD=400*1=400, insgesamt = 400

rankingTimeSinceLastArticleWeight = 1.4
rankingCharactersPerDayWeight = 1.4
rankingArticlesCountWeight = 1.2
intervall = 2




def tslaFunction(value):
    # function is using months not days so:
    value = round(value / 30.5)
    # to avoid math overflow when passing month thats to big
    if value > 5: #also letzter artikel älter als 5 monate
        return round(-0.5 * value)  # linear loosing points over time
    else:
        result = round(-10 / (0.1 + 10 * math.exp(-1.3 * value)) + 100)
        return round(result * rankingTimeSinceLastArticleWeight)


def cpdFunction(value):
    result = round(10 / (0.103 + 2.5 * math.exp(-0.02 * value)))
    return round(result * rankingCharactersPerDayWeight)


def acFunction(value):
    result = round(10 / (0.1 + math.exp(-0.4 * value)) - 10)
    return round(result * rankingArticlesCountWeight)


def connectToDB():
    try:
        con = MySQLdb.connect(
            host='db',  # was muss hier fuer ein host???
            db='luhze',
            user='gatherer',
            passwd='testGatherer'
        )
        con.set_character_set('utf8mb4')
        con.autocommit(False)
        return con
    except MySQLdb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")

    return 1


def mainFunc():
    print("start analyzing")
    print(datetime.now())
    con = connectToDB()

    try:
        con.autocommit = False
        cur = con.cursor()


        minAuthor = selfCalibrieren(cur)
        
        fileArray.append([json.dumps({'minAuthor':minAuthor}),'minAuthor'])
        #fileArray.append([json.dumps({'date':datetime.now()}, default = str),'date']) #treats datetime as string
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

        # ranking
        rankingSQLStatements = []
        rankingSQLStatements.extend(ranking(cur, 'rankingDefault', 0))
        rankingSQLStatements.extend(ranking(cur, 'rankingMonth', 1))
        rankingSQLStatements.extend(ranking(cur, 'rankingYear', 12))
        rankingSQLStatements.extend(ranking(cur, 'rankingTwoYears', 24))
        rankingSQLStatements.extend(ranking(cur, 'rankingFiveYears', 60))

        insertSQLStatements(cur, con, rankingSQLStatements, "ranking")

        # erstellt und füllt die tabellen für die quarter
        insertSQLStatements(cur, con, calculateWordOccurence(cur), "False")
        # füllt die tabelle für die totalWordOccurence
        insertSQLStatements(cur, con,
                            calculateTotalWordOccurence(cur, createQuarterArray(cur, fetchLastModified(cur, "True")[0])),
                            True)

        print("commiting json for files")
        insertSQLStatements(cur, con, fileArray, "fileArray")


        # cur.close()
    except MySQLdb.Error as e:
        print(f"MySQL Error in mainFunc(): {e}")
        return 1
    except:
        print(sys.exc_info())
        sys.exit(1)
        return 1


def selfCalibrieren(cur):
    print("selfCalibrieren")
    cur.execute(
        'SELECT authorId, count(distinct Link) FROM articles GROUP BY authorId ORDER BY 2 DESC LIMIT %s', [limitAuthors])
    entries = cur.fetchall()
    minAuthor = entries[len(entries) - 1][1]  # makes sure that always 30 authors are shown
    print("minAuthor is: " + str(minAuthor))
    return minAuthor


def oldestArticle(cur, filename):
    print("get oldest article")
    cur.execute('SELECT MIN(created) FROM articles')
    entries = cur.fetchall()
    fileArray.append([json.dumps({'oldestArticle': entries[0][0]}, default=str), filename])
    return entries[0]


def newestArticle(cur, filename):
    print("get newest article")
    cur.execute('SELECT MAX(created) FROM articles')
    entries = cur.fetchall()
    fileArray.append([json.dumps({'newestArticle': entries[0][0]}, default=str), filename])
    return entries[0]


def articlesTimeline(cur, filename):
    print("get articles timeline")
    cur.execute(
        'select cast(date_format(created,"%Y-%m-01") as date),count(distinct link) as countPerMonth from articles group by year(created),month(created) order by 1 asc')
    entries = cur.fetchall()
    fileArray.append([json.dumps(adjustFormatDate(entries)[::-1], default=str), filename])
    return 0


def activeMembers(cur, filename):
    print("get active members")
    cur.execute('SELECT authorId FROM articles GROUP BY authorId')
    entries = cur.fetchall()
    arr = []
    for e in entries:
        cur.execute('SELECT created FROM articles WHERE authorId =%s GROUP BY link', [e[0]])
        dates = cur.fetchall()
        dateArray = []
        for d in dates:
            dateArray.append(d[0].strftime('%Y-%m-%d %H:%M:%S'))
        arr.append({"name": e[0], "articles": dateArray})
    fileArray.append([json.dumps(arr), filename])
    return 0


def ressortTopList(cur, filename):
    print("get ressort top list")
    cur.execute(
        'SELECT ressort, count(distinct link) FROM articles GROUP BY ressort HAVING count(distinct link) >= %s ORDER BY 2 DESC', [str(minRessort)])
    entries = cur.fetchall()
    fileArray.append([json.dumps(adjustFormatName(entries)), filename])
    return 0


def ressortArticlesTimeline(cur, filename):
    print("get ressort articles timeline")
    cur.execute(
        'SELECT ressort, cast(date_format(created,"%%Y-%%m-01") as date),count(distinct link) as countPerMonth from articles where ressort in (select ressort from articles group by ressort having count(distinct link) >= %s) group by ressort, year(created), month(created)', [str(minRessort)])
    entries = cur.fetchall()
    arr = []  # [{ressort: hopo, articles: [{date: some month, 5},{date: some month, 4}]}]
    ressort = entries[0][0]  # set ressort to first in fetched list
    monthArray = []
    for e in entries:
        if ressort == e[0]:
            monthArray.append({"date": e[1], "count": e[2]})
            if e == entries[len(entries) - 1]:  # if it is last element
                arr.append({"ressort": ressort, "countPerMonth": monthArray})
        else:
            arr.append({"ressort": ressort, "countPerMonth": monthArray})
            monthArray = [{"date": e[1], "count": e[2]}]
            ressort = e[0]
            if e == entries[len(entries) - 1]:  # if it is last element
                arr.append({"ressort": ressort, "countPerMonth": monthArray})

    fileArray.append([json.dumps(arr, default=str), filename])
    return 0


def topAuthorsPerRessort(cur, filename):
    print("get top authors per ressort")
    cur.execute('SELECT ressort, ar.authorId, au.firstName, au.lastName, count(link) as count from articles ar join authors au on ar.authorId=au.id where ressort in (select ressort from articles group by ressort having count(distinct link) >= %s) group by ressort, authorId having count >= 5 order by 1 asc,5 desc', [str(minRessort)])
    entries = cur.fetchall()
    arr = []  # should by filled with [{ressort: hopo, authors: [{name: theresa, count:5},{name: someone, count:2}]}] with min count >= 2 (in this example)
    ressort = entries[0][0]  # set ressort to first in fetched list
    authorArray = []
    for e in entries:
        if ressort == e[0]:
            name = (e[2] + " " + e[3]).strip()
            authorArray.append({"name": name, "count": e[4]})
            if e == entries[len(entries) - 1]:  # if it is last element
                arr.append({"ressort": ressort, "authors": authorArray[:3]})
        else:
            arr.append({"ressort": ressort, "authors": authorArray[:3]})
            name = (e[2] + " " + e[3]).strip()
            authorArray = [{"name": name, "count": e[4]}]
            ressort = e[0]
            if e == entries[len(entries) - 1]:  # if it is last element
                arr.append({"ressort": ressort, "authors": authorArray[:3]})

    fileArray.append([json.dumps(arr), filename])
    return 0


def authorTimeline(cur, filename, minAuthor):
    print("get author timeline")
    cur.execute(
        'SELECT ar.authorId, au.firstName, au.lastName, MIN(created), MAX(created) FROM articles ar join authors au on ar.authorId=au.id GROUP BY authorId HAVING count(distinct link) >= %s ORDER BY count(distinct link) DESC', [str(minAuthor)])
    entries = cur.fetchall()
    arr = []  # adjustFormat function only takes array with 2-tupel (2 entries in tupel)
    for e in entries:
        name = (e[1] + " " + e[2]).strip()
        arr.append({"name": name, "min": e[3], "max": e[4]})
    fileArray.append([json.dumps(arr, default=str), filename])
    return 0


def mostArticlesPerTime(cur, filename, minAuthor):
    print("get most articles per time")
    cur.execute(
        'SELECT ar.authorId, au.firstName, au.lastName, ROUND(((DATEDIFF(MAX(created),MIN(created)))/count(distinct link)),1) as diff FROM articles ar join authors au on ar.authorId=au.id GROUP BY authorId HAVING count(distinct link) >= %s ORDER BY diff', [str(minAuthor)])
    entries = cur.fetchall()
    arr = []
    for e in entries:
        arr.append({'name': e[1] + " " + e[2], 'count': str(e[3])})
    fileArray.append([json.dumps(arr), filename])  # decimal output from sql is not serializeable, cast to float
    return 0


def authorAverage(cur, filename, minAuthor):
    print("get author average")
    cur.execute(
        'SELECT ar.authorId, au.firstName, au.lastName, round(avg(wordcount)) as count from (select distinct(link), d.wordcount as wordcount, authorId from articles art join documents d on art.documentId=d.id where authorId in (select authorId from articles group by authorId having count(distinct link) >=%s)) as ar join authors au on ar.authorId=au.id group by authorId order by count desc', [str(minAuthor)])
    entries = cur.fetchall()
    arr = []
    for e in entries:
        arr.append({'name': e[1] + " " + e[2], 'count': str(e[3])})
    fileArray.append([json.dumps(arr), filename])
    return 0


def averageCharactersPerDay(cur, filename, minAuthor):
    print("get average characters per day")
    cur.execute(
        'SELECT ar.authorId, au.firstName, au.lastName, sum(wordcount) as count from (select distinct(link), d.wordcount as wordcount, authorId from articles art join documents d on art.documentId=d.id where authorId in (select authorId from articles group by authorId having count(distinct link) >= %s )) as ar join authors as au on ar.authorId=au.id group by authorId order by count desc', [str(minAuthor)])
    entries = cur.fetchall()
    arr = []
    for e in entries:
        cur.execute('SELECT DATEDIFF(MAX(created),MIN(created))+1 as average from articles where authorId=%s',[str(e[0])])
        res = cur.fetchone()
        name = (e[1] + " " + e[2]).strip()
        arr.append({"name":  name, "count": round(e[3] / res[0])})
    fileArray.append([json.dumps(sorted(arr, key=lambda x: x['count'], reverse=True)), filename])
    return 0


def ressortAverage(cur, filename):
    print("get ressort average")
    cur.execute(
        'SELECT ressort, round(avg(wordcount)) as count from (select distinct(link), d.wordcount as wordcount, ressort from articles ar join documents as d on ar.documentId=d.id where ressort in (select ressort from articles group by ressort having count(distinct link) >=%s)) as sub group by ressort order by count desc', [str(minRessort)])
    entries = cur.fetchall()
    arr = []
    for e in entries:
        arr.append({'name': e[0], 'count': str(e[1])})
    fileArray.append([json.dumps(arr), filename])
    return 0


def authorTopList(cur, filename, minAuthor):
    print("get author top list")
    cur.execute(
        'SELECT ar.authorId, au.firstName, au.lastName,count(distinct link) FROM articles ar join authors au on ar.authorId=au.id GROUP BY authorId HAVING count(distinct link) >= %s ORDER BY 4 DESC', [str(minAuthor)])
    entries = cur.fetchall()
    res = []
    for e in entries:
        res.append({'name': e[1] + " " + e[2], 'count': e[3]})
    fileArray.append([json.dumps(res), filename])
    return 0


def ressortTimeline(cur, filename):
    print("get ressort timeline")
    cur.execute(
        'SELECT ressort, MIN(created), MAX(created) FROM articles GROUP BY ressort ORDER BY count(distinct link) DESC')
    entries = cur.fetchall()
    arr = []  # adjustFormat function only takes array with 2-tupel (2 entries in tupel)
    for e in entries:
        arr.append({"name": e[0], "min": e[1], "max": e[2]})
    fileArray.append([json.dumps(arr, default=str), filename])
    return 0


def ranking(cur, filename, backInTime):
    print("calculate ranking")
    cur.execute('SELECT distinct(ar.authorId), au.firstName, au.lastName  from articles ar join authors au on ar.authorId=au.id')
    entries = cur.fetchall()
    sqlStatements = [];
    for e in entries:  # loop through all authors

        # berechnet sum(wordcount) für alle artikel vor dem gebenen Zeitpunkt, also z.B. alles vor jetzt oder alle vor jetzt minus ein Jahr
        cur.execute(
            'SELECT sum(wordcount) as count from (select distinct(link), d.wordcount as wordcount, authorId from articles ar join documents d on ar.documentId=d.id where authorId = %s and created < DATE_ADD(CURDATE(), INTERVAL - %s MONTH)) as sub', [str(e[0]), str(backInTime)])
        wordcountResult = cur.fetchone()
        if (wordcountResult[0] == "NULL" or wordcountResult[0] == None):  # den autor gabs damals noch nicht
            continue

        cur.execute('SELECT DATEDIFF(DATE_ADD(CURDATE(), INTERVAL - %s MONTH),MIN(created))+1 as average from articles where authorId=%s and created < DATE_ADD(CURDATE(), INTERVAL - %s MONTH)', [str(backInTime), str(e[0]), str(backInTime)])
        daysSinceFirstArticleResult = cur.fetchone()

        cur.execute('SELECT DATEDIFF(DATE_ADD(CURDATE(), INTERVAL - %s MONTH),MAX(created))+1 as average from articles where authorId=%s and created < DATE_ADD(CURDATE(), INTERVAL - %s MONTH)', [str(backInTime), str(e[0]), str(backInTime)])
        daysSinceLastArticleResult = cur.fetchone()

        cur.execute('SELECT count(distinct link) FROM articles where authorId = %s and created < DATE_ADD(CURDATE(), INTERVAL - %s MONTH)', [str(e[0]), str(backInTime)])
        articleCountResult = cur.fetchone()

        # two months before bzw. plus backInTime
        cur.execute(
            'SELECT sum(wordcount) as count from (select distinct(link), d.wordcount as wordcount, authorId from articles ar join documents d on ar.documentId=d.id where authorId = %s and created < DATE_ADD(CURDATE(), INTERVAL - %s MONTH)) as sub', [str(e[0]), str(intervall + backInTime)])
        wordcountResultBackInTime = cur.fetchone()
        if (wordcountResultBackInTime[0] == "NULL" or  wordcountResultBackInTime[0] == None):  # no article published two months before

            sqlStatements.append(['INSERT INTO ranking VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE wordcount=VALUES(wordcount),'
                                  'daysSinceFirstArticle=VALUES(daysSinceFirstArticle), daysSinceLastArticle=VALUES(daysSinceLastArticle),'
                                  'articleCount=VALUES(articleCount), wordcountBackInTime=VALUES(wordcountBackInTime),'
                                  'daysSinceFirstArticleBackInTime=VALUES(daysSinceFirstArticleBackInTime),'
                                  'daysSinceLastArticleBackInTime=VALUES(daysSinceLastArticleBackInTime),'
                                  'articleCountBackInTime=VALUES(articleCountBackInTime)', [None, e[0], int(wordcountResult[0]), 0, daysSinceFirstArticleResult[0],
                                                                                            0, daysSinceLastArticleResult[0], 0, articleCountResult[0], 0]])

            continue
        else:
            cur.execute('SELECT DATEDIFF(DATE_ADD(CURDATE(), INTERVAL - %s MONTH),MIN(created))+1 as average from articles where authorId= %s and created < DATE_ADD(CURDATE(), INTERVAL - %s MONTH)', [str(backInTime), str(e[0]), str(backInTime + intervall)])
            daysSinceFirstArticleResultBackInTime = cur.fetchone()

            cur.execute('SELECT DATEDIFF(DATE_ADD(CURDATE(), INTERVAL - %s MONTH),MAX(created))+1 as average from articles where authorId=%s and created < DATE_ADD(CURDATE(), INTERVAL - %s MONTH)', [str(backInTime), str(e[0]), str(backInTime + intervall)])
            daysSinceLastArticleResultBackInTime = cur.fetchone()

            cur.execute('SELECT count(distinct link) FROM articles where authorId = %s and created < DATE_ADD(CURDATE(), INTERVAL - %s MONTH)', [str(e[0]), str(intervall + backInTime)])
            articleCountResultBackInTime = cur.fetchone()



        sqlStatements.append(['INSERT INTO ranking VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE wordcount=VALUES(wordcount),'
                                 'daysSinceFirstArticle=VALUES(daysSinceFirstArticle), daysSinceLastArticle=VALUES(daysSinceLastArticle),'
                                 'articleCount=VALUES(articleCount), wordcountBackInTime=VALUES(wordcountBackInTime),'
                                 'daysSinceFirstArticleBackInTime=VALUES(daysSinceFirstArticleBackInTime),'
                                 'daysSinceLastArticleBackInTime=VALUES(daysSinceLastArticleBackInTime),'
                                 'articleCountBackInTime=VALUES(articleCountBackInTime)',
                                 [None, e[0], int(wordcountResult[0]), wordcountResultBackInTime[0],
                                  daysSinceFirstArticleResult[0], daysSinceFirstArticleResultBackInTime[0],
                                  daysSinceLastArticleResult[0], daysSinceLastArticleResultBackInTime[0],
                                  articleCountResult[0], articleCountResultBackInTime[0]]])

    return sqlStatements


def createQuarterArray(cur, lastmodified):
    # erstellt für jedes Quartal eine wordOccurence Tabelle
    # ermittelt den neuesten ältesten artikel, also ein minimales datum
    cur.execute('SELECT cast(date_format(MIN(created),"%%Y-%%m-01") as date) FROM articles WHERE created > %s',
                [lastmodified.strftime('%Y-%m-%d %H:%M:%S')])
    minDate = cur.fetchone()[0]

    # ermittelt den neuesten jüngsten artikel, also ein maximales datum
    cur.execute(
        'SELECT cast(date_format(MAX(created),"%%Y-%%m-01") as date) FROM articles WHERE created > %s',
        [lastmodified.strftime('%Y-%m-%d %H:%M:%S')])
    maxDate = cur.fetchone()[0]

    quarterArray = []

    if minDate is not None and maxDate is not None:
        minYear = str(minDate.strftime('%Y-%m-%d %H:%M:%S')).split("-")[0]
        maxYear = str(maxDate.strftime('%Y-%m-%d %H:%M:%S')).split("-")[0]

        initQuarter = (((int(minDate.strftime('%Y-%m-%d %H:%M:%S').split("-")[1]) - 1) // 3) + 1)  # gib quarter von 1 bis 4

        for year in range(int(minYear), int(maxYear) + 1):  # +1 da maxYear exklusive Grenze
            for quarter in range(initQuarter, 5):  # 5 ist hier wieder exklusiv
                quarterArray.append(str(year) + str(quarter))
            initQuarter = 1  # setzt initquarter wieder auf 1, s.d. die for schleife jetzt von 1 anfängt
    else:
        print("no articles in new quarters")

    return quarterArray

def insertSQLStatements(cur, con, sqlStatements, whatAction):
    if sqlStatements is not None and len(sqlStatements) > 0:
        try:
            if whatAction == "fileArray":
                for statement in sqlStatements:
                    cur.execute('INSERT INTO files VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE json=VALUES(json)', [None, statement[1], statement[0]])

                cur.execute('UPDATE lastmodified set lastModifiedFiles = %s', [datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S')])  # update lastmodified
            else:
                for statement in sqlStatements:
                    #print(statement[0])
                    #print(statement[1])
                    cur.execute(statement[0], statement[1])

                if whatAction == "True":
                    cur.execute('UPDATE lastmodified set lastModifiedTotalWordOccurence = %s', [datetime.now().strftime(
                        '%Y-%m-%d %H:%M:%S')])  # update lastmodified
                elif whatAction == "False":
                    cur.execute('UPDATE lastmodified set lastModifiedWordOccurence = %s', [datetime.now().strftime(
                        '%Y-%m-%d %H:%M:%S')])  # update lastmodified
                elif whatAction == "ranking":
                    cur.execute('UPDATE lastmodified set lastModifiedRanking = %s', [datetime.now().strftime(
                        '%Y-%m-%d %H:%M:%S')])  # update lastmodified


            print("commiting statements")
            con.commit()
            return 0
        except MySQLdb.Error as e:
            print(f"Error while inserting sql statements from analyzeLuhze: {e}")
            print("rollback everything")
            # loescht nicht die neu angelegten tabellen, da die als ddl nicht von autocommit(false) betroffen sind
            # kann zwar hier alle tabellen loeschen die in quarterArray vorkommen aber dann loesche ich auch potenzielle immer die mit dem alten aber noch aktuellen quarter
            con.rollback()
            cur.close()
            print(sys.exc_info())
            sys.exit(1)  # kann man eh stoppen, da constraints der db blockieren

    else:
        print("nothing to write to db")
        return 0


def fetchLastModified(cur, total):
    print("fetch lastmodified")
    try:
        # fetch lastmodiefied
        if total:
            cur.execute('SELECT lastmodifiedTotalWordOccurence from lastmodified')
        else:
            cur.execute('SELECT lastmodifiedWordOccurence from lastmodified')
        lastmodified = cur.fetchone()  # letztes mal das analysiert wurde
        return lastmodified
    except MySQLdb.Error as e:
        print(f"Error while fetching lastmodified: {e}")
        print(sys.exc_info())
        sys.exit(1)  # kann man eh stoppen, da constraints der db blockieren



def calculateWordOccurence(cur):
    print("calculate word occurence for each quarter")
    # berechnet zu jedem wort eine relative zahl die die absolute Anzahl der Erscheinen des Wortes dividiert durch eine bestimmte
    # Zahl dartsellt (z.B. 100 000)
    # ich nutze die lastmodified tabelle um nicht alle artikel nochmals zu analysieren zu müssen

    lastmodified = fetchLastModified(cur, False)[0]
    # zunächst erstellen der neuen tabellen für die neuen Quartale
    quarterArray = createQuarterArray(cur, lastmodified)
    sqlStatements = []#createQuarterTables(cur, quarterArray)

    # fetch new articles from documents
    cur.execute('SELECT document, YEAR(createdDate), QUARTER(createdDate) FROM documents WHERE addedDate > %s',
                [lastmodified.strftime('%Y-%m-%d %H:%M:%S')])
    newDocuments = cur.fetchall()

    # loop durch die neuen quarter und fasse dokumente aus den quarter zusammen
    # immer auf der Grundlage dass es das eventuell ein überschneidendes Quarter gibt, quasi ein laufender Monat wo schon dinge drinstehen
    # das ist immer maximal ein yearAndQuarter, das wissen wir anhand von lastmodified
    print("new quarters:")
    print(quarterArray)
    for yearAndQuarter in quarterArray:

        quarterSqlStatements = []

        quarterText = ""
        # find documentes with same quarter and year
        documentInThatQuarterCount = 0
        for document in newDocuments:
            if yearAndQuarter == str(document[1]) + str(document[2]):
                # fasse dokumente zusammen
                quarterText += document[0]
                documentInThatQuarterCount += 1
        print("found " + str(documentInThatQuarterCount) + " documents in quarter " + str(yearAndQuarter))

        # get last wordcount from table
        cur.execute("SELECT MAX(quarterWordCount) FROM wordOccurenceOverTheQuarters WHERE yearAndQuarter = %s", [yearAndQuarter])
        quarterWordCount = cur.fetchone()[0] # anzahl aller wörter auf luhze.de in diesem quartal
        if quarterWordCount is None:
            print("entries with yearAndQuarter " + yearAndQuarter + " do not exist yet. Treat quarter wordcount as zero.")
            quarterWordCount = 0
        else:
            quarterWordCount = int(quarterWordCount)

        countPerWordDict = {}
        upperText = quarterText.upper()
        allWords = upperText.split()

        for w in allWords:
            w = w.strip()
            if re.match(r'.{2,}$', w):
                w = removeTrailingPunctuations(w)
                w = removeLeadingPunctuations(w)
                if w is not None and len(w) > 1:
                    if w in countPerWordDict:
                        countPerWordDict[w] += 1
                    else:
                        countPerWordDict[w] = 1
                    quarterWordCount += 1

        for w in countPerWordDict.keys():
            quarterSqlStatements.append([
                'INSERT INTO wordOccurenceOverTheQuarters VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE occurencePerWords=(((occurence + VALUES(occurence))/VALUES(quarterWordCount))*100000),occurence=occurence + VALUES(occurence), quarterWordCount=VALUES(quarterWordCount)',
                [w, yearAndQuarter, round(countPerWordDict[w] / quarterWordCount * 100000),
                 countPerWordDict[w], quarterWordCount]])

        sqlStatements.extend(quarterSqlStatements)

    return sqlStatements

def calculateTotalWordOccurence(cur, quarterArray):
    print("Calculate total word occurence")
    countPerWordDict = {}
    sqlStatements = []
    totalWordCount = 0
    print(quarterArray)
    for yearAndQuarter in quarterArray:

        cur.execute('SELECT word, occurence, quarterWordCount FROM wordOccurenceOverTheQuarters WHERE yearAndQuarter = %s', [yearAndQuarter])

        allEntriesFromThatTable = cur.fetchall()
        # maybe there is no word with that yearAndQuarter
        if allEntriesFromThatTable is None or len(allEntriesFromThatTable) == 0:
            continue
        totalWordCount += allEntriesFromThatTable[0][2]
        for word in allEntriesFromThatTable:
            if word[0] in countPerWordDict:
                countPerWordDict[word[0]] += word[1]
            else:
                countPerWordDict[word[0]] = word[1]



    for word in countPerWordDict.keys():
        if word=="der":
            print(countPerWordDict[word])
        sqlStatements.append([
            'INSERT INTO totalWordOccurence VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE occurencePerWords=(((occurence + VALUES(occurence))/VALUES(totalWordCount))*100000),occurence=occurence + VALUES(occurence), totalWordCount=VALUES(totalWordCount)',
            [word, round(countPerWordDict[word] / totalWordCount * 100000), countPerWordDict[word],
             totalWordCount]])

    return sqlStatements


def removeTrailingPunctuations(w):
    unwantedPunctuations = ["-", ",", ":", ".", "!", "?", "\"", "“", ")"]

    if w[-1] in unwantedPunctuations and len(w) > 2 and w != "STUDENT!": #student! darf das Ausrufezeichen behalten
        return removeTrailingPunctuations(w[:-1])
    else:
        return w


def removeLeadingPunctuations(w):
    unwantedPunctuations = ["-", ",", ":", ".", "!", "?", "\"", "„", "("]

    if w[0] in unwantedPunctuations and len(w) > 2:
        return removeLeadingPunctuations(w[1:])
    else:
        return w






def writeToDB(cur, con):
    try:
        for file in fileArray:
            print("insertOrUpdate", [file[1], "{" + str(file[0]) + "}"])
            cur.callproc("insertOrUpdate", [file[1], str(file[0])])
        # mit cursor.stored_results() results verarbeiten,falls gewünscht
    except MySQLdb.Error as e:
        print(f"Error inserting rows to MariaDB Platform: {e}")
        print("rollback")
        con.rollback()  # rolled nur den letzten Eintrag back
        return 1
    else:
        print("commiting changes")
        con.commit()
        return 0


def adjustFormatDate(entries):
    arr = []
    for e in entries:
        arr.append({'date': e[0], 'count': e[1]})
    return arr


def adjustFormatName(entries):
    arr = []
    for e in entries:
        arr.append({'name': e[0], 'count': e[1]})
    return arr
