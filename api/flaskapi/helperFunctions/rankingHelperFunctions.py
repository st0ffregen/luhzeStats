from flask import Response
from flask import g
import json
import math

# szenario: wenig aktive Person: ZeitZumLetztenArtikel=120*-0.5=-60, ArtikelAnzahl=10*5=50, CPD=150*1=150, insgesamt = 140
# szenario: sehr aktive Person: ZeitZumLetztenArtikel=15*-0.5=-7, ArtikelAnzahl=35*5=175, CPD=400*1=400, insgesamt = 400

rankingTimeSinceLastArticleWeight = 1.4
rankingCharactersPerDayWeight = 1.4
rankingArticlesCountWeight = 1.2


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


def getDistinctAuthorIdAndName():
    g.g.cur.execute(
        'SELECT distinct(ar.authorId), au.name  from articles ar join authors au on ar.authorId=au.id')
    return g.g.cur.fetchall()


def getWrittenCharacters(authorId, daysBackInTime):
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

    writtenCharacters = getWrittenCharacters(authorId, daysBackInTime)

    if writtenCharacters is None:
        return None

    daysSinceFirstArticle = getDaysSinceFirstArticle(authorId, daysBackInTime)
    daysSinceLastArticle = getDaysSinceLastArticle(authorId, daysBackInTime)
    articleCount = getArticleCount(authorId, daysBackInTime)

    writtenCharactersTwoMonthsBefore = getWrittenCharacters(authorId, daysBackInTime + 60)

    if writtenCharactersTwoMonthsBefore is None:
        writtenCharactersTwoMonthsBefore = 0
        daysSinceFirstArticleTwoMonthsBefore = 0
        daysSinceLastArticleTwoMonthsBefore = 0
        articleCountTwoMonthsBefore = 0
    else:
        daysSinceFirstArticleTwoMonthsBefore = getDaysSinceFirstArticle(authorId, daysBackInTime + 60)
        daysSinceLastArticleTwoMonthsBefore = getDaysSinceLastArticle(authorId, daysBackInTime + 60)
        articleCountTwoMonthsBefore = getArticleCount(authorId, daysBackInTime + 60)

    try:
        writtenCharactersPerDay = round(writtenCharacters / daysSinceFirstArticle)
    except ZeroDivisionError:
        writtenCharactersPerDay = 0

    try:
        writtenCharactersPerDayTwoMonthsBefore = round(writtenCharactersTwoMonthsBefore / daysSinceFirstArticle)
    except ZeroDivisionError:
        writtenCharactersPerDayTwoMonthsBefore = 0

    return {
        'name': authorName,
        'writtenCharactersPerDay': writtenCharactersPerDay,
        'daysSinceFirstArticle': daysSinceFirstArticle,
        'daysSinceLastArticle': daysSinceLastArticle,
        'articleCount': articleCount,
        'writtenCharactersPerDayTwoMonthsBefore': writtenCharactersPerDayTwoMonthsBefore,
        'daysSinceFirstArticleTwoMonthsBefore': daysSinceFirstArticleTwoMonthsBefore,
        'daysSinceLastArticleTwoMonthsBefore': daysSinceLastArticleTwoMonthsBefore,
        'articleCountTwoMonthsBefore': articleCountTwoMonthsBefore,
        'daysBackInTime': daysBackInTime,
        'rankingTsla': tslaFunction(daysSinceLastArticle),
        'rankingCpd': cpdFunction(writtenCharactersPerDay),
        'rankingAc': acFunction(articleCount),
        'rankingTslaTwoMonthsBefore': tslaFunction(daysSinceLastArticleTwoMonthsBefore),
        'rankingCpdTwoMonthsBefore': cpdFunction(writtenCharactersPerDayTwoMonthsBefore),
        'rankingAcTwoMonthsBefore': acFunction(articleCountTwoMonthsBefore)
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



