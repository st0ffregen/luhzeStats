from flask import Flask
from flask import jsonify
from flask import Response
from flask import request
from flask import g
import MySQLdb
import json
import os
from api import app

minCountOfArticlesAuthorsNeedToHaveToBeDisplayed = 10
minCountOfArticlesRessortsNeedToHaveToBeDisplayed = 10



@app.route('/date', methods=['GET'])
def date():
    g.cur.execute('SELECT lastModifiedFiles from lastmodified')
    return Response(json.dumps({'date': g.cur.fetchone()[0].strftime('%Y-%m-%d %H:%M:%S')}), mimetype='application/json')


@app.route('/minAuthor', methods=['GET'])
def minAuthor():
    return Response(json.dumps({'minAuthor' : minCountOfArticlesAuthorsNeedToHaveToBeDisplayed}), mimetype='application/json')


@app.route('/oldestArticle',methods=['GET'])
def oldestArticle():
    g.cur.execute('SELECT MIN(created) FROM articles')
    entries = g.cur.fetchall()
    return Response(json.dumps({'oldestArticle': entries[0][0]}, default=str), mimetype='application/json')


@app.route('/newestArticle',methods=['GET'])
def newestArticle():
    g.cur.execute('SELECT MAX(created) FROM articles')
    entries = g.cur.fetchall()
    return Response(json.dumps({'newestArticle': entries[0][0]}, default=str), mimetype='application/json')


@app.route('/activeMembers', methods=['GET'])
def activeMembers():
    g.cur.execute('SELECT authorId FROM articles GROUP BY authorId')
    authorIdArray = g.cur.fetchall()
    responseDict = []
    for authorId in authorIdArray:
        g.cur.execute('SELECT created FROM articles WHERE authorId =%s GROUP BY link', [authorId[0]])
        fetchedDateArray = g.cur.fetchall()
        dateArray = []
        for d in fetchedDateArray:
            dateArray.append(d[0].strftime('%Y-%m-%d %H:%M:%S'))
        responseDict.append({"name": authorId[0], "articles": dateArray})
    return Response(json.dumps(responseDict), mimetype='application/json')


@app.route('/ressortTopList', methods=['GET'])
def ressortTopList():
    g.cur.execute(
        'SELECT ressort, count(distinct link) FROM articles GROUP BY ressort HAVING count(distinct link) >= %s ORDER BY 2 DESC',
        [str(minCountOfArticlesRessortsNeedToHaveToBeDisplayed)])
    responseDict = g.cur.fetchall()
    return Response(json.dumps(adjustFormatName(responseDict)), mimetype='application/json')


@app.route('/ressortArticlesTimeline', methods=['GET'])
def ressortArticlesTimeline():
    # respone: [{ressort: hopo, articles: [{date: some month, 5},{date: some month, 4}]}]

    g.cur.execute(
        'SELECT ressort, cast(date_format(created,"%%Y-%%m-01") as date),count(distinct link) as countPerMonth from articles'
        ' where ressort in (select ressort from articles group by ressort having count(distinct link) >= %s) '
        'group by ressort, year(created), month(created)',
        [str(minCountOfArticlesRessortsNeedToHaveToBeDisplayed)])
    fetchedRessortDateCountPerMonthArray = g.cur.fetchall()
    responseDict = []
    ressort = fetchedRessortDateCountPerMonthArray[0][0]  # set ressort to first in fetched list
    monthArray = []
    for e in fetchedRessortDateCountPerMonthArray:
        if ressort == e[0]:
            monthArray.append({"date": e[1], "count": e[2]})
        else:
            responseDict.append({"ressort": ressort, "countPerMonth": monthArray})
            monthArray = [{"date": e[1], "count": e[2]}]
            ressort = e[0]

        if e == fetchedRessortDateCountPerMonthArray[len(fetchedRessortDateCountPerMonthArray) - 1]:  # if it is last element
            responseDict.append({"ressort": ressort, "countPerMonth": monthArray})

    return Response(json.dumps(responseDict), mimetype='application/json')


