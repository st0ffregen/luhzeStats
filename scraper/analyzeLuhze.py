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

    executeSQL(calculateWordOccurrence(cur, lastModifiedDate), con, cur)

    executeSQL(fillDbWithMissingYearsAndQuarters(cur, lastModifiedDate), con, cur)

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
    cur.execute('select word from wordOccurence limit %s offset %s', [limit, offset])
    return cur.fetchall


def prepareSQLForMissingYearAndQuarters(cur, fetchedWords, yearAndQuarterArray):
    sqlStatements = []

    for yearAndQuarter in yearAndQuarterArray:
        year = yearAndQuarter[0]
        quarter = yearAndQuarter[1]
        cur.execute('select max(quarterWordCount) from wordOccurrence where year = %s and quarter = %s',
                    [year, quarter])
        quarterWordCount = cur.fetchone()[0]

        for word in fetchedWords[0]:
            sqlStatements.append('insert ignore into wordOccurrence values (%s, %s, %s, 0, %s, %s, %s)', [word, year, quarter, quarterWordCount, None, None])

    return sqlStatements


def fillDbWithMissingYearsAndQuarters(cur, lastModifiedDate):
    yearAndQuarterArray = createYearAndQuarterArray(cur, lastModifiedDate)

    fetchedRows = []
    offset = 0
    sqlStatements = []

    while len(fetchedRows) > 0:
        fetchedRows = getWords(cur, offset, 5000)
        sqlStatements.extend(prepareSQLForMissingYearAndQuarters(cur, fetchedRows, yearAndQuarterArray))

    return sqlStatements


def getLastModifiedDate(cur):
    cur.execute('select max(updatedAt) from wordOccurence')
    return cur.fetchone()[0].strftime('%Y-%m-%d %H:%M:%S')


def prepareSQLStatements(countPerWordDict, charCountInThatYearAndQuarter, year, quarter):
    sqlStatements = []

    for word in countPerWordDict.keys():
        occurrenceRatio = occurrenceRatioMultiplier * countPerWordDict[word]/charCountInThatYearAndQuarter
        sqlStatements.append('insert into wordOccurence values (%s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update '
                             'occurence=values(occurence), quarterWordCount=values(quarterWordCount), '
                             'occurrenceRatio=values(occurrenceRatio)',
                             [word, year, quarter, countPerWordDict[word], charCountInThatYearAndQuarter, occurrenceRatio, None, None])

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
