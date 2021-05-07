from flask import Response
from flask import g
import json


def getDistinctAuthorIdAndName():
    g.g.cur.execute(
        'SELECT distinct(ar.authorId), au.name  from articles ar join authors au on ar.authorId=au.id')
    return g.g.cur.fetchall()


def getWrittenCharactersPerDay(authorId, daysBackInTime):
    g.g.cur.execute(
        'SELECT sum(charcount) from (select distinct(link), d.charcount as charcount, authorId from articles ar join documents d on ar.documentId=d.id where authorId = %s and created < DATE_ADD(CURDATE(), INTERVAL - %s DAY)) as sub',
        [str(authorId), str(daysBackInTime)])
    charsPerDayResult = g.g.cur.fetchone()[0]
    if charsPerDayResult == "NULL" or charsPerDayResult is None:  # den autor gabs damals noch nicht
        return None

    return charsPerDayResult


def getDaysSinceFirstArticle(authorId, daysBackInTime):
    g.g.cur.execute(
        'SELECT DATEDIFF(DATE_ADD(CURDATE(), INTERVAL - %s DAY),MIN(created))+1 from articles where authorId=%s and created < DATE_ADD(CURDATE(), INTERVAL - %s DAY)',
        [str(daysBackInTime), str(authorId), str(daysBackInTime)])
    return g.g.cur.fetchone()[0]


def getDaysSinceLastArticle(authorId, daysBackInTime):
    g.cur.execute(
        'SELECT DATEDIFF(DATE_ADD(CURDATE(), INTERVAL - %s DAY),MAX(created))+1 from articles where authorId=%s and created < DATE_ADD(CURDATE(), INTERVAL - %s DAY)',
        [str(daysBackInTime), str(authorId), str(daysBackInTime)])
    return g.cur.fetchone()[0]


def getArticleCount(authorId, daysBackInTime):
    g.cur.execute(
        'SELECT count(distinct link) FROM articles where authorId = %s and created < DATE_ADD(CURDATE(), INTERVAL - %s DAY)',
        [str(authorId), str(daysBackInTime)])
    return g.cur.fetchone()[0]


def calculateValues(authorId, authorName, daysBackInTime):

    writtenCharactersPerDay = getWrittenCharactersPerDay(authorId, daysBackInTime)

    if writtenCharactersPerDay is None:
        return None

    daysSinceFirstArticle = getDaysSinceFirstArticle(authorId, daysBackInTime)
    daysSinceLastArticle = getDaysSinceLastArticle(authorId, daysBackInTime)
    articleCount = getArticleCount(authorId, daysBackInTime)

    writtenCharactersPerDayTwoMonthsBefore = getWrittenCharactersPerDay(authorId, daysBackInTime + 60)

    if writtenCharactersPerDayTwoMonthsBefore is None:
        writtenCharactersPerDayTwoMonthsBefore = 0
        daysSinceFirstArticleTwoMonthsBefore = 0
        daysSinceLastArticleTwoMonthsBefore = 0
        articleCountTwoMonthsBefore = 0
    else:
        daysSinceFirstArticleTwoMonthsBefore = getDaysSinceFirstArticle(authorId, daysBackInTime + 60)
        daysSinceLastArticleTwoMonthsBefore = getDaysSinceLastArticle(authorId, daysBackInTime + 60)
        articleCountTwoMonthsBefore = getArticleCount(authorId, daysBackInTime + 60)

    return {
        'name': authorName,
        'writtenCharactersPerDay': round(writtenCharactersPerDay / daysSinceFirstArticle),
        'daysSinceFirstArticle': daysSinceFirstArticle,
        'daysSinceLastArticle': daysSinceLastArticle,
        'articleCount': articleCount,
        'writtenCharactersPerDayTwoMonthsBefore': writtenCharactersPerDayTwoMonthsBefore,
        'daysSinceFirstArticleTwoMonthsBefore': daysSinceFirstArticleTwoMonthsBefore,
        'daysSinceLastArticleTwoMonthsBefore': daysSinceLastArticleTwoMonthsBefore,
        'articleCountTwoMonthsBefore': articleCountTwoMonthsBefore,
        'daysBackInTime': daysBackInTime
    }


def calculateRankingForAllAuthors(daysBackInTime):

    responseDict = []

    distinctAuthorIdAndNameArray = getDistinctAuthorIdAndName()

    for author in distinctAuthorIdAndNameArray:
        singleAuthorValues = calculateValues(author[0], author[1], daysBackInTime)

        if singleAuthorValues is None:
            continue

        responseDict.append(singleAuthorValues)

    return responseDict