@app.route('/topAuthorsPerRessort', methods=['GET'])
def topAuthorsPerRessort():
    # response: [{ressort: hopo, authors: [{name: theresa, count:5},{name: someone, count:2}]}]
    g.cur.execute(
        'SELECT ressort, ar.authorId, au.firstName, au.lastName, count(link) as count '
        'from articles ar join authors au on ar.authorId=au.id where ressort in'
        ' (select ressort from articles group by ressort having count(distinct link) >= %s) '
        'group by ressort, authorId having count >= 5 order by 1 asc,5 desc',
        [str(minCountOfArticlesRessortsNeedToHaveToBeDisplayed)])
    entries = g.cur.fetchall()
    responseDict = []
    ressort = entries[0][0]  # set ressort to first in fetched list
    authorArray = []
    for e in entries:
        if ressort == e[0]:
            name = (e[2] + " " + e[3]).strip()
            authorArray.append({"name": name, "count": e[4]})
        else:
            responseDict.append({"ressort": ressort, "authors": authorArray[:3]})
            name = (e[2] + " " + e[3]).strip()
            authorArray = [{"name": name, "count": e[4]}]
            ressort = e[0]

        if e == entries[len(entries) - 1]:  # if it is last element
            responseDict.append({"ressort": ressort, "authors": authorArray[:3]})

    return Response(json.dumps(responseDict), mimetype='application/json')


@app.route('/authorTimeline', methods=['GET'])
def authorTimeline():
    g.cur.execute(
        'SELECT ar.authorId, au.name, MIN(created), MAX(created) FROM articles ar join authors au on ar.authorId=au.id GROUP BY authorId HAVING count(distinct link) >= %s ORDER BY count(distinct link) DESC',
        [str(minCountOfArticlesAuthorsNeedToHaveToBeDisplayed)])
    entries = g.cur.fetchall()
    responseDict = []
    for e in entries:
        responseDict.append({"name": e[1], "min": e[2], "max": e[3]})

    return Response(json.dumps(responseDict, default=str), mimetype='application/json')


@app.route('/articlesTimeline', methods=['GET'])
def articlesTimeline():
    g.cur.execute(
        'select cast(date_format(created,"%Y-%m-01") as date),count(distinct link) as countPerMonth from articles'
        ' group by year(created),month(created) order by 1 asc')
    responseDict = g.cur.fetchall()

    return Response(json.dumps(adjustFormatDate(responseDict)[::-1]), mimetype='application/json')


@app.route('/mostArticlesPerTime', methods=['GET'])
def mostArticlesPerTime():
    g.cur.execute(
        'SELECT ar.authorId, au.name, ROUND(((DATEDIFF(MAX(created),MIN(created)))/count(distinct link)),1) as diff '
        'FROM articles ar join authors au on ar.authorId=au.id GROUP BY authorId HAVING count(distinct link) >= %s ORDER BY diff',
        [str(minCountOfArticlesAuthorsNeedToHaveToBeDisplayed)])
    responseDict = g.cur.fetchall()

    return Response(json.dumps(adjustFormatNameStartOnSecondIndex(responseDict)), mimetype='application/json')


@app.route('/authorAverage', methods=['GET'])
def authorAverage():
    g.cur.execute(
        'SELECT ar.authorId, au.name, round(avg(charcount)) as count'
        ' from (select distinct(link), d.charcount as charcount, authorId from articles art join documents d on art.documentId=d.id '
        'where authorId in (select authorId from articles group by authorId having count(distinct link) >=%s)) as ar '
        'join authors au on ar.authorId=au.id group by authorId order by count desc',
        [str(minCountOfArticlesAuthorsNeedToHaveToBeDisplayed)])
    responseDict = g.cur.fetchall()

    return Response(json.dumps(adjustFormatNameStartOnSecondIndex(responseDict)), mimetype='application/json')


@app.route('/averageCharactersPerDay',methods=['GET'])
def averageCharactersPerDay():
    g.cur.execute(
        'SELECT ar.authorId, au.name, sum(charcount) as count from '
        '(select distinct(link), d.charcount as charcount, authorId from articles art join documents d on art.documentId=d.id '
        'where authorId in (select authorId from articles group by authorId having count(distinct link) >= %s )) as ar '
        'join authors as au on ar.authorId=au.id group by authorId order by count desc', [str(minCountOfArticlesAuthorsNeedToHaveToBeDisplayed)])
    entries = g.cur.fetchall()
    responseDict = []
    for e in entries:
        g.cur.execute('SELECT DATEDIFF(MAX(created),MIN(created))+1 as average from articles where authorId=%s',[str(e[0])])
        res = g.cur.fetchone()
        responseDict.append({"name":  e[1], "count": round(e[2] / res[0])})

    return Response(json.dumps(sorted(responseDict, key=lambda x: x['count'], reverse=True)), mimetype='application/json')


