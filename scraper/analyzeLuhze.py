#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from databaseFunctions import executeSQL, connectToDB, closeConnectionToDB

occurrenceRatioMultiplier = 100000


def analyzeNewData():
    con = connectToDB()
    cur = con.cursor()

    lastModifiedDate = getLastModifiedDate(cur)

    if lastModifiedDate is None:
        lastModifiedDate = '0001-01-01 00:00:01'
    else:
        lastModifiedDate = lastModifiedDate.strftime('%Y-%m-%d %H:%M:%S')

    executeSQL(calculateWordOccurrence(cur, lastModifiedDate), con, cur)

    executeSQL(fillDbWithMissingYearsAndQuarters(cur, '0001-01-01 00:00:01'), con, cur)

    closeConnectionToDB(con, cur)


def createYearAndQuarterArray(cur, lastModifiedDate):
    cur.execute(
        'SELECT cast(date_format(MIN(publishedDate),"%%Y-%%m-01") as date) FROM articles WHERE publishedDate > %s',
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
                quarterArray.append([year, quarter])
            initQuarter = 1  # setzt initquarter wieder auf 1, s.d. die for schleife jetzt von 1 anfängt
    else:
        print("no articles in new quarters")

    return quarterArray


def getWords(cur, offset, limit):
    cur.execute('select distinct(word) from wordOccurrence limit %s offset %s', [limit, offset])
    return cur.fetchall()


def prepareSQLForMissingYearAndQuarters(cur, fetchedWords, yearAndQuarterArray):
    sqlStatements = []

    for yearAndQuarter in yearAndQuarterArray:
        year = yearAndQuarter[0]
        quarter = yearAndQuarter[1]
        cur.execute('select max(quarterWordCount) from wordOccurrence where year = %s and quarter = %s',
                    [year, quarter])
        quarterWordCount = cur.fetchone()[0]

        if quarterWordCount is None:
            quarterWordCount = 0

        for word in fetchedWords:
            sqlStatements.append(['insert ignore into wordOccurrence values (%s, %s, %s, 0, %s, 0, %s, %s)', [word, year, quarter, quarterWordCount, None, None]])

    return sqlStatements


def fillDbWithMissingYearsAndQuarters(cur, lastModifiedDate):
    yearAndQuarterArray = createYearAndQuarterArray(cur, lastModifiedDate)

    fetchedRows = []
    offset = 0
    sqlStatements = []

    while True:
        fetchedRows = getWords(cur, offset, 5000)
        if len(fetchedRows) == 0:
            break
        sqlStatements.extend(prepareSQLForMissingYearAndQuarters(cur, fetchedRows, yearAndQuarterArray))
        offset += 5000

    return sqlStatements


def getLastModifiedDate(cur):
    cur.execute('select max(updatedAt) from wordOccurrence')
    return cur.fetchone()[0]


def prepareSQLStatements(countPerWordDict, charCountInThatYearAndQuarter, year, quarter):
    sqlStatements = []

    for word in countPerWordDict.keys():
        occurrenceRatio = occurrenceRatioMultiplier * countPerWordDict[word]/charCountInThatYearAndQuarter
        sqlStatements.append(['insert into wordOccurrence values (%s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update '
                             'occurrence=values(occurrence), quarterWordCount=values(quarterWordCount), '
                             'occurrenceRatio=values(occurrenceRatio)',
                             [word, year, quarter, countPerWordDict[word], charCountInThatYearAndQuarter, occurrenceRatio, None, None]])

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

    cur.execute('SELECT YEAR(a.publishedDate) as year, QUARTER(a.publishedDate) as quarter FROM articles a join documents d '
                'on a.documentId=d.id WHERE d.updatedAt > %s order by year, quarter',
                [lastModifiedDate])
    yearAndQuartersWithUpdatedDocumentsArray = cur.fetchall()

    for yearAndQuarter in yearAndQuartersWithUpdatedDocumentsArray:
        sqlStatements.extend(calculateWordOccurrenceForWholeYearAndQuarter(cur, yearAndQuarter[0], yearAndQuarter[1]))

    return sqlStatements
