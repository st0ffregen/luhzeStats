#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import pydevd_pycharm
from analyzeLuhze import analyzeNewData
from scrapingFunctions import scrapeRessort, scrapeAuthor, scrapeTitle, scrapeDate, scrapeWordcountAndText, \
    readInSite, getLinksToSingleArticlesFromOverviewPages
from databaseFunctions import executeSQL, connectToDB, closeConnectionToDB


luhzeArticleOverviewPageUrl = 'https://www.luhze.de/page/'
numberOfOverviewPagesToScrapeAgain = int(os.environ['NUMBERS_OF_OVERVIEW_PAGES_TO_SCRAPE_AGAIN'])


def prepareSQLStatements(link, title, authorArray, ressortArray, wordcount, document, date):

    preparedSQLStatements = []
    # there are cases where a ressort, author etc. may be removed after a while so its most safe to delete all affected rows first
    preparedSQLStatements.append(['DELETE FROM documents WHERE document=%s', [document]])

    preparedSQLStatements.append(['DELETE FROM articles WHERE link=%s', [link]])

    preparedSQLStatements.append(['INSERT INTO documents VALUES(%s,%s,%s,%s,%s)',
                                  [None, document, wordcount, None, None]])

    for author in authorArray:

        preparedSQLStatements.append(['INSERT IGNORE INTO authors VALUES(%s,%s,%s,%s)', [None, author, None, None]])
        for ressort in ressortArray:
            preparedSQLStatements.append([
                'INSERT INTO articles VALUES(%s,%s,%s,(SELECT id FROM authors WHERE name=%s),%s,%s,(SELECT id FROM documents WHERE document=%s),%s,%s)',
                [None, link, title, author, ressort, date, document, None, None]])

    return preparedSQLStatements


def scrapeAllInformation(linkToArticle):

    parsedArticlePage = readInSite(linkToArticle)
    title = scrapeTitle(parsedArticlePage)
    authorArray = scrapeAuthor(parsedArticlePage)
    ressortArray = scrapeRessort(parsedArticlePage)
    date = scrapeDate(parsedArticlePage)
    textWordcountArray = scrapeWordcountAndText(parsedArticlePage, title)
    wordcount = textWordcountArray[0]
    document = textWordcountArray[1]

    return {'title': title,
            'authorArray': authorArray,
            'ressortArray': ressortArray,
            'date': date,
            'wordcount': wordcount,
            'document': document}


def connectToDebugger():
    ip = os.environ['DEBUGGING_IP']
    port = 36045#int(os.environ['DEBUGGING_PORT'])
    pydevd_pycharm.settrace(ip, port=port, stdoutToServer=True, stderrToServer=True)


def main():
    if os.environ['DEBUGGING_ENABLED'] == 'true':
        connectToDebugger()

    con, cur = connectToDB()

    linkToArticleArray = getLinksToSingleArticlesFromOverviewPages(numberOfOverviewPagesToScrapeAgain,
                                                                   luhzeArticleOverviewPageUrl)
    reversedLinkToSingleArticlesArray = linkToArticleArray[::-1]

    sqlStatements = []

    for linkToArticle in reversedLinkToSingleArticlesArray:

        informationDict = scrapeAllInformation(linkToArticle)

        sqlStatements.extend(prepareSQLStatements(
            linkToArticle,
            informationDict['title'],
            informationDict['authorArray'],
            informationDict['ressortArray'],
            informationDict['wordcount'],
            informationDict['document'],
            informationDict['date']
        ))

    executeSQL(sqlStatements, con, cur)
    closeConnectionToDB(con, cur)

    analyzeNewData()


if __name__ == '__main__':
    main()
