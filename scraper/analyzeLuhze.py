#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import os
import datetime
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from databaseFunctions import executeSQL, connectToDB, closeConnectionToDB

occurrenceRatioMultiplier = 100000
unwantedPunctuations = ['´', '‚', '‘', '-', '“', '„', '*', '#', ',', ':', '.', '.', '!', '?', '\"', '“', '„', ')', '(', '”', '“', '[', ']', '–', '„', '„', '…', '’', '»', '\u200b']
wantedPunctuatedWords = ['STUDENT!']


def analyzeNewData():
    logger = configureLogger()

    logger.info('Start analyzer')

    con, cur = connectToDB()

    lastModifiedDate = getLastModifiedDate(cur)

    if lastModifiedDate is None:
        lastModifiedDate = '0001-01-01 00:00:01'
    else:
        lastModifiedDate = lastModifiedDate.strftime('%Y-%m-%d %H:%M:%S')
    logger.info('Last modified date is ' + lastModifiedDate)

    executeSQL(calculateWordOccurrence(cur, lastModifiedDate, logger), con, cur)
    executeSQL(fillDbWithMissingYearsAndQuarters(cur, '0001-01-01 00:00:01', logger), con, cur)

    closeConnectionToDB(con, cur)

    logger.info('Terminate analyzer')


def configureLogger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    file_handler = logging.FileHandler('logs/scraper.log')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


def createYearAndQuarterArray(cur, lastModifiedDate):
    cur.execute(
        'SELECT cast(date_format(MIN(publishedDate),"%%Y-%%m-01") as date) FROM articles WHERE publishedDate > %s',
        [lastModifiedDate])
    minDate = cur.fetchone()[0]

    if minDate < datetime.date(2015, 4, 1):
        minDate = datetime.date(2015, 4, 1)  # min date should be 2015-04-01 because data before that is unreliable

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
        maxQuarter = (((int(
            maxDate.strftime('%Y-%m-%d %H:%M:%S').split("-")[1]) - 1) // 3) + 1)


        for year in range(int(minYear), int(maxYear) + 1):  # +1 da maxYear exklusive Grenze
            quarterLimit = 4
            if year == int(maxYear):
                quarterLimit = maxQuarter
            for quarter in range(initQuarter, quarterLimit + 1):  # +1 ist hier wieder exklusiv
                quarterArray.append([year, quarter])
            initQuarter = 1  # setzt initquarter wieder auf 1, s.d. die for schleife jetzt von 1 anfängt
    else:
        print("no articles in new quarters")

    return quarterArray


def prepareSQLForMissingYearAndQuarters(cur, fetchedWords, yearAndQuarterArray, logger):
    sqlStatements = []

    for yearAndQuarter in yearAndQuarterArray:
        year, quarter = yearAndQuarter
        logger.info('Fill missing rows in year ' + str(year) + ' and quarter ' + str(quarter))
        cur.execute('select max(quarterWordCount) from wordOccurrence where year = %s and quarter = %s',
                    [year, quarter])
        quarterWordCount = cur.fetchone()[0]

        if quarterWordCount is None:
            quarterWordCount = 0

        for word in fetchedWords:
            sqlStatements.append(['insert ignore into wordOccurrence values (%s, %s, %s, 0, %s, 0, %s, %s)', [word, year, quarter, quarterWordCount, None, None]])

    return sqlStatements


def fillDbWithMissingYearsAndQuarters(cur, lastModifiedDate, logger):
    yearAndQuarterArray = createYearAndQuarterArray(cur, lastModifiedDate)
    sqlStatements = []

    cur.execute('select distinct(word) from wordOccurrence')
    fetchedRows = cur.fetchall()

    sqlStatements.extend(prepareSQLForMissingYearAndQuarters(cur, fetchedRows, yearAndQuarterArray, logger))

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
    cur.execute('SELECT distinct(d.document) from documents d join articles a on a.documentId=d.id '
                'where YEAR(a.publishedDate) = %s and QUARTER(a.publishedDate) = %s',
                [year, quarter])
    documentArray = cur.fetchall()

    yearAndQuarterText = ''

    for document in documentArray:
        yearAndQuarterText += document[0] + ' '
    countPerWordDict, charCountInThatYearAndQuarter = calculateWordOccurrenceInThatText(yearAndQuarterText)

    return prepareSQLStatements(countPerWordDict, charCountInThatYearAndQuarter, year, quarter)


def calculateWordOccurrenceInThatText(text):

    countPerWordDict = {}
    yearAndQuarterWordCount = 0

    upperText = text.upper()
    wordArray = upperText.split()

    for w in wordArray:
        w = w.strip()
        w = removeTrailingPunctuations(w)
        w = removeLeadingPunctuations(w)
        if re.match(r'.{2,}$', w):
            if w is not None and len(w) > 1:
                if w in countPerWordDict:
                    countPerWordDict[w] += 1
                else:
                    countPerWordDict[w] = 1
                yearAndQuarterWordCount += 1

    return countPerWordDict, yearAndQuarterWordCount


def removeTrailingPunctuations(w):

    if len(w) > 0 and w[-1] in unwantedPunctuations and w not in wantedPunctuatedWords:
        return removeTrailingPunctuations(w[:-1])
    else:
        return w


def removeLeadingPunctuations(w):

    if len(w) > 0 and w[0] in unwantedPunctuations and w not in wantedPunctuatedWords:
        return removeLeadingPunctuations(w[1:])
    else:
        return w


def calculateWordOccurrence(cur, lastModifiedDate, logger):
    # Four cases need to be addressed
    # 1) The document is new to the documents table (same updated and created date)
    # 1.1) the document is published in a new yearAndQuarter
    # 1.2) the yearAndQuarter already exists and has to be updated
    # 2) the document was updated
    # in this case it is necessary to calculate the whole yearAndQuarter for all words again
    # for the sake of clean code, in every case the app will fetch all documents in that year and quarter and recalculate
    # the occurrence numbers

    sqlStatements = []

    cur.execute('SELECT YEAR(a.publishedDate) as year, QUARTER(a.publishedDate) as quarter FROM articles a join documents d '
                'on a.documentId=d.id WHERE d.updatedAt > %s and d.updatedAt > \'2015-04-01T00:00:00\' group by year, quarter',
                [lastModifiedDate])
    yearAndQuartersWithUpdatedDocumentsArray = cur.fetchall()

    for yearAndQuarter in yearAndQuartersWithUpdatedDocumentsArray:
        logger.info('Calculate date for year ' + str(yearAndQuarter[0]) + ' and quarter ' + str(yearAndQuarter[1]))
        sqlStatements.extend(calculateWordOccurrenceForWholeYearAndQuarter(cur, yearAndQuarter[0], yearAndQuarter[1]))

    return sqlStatements
