#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from datetime import datetime
import MySQLdb
import math
import re
import sys
import os
from scraper.databaseFunctions import executeSQL, connectToDB, closeConnectionToDB

minRessort = 14
limitAuthors = 25
fileArray = []

# szenario: wenig aktive Person: ZeitZumLetztenArtikel=120*-0.5=-60, ArtikelAnzahl=10*5=50, CPD=150*1=150, insgesamt = 140
# szenario: sehr aktive Person: ZeitZumLetztenArtikel=15*-0.5=-7, ArtikelAnzahl=35*5=175, CPD=400*1=400, insgesamt = 400

rankingTimeSinceLastArticleWeight = 1.4
rankingCharactersPerDayWeight = 1.4
rankingArticlesCountWeight = 1.2
intervall = 2


occurrenceRatioMultiplier = 100000

def tslaFunction(value):
    # function is using months not days so:
    value = round(value / 30.5)
    # to avoid math overflow when passing month thats to big
    if value > 5:  # also letzter artikel älter als 5 monate
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


def analyzeNewData():
    con = connectToDB()
    cur = con.cursor()

    lastModifiedDate = getLastModifiedDate(cur)

    executeSQL(calculateWordOccurrence(cur, lastModifiedDate), con, cur)

    executeSQL(fillDbWithMissingYearsAndQuarters(cur, lastModifiedDate), con, cur)

    # füllt die tabelle für die totalWordOccurence
    insertSQLStatements(cur, con,
                        calculateTotalWordOccurence(cur, createQuarterArray(cur, fetchLastModified(cur, "True")[0])),
                        True)


    closeConnectionToDB(con, cur)


