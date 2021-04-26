#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from scraper.analyzeLuhze import analyzeNewData
from scraper.scrapingFunctions import scrapeRessort, scrapeAuthor, scrapeTitle, scrapeDate, scrapeWordcountAndText, \
    readInSite, getLinksToSingleArticlesFromOverviewPages
from scraper.databaseFunctions import executeSQL, connectToDB, closeConnectionToDB
import os

luhzeArticleOverviewPageUrl = 'https://www.luhze.de/page/'
numberOfOverviewPagesToScrapeAgain = os.environ['NUMBERS_OF_OVERVIEW_PAGES_TO_SCRAPE_AGAIN']


def prepareSQLStatements(link, title, authorArray, ressortArray, wordcount, document, date):

    # there are cases where a ressort, author etc. may be removed after a while so its most safe to delete all affected rows first
    preparedSQLStatements = ['DELETE FROM articles WHERE link=%s', [link]]

    preparedSQLStatements.append(['INSERT INTO documents VALUES(%s,%s,%s,%s,%s)',
                                  [None, document, wordcount, date, datetime.now().strftime('%Y-%m-%d %H:%M:%S')]])

    for author in authorArray:
        preparedSQLStatements.append(['INSERT IGNORE INTO authors VALUES(%s,%s,%s)', [None, author]])
        for ressort in ressortArray:
            preparedSQLStatements.append([
                'INSERT INTO articles VALUES(%s,%s,%s,(SELECT id FROM authors WHERE name=%s),%s,%s, (SELECT id FROM documents WHERE document=%s))',
                [None, link, title, author, ressort, date, document]])

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

    return {'titel': title,
            'authorArray': authorArray,
            'ressortArray': ressortArray,
            'date': date,
            'wordcount': wordcount,
            'document': document}


def main():
    print('starting gathering')
    print(datetime.now())
    con = connectToDB()
    cur = con.cursor()

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

    executeSQL(sqlStatements, cur, con)
    closeConnectionToDB(con, cur)

    analyzeNewData(cur)


if __name__ == '__main__':
    main()