@app.route('/ressortAverage', methods=['GET'])
def ressortAverage():
    g.cur.execute(
        'SELECT ressort, round(avg(charcount)) as count from (select distinct(link), d.charcount as charcount,'
        ' ressort from articles ar join documents as d on ar.documentId=d.id where ressort in'
        ' (select ressort from articles group by ressort having count(distinct link) >=%s)) as sub '
        'group by ressort order by count desc', [str(minCountOfArticlesRessortsNeedToHaveToBeDisplayed)])
    responseDict = g.cur.fetchall()

    return Response(json.dumps(adjustFormatName(responseDict)), mimetype='application/json')


@app.route('/authorTopList', methods=['GET'])
def authorTopList():
    g.cur.execute(
        'SELECT ar.authorId, au.name, count(distinct link) FROM articles ar join authors au on ar.authorId=au.id GROUP BY authorId HAVING count(distinct link) >= %s ORDER BY 4 DESC', [str(minAuthor)])
    responseDict = g.cur.fetchall()

    return Response(json.dumps(adjustFormatNameStartOnSecondIndex(responseDict)), mimetype='application/json')


@app.route('/ressortTimeline', methods=['GET'])
def ressortTimeline():
    g.cur.execute(
        'SELECT ressort, MIN(created), MAX(created) FROM articles GROUP BY ressort ORDER BY count(distinct link) DESC')
    entries = g.cur.fetchall()
    responseDict = []
    for e in entries:
        responseDict.append({"name": e[0], "min": e[1], "max": e[2]})

    return Response(json.dumps(responseDict), mimetype='application/json')


# for all authors

def getRankingForAllAuthors(backInTime):
    con = connectToDB()
    with con:
        g.cur = con.g.cursor()
        g.cur.execute('SELECT a.firstName, a.lastName, r.charsPerDay, r.daysSinceFirstArticle, r.daysSinceLastArticle,'
                    ' r.articleCount, r.charsPerDayBackInTime, r.daysSinceFirstArticleBackInTime,'
                    ' r.daysSinceLastArticleBackInTime, r.articleCountBackInTime '
                    'FROM ranking r join authors a on r.authorId=a.id WHERE backInTime=%s', [backInTime])
        entries = g.cur.fetchall()

        if entries is None or len(entries) == 0:
            print("no entries in db for backInTime = " + str(backInTime))
            g.cur.close()
            return jsonify("no entries in db for backInTime = " + str(backInTime))
        else:
            response = [];
            for entry in entries:
                response.append({'firstName': entry[0], 'lastName': entry[1], 'charsPerDay': entry[2],
                            'daysSinceFirstArticle': entry[3],
                            'daysSinceLastArticle': entry[4], 'articleCount': entry[5], 'charsPerDayBackInTime': entry[6],
                            'daysSinceFirstArticleBackInTime': entry[7], 'daysSinceLastArticleBackInTime': entry[8],
                            'articleCountBackInTime': entry[9], 'backInTime': backInTime})
            g.cur.close()
            return Response(json.dumps(response), mimetype='application/json')

@app.route('/json/rankingDefault', methods=['GET'])
def ranking():
    return getRankingForAllAuthors(0)

@app.route('/json/rankingMonth', methods=['GET'])
def rankingMonth():
    return getRankingForAllAuthors(1)

@app.route('/json/rankingYear', methods=['GET'])
def rankingYear():
    return getRankingForAllAuthors(12)

@app.route('/json/rankingTwoYears', methods=['GET'])
def rankingTwoYears():
    return getRankingForAllAuthors(24)

@app.route('/json/rankingFiveYears', methods=['GET'])
def rankingFiveYears():
    return getRankingForAllAuthors(60)

# for single authors:

def getRankingForSingleAuthor(backInTime, firstName, lastName):
    con = connectToDB()
    with con:
        g.cur = con.g.cursor()
        g.cur.execute('SELECT a.firstName, a.lastName, r.charsPerDay, r.daysSinceFirstArticle, r.daysSinceLastArticle,'
                    ' r.articleCount, r.charsPerDayBackInTime, r.daysSinceFirstArticleBackInTime,'
                    ' r.daysSinceLastArticleBackInTime, r.articleCountBackInTime '
                    'FROM ranking r join authors a on r.authorId=a.id WHERE backInTime=%s and a.firstName=%s and a.lastName=%s', [backInTime, firstName, lastName])
        entry = g.cur.fetchone()

        if entry is None or len(entry) == 0:
            name = (firstName + lastName).strip()
            print("no entries in db for " + name + " with backInTime = " + str(backInTime))
            g.cur.close()
            return jsonify("no entries in db for " + name + " with backInTime = " + str(backInTime))
        else:
            g.cur.close()
            response = {'firstName':entry[0], 'lastName':entry[1], 'charsPerDay':entry[2], 'daysSinceFirstArticle':entry[3],
                        'daysSinceLastArticle':entry[4], 'articleCount':entry[5], 'charsPerDayBackInTime':entry[6],
                        'daysSinceFirstArticleBackInTime':entry[7], 'daysSinceLastArticleBackInTime':entry[8],
                        'articleCountBackInTime':entry[9], 'backInTime': backInTime}
            return Response(json.dumps(response), mimetype='application/json')