def fillDbWithMissingYearsAndQuarters(cur, lastModifiedDate):
# hier weitermachen, die methode soll ab jetzt einfach alle wörter in der db durchgehen und für jedes feststellen
# dass für alle years and quarter ein eintrag existiert. Falls keiner da ist soll einer mit 0,0,0 insertet werden

    cur.execute('SELECT cast(date_format(MIN(publishedDate),"%%Y-%%m-01") as date) FROM articles WHERE publishedDate > %s',
                [lastModifiedDate])
    minDate = cur.fetchone()[0]

    cur.execute(
        'SELECT cast(date_format(MAX(publishedDate),"%%Y-%%m-01") as date) FROM articles WHERE publishedDate > %s',
        [lastModifiedDate])
    maxDate = cur.fetchone()[0]

    quarterArray = []

    if minDate is not None and maxDate is not None:
        minYear = str(minDate.strftime('%Y-%m-%d %H:%M:%S')).split("-")[0]
        maxYear = str(maxDate.strftime('%Y-%m-%d %H:%M:%S')).split("-")[0]

        initQuarter = (((int(
            minDate.strftime('%Y-%m-%d %H:%M:%S').split("-")[1]) - 1) // 3) + 1)  # gib quarter von 1 bis 4

        for year in range(int(minYear), int(maxYear) + 1):  # +1 da maxYear exklusive Grenze
            for quarter in range(initQuarter, 5):  # 5 ist hier wieder exklusiv
                quarterArray.append(str(year) + str(quarter))
            initQuarter = 1  # setzt initquarter wieder auf 1, s.d. die for schleife jetzt von 1 anfängt
    else:
        print("no articles in new quarters")

    return quarterArray


def getLastModifiedDate(cur):
    cur.execute('select max(updatedAt) from wordOccurence')
    return cur.fetchone()[0].strftime('%Y-%m-%d %H:%M:%S')


def prepareSQLStatements(countPerWordDict, charCountInThatYearAndQuarter, year, quarter):
    sqlStatements = []

    for word in countPerWordDict.keys():
        occurrenceRatio = occurrenceRatioMultiplier * countPerWordDict[word]/charCountInThatYearAndQuarter
        sqlStatements.append('insert into wordOccurence values (%s, %s, %s, %s, %s, %s) on duplicate key update '
                             'occurence=values(occurence), quarterWordCount=values(quarterWordCount), '
                             'occurrenceRatio=values(occurrenceRatio)',
                             [word, year, quarter, countPerWordDict[word], charCountInThatYearAndQuarter, occurrenceRatio])

    return sqlStatements


def calculateWordOccurrenceForWholeYearAndQuarter(cur, year, quarter):
    cur.execute('SELECT d.document from documents d join articles a on a.documentId=d.id '
                'where YEAR(a.publishedDate) = %s and QUARTER(a.publishedDate) = %s',
                [year, quarter])
    documentArray = cur.fetchall()

    charCountInThatYearAndQuarter = 0
    yearAndQuarterText = ''

    for document in documentArray[0]:
        yearAndQuarterText += document + ' '

    results = calculateWordOccurrenceInThatText(yearAndQuarterText)

    countPerWordDict = results[0]
    charCountInThatYearAndQuarter = results[1]

    return prepareSQLStatements(countPerWordDict, charCountInThatYearAndQuarter, year, quarter)


def calculateWordOccurrenceInThatText(text):

    countPerWordDict = {}
    yearAndQuarterWordCount = 0

    upperText = text.upper()
    wordArray = upperText.split()

    for w in wordArray:
        w = w.strip()
        if re.match(r'.{2,}$', w):
            w = removeTrailingPunctuations(w)
            w = removeLeadingPunctuations(w)
            if w is not None and len(w) > 1:
                if w in countPerWordDict:
                    countPerWordDict[w] += 1
                else:
                    countPerWordDict[w] = 1
                yearAndQuarterWordCount += 1

    return [countPerWordDict, yearAndQuarterWordCount]


def removeTrailingPunctuations(w):
    unwantedPunctuations = ["-", ",", ":", ".", "!", "?", "\"", "“", ")"]

    if w[-1] in unwantedPunctuations and len(w) > 2 and w != "STUDENT!":  # student! darf das Ausrufezeichen behalten
        return removeTrailingPunctuations(w[:-1])
    else:
        return w


def removeLeadingPunctuations(w):
    unwantedPunctuations = ["-", ",", ":", ".", "!", "?", "\"", "„", "("]

    if w[0] in unwantedPunctuations and len(w) > 2:
        return removeLeadingPunctuations(w[1:])
    else:
        return w


def calculateWordOccurrence(cur, lastModifiedDate):
    # Four cases need to be addressed
    # 1) The document is new (same updated and created date)
    # 1.1) the document is published in a new yearAndQuarter
    # 1.2) the yearAndQuarter already exists and has to be updated
    # 2) the document was updated
    # in this case it is necessary to calculate the whole yearAndQuarter for all words again
    # for the sake of clean code, in every case the app will fetch all documents in that year and quarter and recalculate
    # the occurrence numbers

    sqlStatements = []

    cur.execute('SELECT YEAR(a.publishedDate), QUARTER(a.publishedDate) FROM articles a join documents d '
                'on a.documentId=d.id WHERE d.updetedAt > %s',
                [lastModifiedDate])
    yearAndQuartersWithUpdatedDocumentsArray = cur.fetchall()

    for yearAndQuarter in yearAndQuartersWithUpdatedDocumentsArray:
        calculateWordOccurrenceForWholeYearAndQuarter(cur, yearAndQuarter[0], yearAndQuarter[1])

    return sqlStatements


def calculateTotalWordOccurence(cur, quarterArray):
    print("Calculate total word occurence")
    countPerWordDict = {}
    sqlStatements = []
    totalWordCount = 0
    print(quarterArray)
    for yearAndQuarter in quarterArray:

        cur.execute(
            'SELECT word, occurence, quarterWordCount FROM wordOccurenceOverTheQuarters WHERE yearAndQuarter = %s',
            [yearAndQuarter])

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
        if word == "der":
            print(countPerWordDict[word])
        sqlStatements.append([
            'INSERT INTO totalWordOccurence VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE occurencePerWords=(((occurence + VALUES(occurence))/VALUES(totalWordCount))*100000),occurence=occurence + VALUES(occurence), totalWordCount=VALUES(totalWordCount)',
            [word, round(countPerWordDict[word] / totalWordCount * 100000), countPerWordDict[word],
             totalWordCount]])

    return sqlStatements
