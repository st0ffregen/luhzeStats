#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from datetime import datetime
import MySQLdb
import math
import re
import sys
import os

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


def analyzeNewData(con, cur):

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



def ranking(cur, backInTime):
    print("calculate ranking for backInTime " + str(backInTime))


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

        initQuarter = (((int(
            minDate.strftime('%Y-%m-%d %H:%M:%S').split("-")[1]) - 1) // 3) + 1)  # gib quarter von 1 bis 4

        for year in range(int(minYear), int(maxYear) + 1):  # +1 da maxYear exklusive Grenze
            for quarter in range(initQuarter, 5):  # 5 ist hier wieder exklusiv
                quarterArray.append(str(year) + str(quarter))
            initQuarter = 1  # setzt initquarter wieder auf 1, s.d. die for schleife jetzt von 1 anfängt
    else:
        print("no articles in new quarters")

    return quarterArray


def insertSQLStatements(cur, con, sqlStatements, whatAction):

    for statement in sqlStatements:
        print(statement[0])
        print(statement[1])
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
    sqlStatements = []  # createQuarterTables(cur, quarterArray)

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
        cur.execute("SELECT MAX(quarterWordCount) FROM wordOccurenceOverTheQuarters WHERE yearAndQuarter = %s",
                    [yearAndQuarter])
        quarterWordCount = cur.fetchone()[0]  # anzahl aller wörter auf luhze.de in diesem quartal
        if quarterWordCount is None:
            print(
                "entries with yearAndQuarter " + yearAndQuarter + " do not exist yet. Treat quarter wordcount as zero.")
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