@app.route('/json/singleRankingDefault', methods=['GET'])
def singleRanking():
    if 'firstName' and 'lastName' in request.args:
        return getRankingForSingleAuthor(0,request.args['firstName'],request.args['lastName'])

@app.route('/json/singleRankingMonth', methods=['GET'])
def singleRankingMonth():
    if 'firstName' and 'lastName' in request.args:
        return getRankingForSingleAuthor(1, request.args['firstName'], request.args['lastName'])

@app.route('/json/singleRankingYear', methods=['GET'])
def singleRankingYear():
    if 'firstName' and 'lastName' in request.args:
        return getRankingForSingleAuthor(12, request.args['firstName'], request.args['lastName'])

@app.route('/json/singleRankingTwoYears', methods=['GET'])
def singleRankingTwoYears():
    if 'firstName' and 'lastName' in request.args:
        return getRankingForSingleAuthor(24, request.args['firstName'], request.args['lastName'])

@app.route('/json/singleRankingFiveYears', methods=['GET'])
def singleRankingFiveYears():
    if 'firstName' and 'lastName' in request.args:
        return getRankingForSingleAuthor(60, request.args['firstName'], request.args['lastName'])

@app.route('/json/minAndMaxYearAndQuarter', methods=['GET'])
def minYearAndQuarter():
    con = connectToDB()
    with con:
        g.cur = con.g.cursor()
        g.cur.execute('SELECT MIN(yearAndQuarter), MAX(yearAndQuarter) from wordOcg.curenceOverTheQuarters')
        res = g.cur.fetchone()
        g.cur.close()
        return Response(json.dumps({'minYearAndQuarter': res[0], 'maxYearAndQuarter': res[1]}), mimetype='application/json')

@app.route('/json/maxYearAndQuarter', methods=['GET'])
def maxYearAndQuarter():
    con = connectToDB()
    with con:
        g.cur = con.g.cursor()
        g.cur.execute('SELECT MAX(yearAndQuarter) from wordOcg.curenceOverTheQuarters')
        return Response(json.dumps({'maxYearAndQuarter': g.cur.fetchone()[0]}), mimetype='application/json')

@app.route('/json/wordOcg.curence', methods=['GET'])
def wordOcg.curence():
    # read in word
    if 'word' in request.args:
        word = request.args['word'].upper()
        con = connectToDB()
        result = []

        with con:

            g.cur = con.g.cursor()
            if "+++" in word:
                wordsToFetchArray = word.split("+++")

                for w in wordsToFetchArray:

                    if w == "": #passiert gerade dann wenn nach dem +++ nichts eingegeben wurde
                        continue

                    g.cur.execute(
                        'SELECT yearAndQuarter, ocg.curencePerWords, ocg.curence FROM wordOcg.curenceOverTheQuarters WHERE word = %s',
                        [w])
                    ocg.curences = g.cur.fetchall()

                    if ocg.curences is None or len(ocg.curences) == 0:
                        continue

                    for entry in ocg.curences:
                        if len(result) > 0:
                            #wenn es den result array schon mit werten gibt search in result array for same yearAndQuarter
                            # wenn aber das spezifische yearAndQuarter noch nicht gibt wird es neu hinzugefügt -> found variable
                            found = False
                            for yearAndQuarterEntry in result:
                                if yearAndQuarterEntry['yearAndQuarter'] == entry[0]:
                                    found = True
                                    yearAndQuarterEntry['ocg.curencePerWords'] += entry[1] # aufaddieren
                                    yearAndQuarterEntry['ocg.curence'] += entry[2] # aufaddieren
                            if not found:
                                # muss dann im frontend nach datum sortiert werden
                                result.append(
                                    {'yearAndQuarter': entry[0], 'ocg.curencePerWords': entry[1], 'ocg.curence': entry[2]})
                        else:
                            result.append(
                                {'yearAndQuarter': entry[0], 'ocg.curencePerWords': entry[1], 'ocg.curence': entry[2]})

            else:

                g.cur.execute('SELECT yearAndQuarter, ocg.curencePerWords, ocg.curence FROM wordOcg.curenceOverTheQuarters WHERE word = %s', [word])
                ocg.curences = g.cur.fetchall()

                if ocg.curences is None or len(ocg.curences) == 0:
                    return jsonify("Error. The word " + word + " does not exist.")

                for entry in ocg.curences:
                    result.append({'yearAndQuarter': entry[0], 'ocg.curencePerWords': entry[1], 'ocg.curence': entry[2]})

            g.cur.close()
            return Response(json.dumps(sorted(result, key=lambda x: x['yearAndQuarter'])),  mimetype='application/json')
    else:
        return jsonify("Error. No word provided. Please specify a word")


