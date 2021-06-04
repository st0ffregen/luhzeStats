from flask import g
import math

# szenario: wenig aktive Person: ZeitZumLetztenArtikel=120*-0.5=-60, ArtikelAnzahl=10*5=50, CPD=150*1=150, insgesamt = 140
# szenario: sehr aktive Person: ZeitZumLetztenArtikel=15*-0.5=-7, ArtikelAnzahl=35*5=175, CPD=400*1=400, insgesamt = 400

rankingTimeSinceLastArticleWeight = 1.4
rankingCharactersPerDayWeight = 1.4
rankingArticlesCountWeight = 1


def tslaFunction(daysSinceLastArticle):
    # function is using months not days so:
    monthsSinceLastArticle = daysSinceLastArticle / 30.5
    # to avoid math overflow when passing month thats to big
    if monthsSinceLastArticle > 6:  # also letzter artikel älter als 5 monate
        result = (-1.4 / 100) * monthsSinceLastArticle  # linear loosing points over time
    else:
        result = 100 * math.exp(-0.01 * daysSinceLastArticle)

    return result * rankingTimeSinceLastArticleWeight


def cpdFunction(charactersPerDay):
    result = -100 * (math.exp(-0.01 * charactersPerDay) - 1)
    return result * rankingCharactersPerDayWeight


def acFunction(articleCount):
    result = -100 * (math.exp(-0.1 * articleCount) - 1)
    return result * rankingArticlesCountWeight


def getDistinctAuthorIdAndName():
    g.cur.execute(
        'SELECT distinct(ar.authorId), au.name  from articles ar join authors au on ar.authorId=au.id')
    return g.cur.fetchall()


def getWrittenCharacters(authorId, daysBackInTime):
    g.cur.execute(
        'SELECT sum(charcount) from (select distinct(link), d.charCount as charCount, authorId from articles ar join documents d on ar.documentId=d.id where authorId = %s and publishedDate < DATE_ADD(CURDATE(), INTERVAL - %s DAY)) as sub',
        [str(authorId), str(daysBackInTime)])
    charsPerDayResult = g.cur.fetchone()[0]
    if charsPerDayResult == "NULL" or charsPerDayResult is None:  # den autor gabs damals noch nicht
        return None

    return charsPerDayResult


def getDaysSinceFirstArticle(authorId, daysBackInTime):
    g.cur.execute(
        'SELECT DATEDIFF(DATE_ADD(CURDATE(), INTERVAL - %s DAY),MIN(publishedDate))+1 from articles where authorId=%s and publishedDate < DATE_ADD(CURDATE(), INTERVAL - %s DAY)',
        [str(daysBackInTime), str(authorId), str(daysBackInTime)])
    return g.cur.fetchone()[0]


def getDaysSinceLastArticle(authorId, daysBackInTime):
    g.cur.execute(
        'SELECT DATEDIFF(DATE_ADD(CURDATE(), INTERVAL - %s DAY),MAX(publishedDate))+1 from articles where authorId=%s and publishedDate < DATE_ADD(CURDATE(), INTERVAL - %s DAY)',
        [str(daysBackInTime), str(authorId), str(daysBackInTime)])
    return g.cur.fetchone()[0]


def getArticleCount(authorId, daysBackInTime):
    g.cur.execute(
        'SELECT count(distinct link) FROM articles where authorId = %s and publishedDate < DATE_ADD(CURDATE(), INTERVAL - %s DAY)',
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
        writtenCharactersPerDayTwoMonthsBefore = round(
            writtenCharactersTwoMonthsBefore / daysSinceFirstArticleTwoMonthsBefore)
    except ZeroDivisionError:
        writtenCharactersPerDayTwoMonthsBefore = 0

    rankingTsla = tslaFunction(daysSinceLastArticle)
    rankingCpd = cpdFunction(writtenCharactersPerDay)
    rankingAc = acFunction(articleCount)

    rankingScoreNow = round(rankingTsla + rankingCpd + rankingAc)

    rankingTslaTwoMonthsBefore = tslaFunction(daysSinceLastArticleTwoMonthsBefore)
    rankingCpdTwoMonthsBefore = cpdFunction(writtenCharactersPerDayTwoMonthsBefore)
    rankingAcTwoMonthsBefore = acFunction(articleCountTwoMonthsBefore)

    rankingScoreTwoMonhtsBefore = round(
        rankingTslaTwoMonthsBefore + rankingCpdTwoMonthsBefore + rankingAcTwoMonthsBefore)

    rankingScoreDiff = rankingScoreNow - rankingScoreTwoMonhtsBefore

    return {
        'name': authorName,
        # 'writtenCharactersPerDay': writtenCharactersPerDay,
        # 'daysSinceFirstArticle': daysSinceFirstArticle,
        # 'daysSinceLastArticle': daysSinceLastArticle,
        # 'articleCount': articleCount,
        # 'writtenCharactersPerDayTwoMonthsBefore': writtenCharactersPerDayTwoMonthsBefore,
        # 'daysSinceFirstArticleTwoMonthsBefore': daysSinceFirstArticleTwoMonthsBefore,
        # 'daysSinceLastArticleTwoMonthsBefore': daysSinceLastArticleTwoMonthsBefore,
        # 'articleCountTwoMonthsBefore': articleCountTwoMonthsBefore,
        # 'rankingTsla': rankingTsla,
        # 'rankingCpd': rankingCpd,
        # 'rankingAc': rankingAc,
        # 'rankingTslaTwoMonthsBefore': rankingTslaTwoMonthsBefore,
        # 'rankingCpdTwoMonthsBefore': rankingCpdTwoMonthsBefore,
        # 'rankingAcTwoMonthsBefore': rankingAcTwoMonthsBefore,
        # 'daysBackInTime': daysBackInTime,
        'rankingScore': rankingScoreNow,
        'rankingScoreDiff': rankingScoreDiff
    }


def calculateRankingForAllAuthors(daysBackInTime):
    responseDict = []

    distinctAuthorIdAndNameArray = getDistinctAuthorIdAndName()

    for author in distinctAuthorIdAndNameArray:
        singleAuthorValues = calculateValues(author[0], author[1], daysBackInTime)

        if singleAuthorValues is None:
            continue

        responseDict.append(singleAuthorValues)

    return sorted(responseDict, key=lambda x: x['rankingScore'])[::-1]
