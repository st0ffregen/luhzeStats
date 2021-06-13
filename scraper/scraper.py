#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import sys
import os
import logging
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


def scrapeAllInformation(linkToArticle, logger):

    logger.info('Scrape information from ' + linkToArticle)

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
    port = int(os.environ['DEBUGGING_PORT'])
    pydevd_pycharm.settrace(ip, port=port, stdoutToServer=True, stderrToServer=True)


def configureLogger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    file_handler = logging.FileHandler('logs/scraper.log')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


def main():
    logger = configureLogger()

    logger.info('Start scraper')

    ip = '192.168.1.56'
    port = 33849
    pydevd_pycharm.settrace(ip, port=port, stdoutToServer=True, stderrToServer=True)

    con, cur = connectToDB()

    linkToArticleArray = getLinksToSingleArticlesFromOverviewPages(numberOfOverviewPagesToScrapeAgain,
                                                                   luhzeArticleOverviewPageUrl)
    reversedLinkToSingleArticlesArray = linkToArticleArray[::-1]

    sqlStatements = []

    for linkToArticle in reversedLinkToSingleArticlesArray:

        informationDict = scrapeAllInformation(linkToArticle, logger)

        sqlStatements.extend(prepareSQLStatements(
            linkToArticle,
            informationDict['title'],
            informationDict['authorArray'],
            informationDict['ressortArray'],
            informationDict['wordcount'],
            informationDict['document'],
            informationDict['date']
        ))

    logger.info('Execute SQL')

    executeSQL(sqlStatements, con, cur)
    closeConnectionToDB(con, cur)

    logger.info('Terminate scraper')

    analyzeNewData()

    logger.info('Terminate application')


if __name__ == '__main__':
    main()