@app.route('/json/autocomplete', methods=['GET'])
def totalWordOcg.curence():
    # read in word
    if 'word' in request.args:
        word = request.args['word'].upper()
        con = connectToDB()
        with con:
            g.cur = con.g.cursor()

            if "+++" in word:
                wordsToFetchArray = word.split("+++")
                result = []
                for w in wordsToFetchArray:

                    restOfResult = []  # gibt quasi ein first result das ist das wort was eigeben wurde, falls vorhanden in der db, nach oben zu schieben auch wenn es weniger treffer als andere hat

                    if w == "": #passiert gerade dann wenn nach dem +++ nichts eingegeben wurde
                        continue

                    g.cur.execute(
                        'SELECT word, ocg.curencePerWords, ocg.curence, totalWordCount FROM totalWordOcg.curence WHERE BINARY word like CONCAT(%s,\'%%\') order by ocg.curencePerWords desc limit 5',
                        [ecscapeSpecialCharacters(w)])  # escape das % mit einem weiteren %
                    occ = g.cur.fetchall()

                    if len(result) > 0:
                        for entry in occ:
                            if entry[0] == w:
                                result[0]['ocg.curencePerWords'] += entry[1]
                                result[0]['ocg.curence'] += entry[2]
                            else:
                                restOfResult.append({'word': word.split(w)[0] + entry[0], 'ocg.curencePerWords': result[0]['ocg.curencePerWords'] + entry[1], 'ocg.curence': result[0]['ocg.curence'] + entry[2]})
                    else: # first word in wordsToFetchArray
                        for entry in occ:
                            if entry[0] == w:
                                result = [{'word': word, 'ocg.curencePerWords': entry[1], 'ocg.curence': entry[2]}]
                            else:
                                restOfResult.append({'word': word, 'ocg.curencePerWords': entry[1], 'ocg.curence': entry[2]})
            else:
                result = []
                restOfResult = []  # gibt quasi ein first result das ist das wort was eigeben wurde, falls vorhanden in der db, nach oben zu schieben auch wenn es weniger treffer als andere hat

                g.cur.execute('SELECT word, ocg.curencePerWords, ocg.curence, totalWordCount FROM totalWordOcg.curence WHERE BINARY word like CONCAT(%s,\'%%\') order by ocg.curencePerWords desc limit 5', [ecscapeSpecialCharacters(word)]) # escape das % mit einem weiteren %
                occ = g.cur.fetchall()

                for w in occ:
                    if w[0] == word:
                        result = [{'word': w[0], 'ocg.curencePerWords': w[1], 'ocg.curence': w[2]}]
                    else:
                        restOfResult.append({'word': w[0], 'ocg.curencePerWords': w[1], 'ocg.curence': w[2]})

            result.extend(restOfResult)
            g.cur.close()
            return Response(json.dumps(result),  mimetype='application/json')

    else:
        return jsonify("Error. No word filed provided. Please specify a word")


def ecscapeSpecialCharacters(wordToEscapeCharactersIn):
    # die methode escapet im string special charcters in der mysql like funktion
    # das ist % welches wildcard fuer mehrere zeichen ist und _ was fuer ein zeichen ist
    specialCharactersInMySQL = ['_', '%']
    if wordToEscapeCharactersIn is not None and wordToEscapeCharactersIn != "":
        return wordToEscapeCharactersIn.replace("_","\_").replace("%", "\%")


def adjustFormatDate(entries):
    arr = []
    for e in entries:
        arr.append({'date': e[0], 'count': str(e[1])})
    return arr


def adjustFormatName(entries):
    arr = []
    for e in entries:
        arr.append({'name': e[0], 'count': str(e[1])})
    return arr


def adjustFormatNameStartOnSecondIndex(entries):
    arr = []
    for e in entries:
        arr.append({'name': e[1], 'count': str(e[2])})
    return arr

