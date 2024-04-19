from flask import jsonify
from flask import Response
from flask import request
from flask import g
import datetime
import json
from flaskapi import app
from flaskapi.helperFunctions.rankingHelperFunctions import calculateRankingForAllAuthors, calculateValues
from flaskapi.helperFunctions.wordOccurenceHelperFunctions import getOccurrences, getTotalOccurrences
from flaskapi.helperFunctions.helperFunctions import createYearAndMonthArray, createYearAndQuarterArray
import pydevd_pycharm

minCountOfArticlesAuthorsNeedToHaveToBeDisplayed = 16
minCountOfArticlesRessortsNeedToHaveToBeDisplayed = 7


@app.route('/api/date', methods=['GET'])
def date():
    g.cur.execute('select max(updatedAt) from ('
                  'select max(updatedAt) as updatedAt from authors union all '
                  'select max(updatedAt) as updatedAt from articles union all '
                  'select max(updatedAt) as updatedAt from wordOccurrence) as subQuery')
    return Response(json.dumps({'date': g.cur.fetchone()[0].strftime('%Y-%m-%d %H:%M:%S')}), mimetype='application/json')


@app.route('/api/minAuthor', methods=['GET'])
def minAuthor():
    return Response(json.dumps({'minAuthor': minCountOfArticlesAuthorsNeedToHaveToBeDisplayed}), mimetype='application/json')


@app.route('/api/minRessort', methods=['GET'])
def minRessort():
    return Response(json.dumps({'minRessort': minCountOfArticlesRessortsNeedToHaveToBeDisplayed}), mimetype='application/json')


@app.route('/api/oldestArticle', methods=['GET'])
def oldestArticle():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    g.cur.execute('SELECT MIN(publishedDate) FROM articles where publishedDate <= %s', [dateBackInTime])
    entries = g.cur.fetchall()
    if len(entries) == 0:
        return jsonify('error: no data for requested date ' + dateBackInTime.strftime('%Y-%m-%d'))

    return Response(json.dumps({'oldestArticle': entries[0][0]}, default=str), mimetype='application/json')


@app.route('/api/newestArticle', methods=['GET'])
def newestArticle():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    g.cur.execute('SELECT MAX(publishedDate) FROM articles where publishedDate <= %s', [dateBackInTime])
    entries = g.cur.fetchall()
    if len(entries) == 0:
        return jsonify('error: no data for requested date ' + dateBackInTime.strftime('%Y-%m-%d'))

    return Response(json.dumps({'newestArticle': entries[0][0]}, default=str), mimetype='application/json')


@app.route('/api/activeMembers', methods=['GET'])
def activeMembers():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    yearAndQuarterArray = createYearAndQuarterArray(dateBackInTime)
    responseDict = []
    for yearAndQuarter in yearAndQuarterArray:
        year, quarter = yearAndQuarter
        g.cur.execute(
            'select cast(date_format(publishedDate,\'%%Y-%%m-01\') as date), count(distinct authorId) from articles where YEAR(publishedDate) = %s and QUARTER(publishedDate) = %s and publishedDate <= %s',
            [year, quarter, dateBackInTime])
        entry = g.cur.fetchone()
        if entry[0] is None:
            entry = (datetime.date(year, (quarter-1) * 3 + 1, 1), 0)

        responseDict.append(entry)

    return Response(json.dumps(adjustFormatDate(responseDict)), mimetype='application/json')


@app.route('/api/activeMembersWithFourArticles', methods=['GET'])
def activeMembersWithFourArticles():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    yearAndQuarterArray = createYearAndQuarterArray(dateBackInTime)
    responseDict = []
    for yearAndQuarter in yearAndQuarterArray:
        year, quarter = yearAndQuarter
        date = datetime.date(year, (quarter-1) * 3 + 1, 1)
        g.cur.execute(
            'select count(*) from (select authorId from articles where YEAR(publishedDate) = %s and QUARTER(publishedDate) = %s and publishedDate <= %s group by authorId having count(link) > 3) as sub',
            [year, quarter, dateBackInTime])
        entry = g.cur.fetchone()

        if entry[0] is None:
            entry = (date, 0)
        else:
            entry = (date, entry[0])

        responseDict.append(entry)

    return Response(json.dumps(adjustFormatDate(responseDict)), mimetype='application/json')


@app.route('/api/ressortTopList', methods=['GET'])
def ressortTopList():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    g.cur.execute(
        'SELECT ressort, count(distinct link) FROM articles where publishedDate <= %s GROUP BY ressort HAVING count(distinct link) >= %s ORDER BY 2 DESC',
        [dateBackInTime, minCountOfArticlesRessortsNeedToHaveToBeDisplayed])
    responseDict = g.cur.fetchall()
    if len(responseDict) == 0:
        return jsonify('error: no data for requested date ' + dateBackInTime.strftime('%Y-%m-%d'))

    return Response(json.dumps(adjustFormatName(responseDict)), mimetype='application/json')


@app.route('/api/ressortArticlesTimeline', methods=['GET'])
def ressortArticlesTimeline():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    # respone: [{ressort: hopo, articles: [{date: some month, 5},{date: some month, 4}]}]
    yearAndMonthArray = createYearAndMonthArray(dateBackInTime)
    responseDict = []
    g.cur.execute('SELECT ressort FROM articles where publishedDate <= %s GROUP BY ressort HAVING count(distinct link) > %s', [dateBackInTime, minCountOfArticlesRessortsNeedToHaveToBeDisplayed])
    allRessorts = g.cur.fetchall()

    if len(allRessorts) == 0:
        return jsonify('error: no data for requested date ' + dateBackInTime.strftime('%Y-%m-%d'))

    for ressort in allRessorts:
        ressortDict = []
        for yearAndMonth in yearAndMonthArray:
            year, month = yearAndMonth
            g.cur.execute(
                'select cast(date_format(publishedDate,\'%%Y-%%m-01\') as date), count(distinct link) from articles where YEAR(publishedDate) = %s and MONTH(publishedDate) = %s and ressort = %s and publishedDate <= %s',
                [year, month, ressort[0], dateBackInTime])
            entry = g.cur.fetchone()
            if entry[0] is None:
                entry = (datetime.date(year, month, 1), 0)
            ressortDict.append(entry)

        responseDict.append({'ressort': ressort[0], 'articles': adjustFormatDate(ressortDict)})

    return Response(json.dumps(responseDict), mimetype='application/json')


@app.route('/api/ressortArticlesTimelineDerivative', methods=['GET'])
def ressortArticlesTimelineDerivative():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    # respone: [{ressort: hopo, articles: [{date: some month, 5},{date: some month, 4}]}]
    yearAndQuarterArray = createYearAndQuarterArray(dateBackInTime)
    responseDict = []
    g.cur.execute('SELECT ressort FROM articles where publishedDate <= %s GROUP BY ressort HAVING count(distinct link) > %s', [dateBackInTime, minCountOfArticlesRessortsNeedToHaveToBeDisplayed])
    allRessorts = g.cur.fetchall()

    if len(allRessorts) == 0:
        return jsonify('error: no data for requested date ' + dateBackInTime.strftime('%Y-%m-%d'))

    for ressort in allRessorts:
        ressortDict = []
        for yearAndQuarter in yearAndQuarterArray:
            year, quarter = yearAndQuarter
            g.cur.execute(
                'select count(distinct link) from articles where YEAR(publishedDate) = %s and QUARTER(publishedDate) = %s and ressort = %s and publishedDate <= %s',
                [year, quarter, ressort[0], dateBackInTime])
            entry = g.cur.fetchone()
            count = entry[0]
            if count is None:
                count = 0

            entry = (datetime.date(year, (quarter-1) * 3 + 1, 1), count)
            ressortDict.append(entry)

        responseDict.append({'ressort': ressort[0], 'articles': adjustFormatDate(ressortDict)})

    return Response(json.dumps(responseDict), mimetype='application/json')


@app.route('/api/topAuthorsPerRessort', methods=['GET'])
def topAuthorsPerRessort():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    # response: [{ressort: hopo, authors: [{name: theresa, count:5},{name: someone, count:2}]}]
    g.cur.execute(
        'SELECT ressort, ar.authorId, au.name, count(link) as count '
        'from articles ar join authors au on ar.authorId=au.id where publishedDate <= %s and ressort in'
        ' (select ressort from articles where publishedDate <= %s group by ressort having count(distinct link) >= %s) '
        'group by ressort, authorId order by 1 asc, 4 desc',
        [dateBackInTime, dateBackInTime, minCountOfArticlesRessortsNeedToHaveToBeDisplayed])
    entries = g.cur.fetchall()
    if len(entries) == 0:
        return jsonify('error: no data for requested date ' + dateBackInTime.strftime('%Y-%m-%d'))

    responseDict = []
    ressort = entries[0][0]  # set ressort to first in fetched list
    authorArray = []
    for e in entries:
        if ressort == e[0]:
            authorArray.append({'name': e[2], 'count': e[3]})
        else:
            responseDict.append({'ressort': ressort, 'authors': authorArray[:3]})
            authorArray = [{'name': e[2], 'count': e[3]}]
            ressort = e[0]

        if e == entries[len(entries) - 1]:  # if it is last element
            responseDict.append({'ressort': ressort, 'authors': authorArray[:3]})

    return Response(json.dumps(responseDict), mimetype='application/json')


@app.route('/api/authorTimeline', methods=['GET'])
def authorTimeline():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    g.cur.execute(
        'SELECT ar.authorId, au.name, MIN(publishedDate), MAX(publishedDate) FROM articles ar join authors au on ar.authorId=au.id where publishedDate <= %s GROUP BY authorId HAVING count(distinct link) >= %s ORDER BY count(distinct link) DESC',
        [dateBackInTime, minCountOfArticlesAuthorsNeedToHaveToBeDisplayed])
    entries = g.cur.fetchall()
    if len(entries) == 0:
        return jsonify('error: no data for requested date ' + dateBackInTime.strftime('%Y-%m-%d'))

    responseDict = []
    for e in entries:
        responseDict.append({'name': e[1], 'min': e[2], 'max': e[3]})

    return Response(json.dumps(responseDict, default=str), mimetype='application/json')


@app.route('/api/articlesTimeline', methods=['GET'])
def articlesTimeline():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    yearAndMonthArray = createYearAndMonthArray(dateBackInTime)
    responseDict = []
    for yearAndMonth in yearAndMonthArray:
        year, month = yearAndMonth
        g.cur.execute(
            'select cast(date_format(publishedDate,\'%%Y-%%m-01\') as date), count(distinct link) from articles where YEAR(publishedDate) = %s and MONTH(publishedDate) = %s and publishedDate <= %s',
            [year, month, dateBackInTime])
        entry = g.cur.fetchone()
        if entry[0] is None:
            entry = (datetime.date(year, month, 1), 0)
        responseDict.append(entry)

    return Response(json.dumps(adjustFormatDate(responseDict)), mimetype='application/json')


@app.route('/api/mostArticlesPerTime', methods=['GET'])
def mostArticlesPerTime():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    g.cur.execute(
        'SELECT ar.authorId, au.name, ROUND(((DATEDIFF(MAX(publishedDate),MIN(publishedDate)))/count(distinct link)),1) as diff '
        'FROM articles ar join authors au on ar.authorId=au.id where publishedDate <= %s GROUP BY authorId HAVING count(distinct link) >= %s ORDER BY diff',
        [dateBackInTime, minCountOfArticlesAuthorsNeedToHaveToBeDisplayed])
    responseDict = g.cur.fetchall()
    if len(responseDict) == 0:
        return jsonify('error: no data for requested date ' + dateBackInTime.strftime('%Y-%m-%d'))

    return Response(json.dumps(adjustFormatNameStartOnSecondIndex(responseDict)), mimetype='application/json')


@app.route('/api/authorAverage', methods=['GET'])
def authorAverage():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    g.cur.execute(
        'SELECT ar.authorId, au.name, round(avg(charCount)) as count '
        'from (select distinct(link), d.charCount as charCount, authorId from articles art join documents d on art.documentId=d.id '
        'where publishedDate <= %s and authorId in (select authorId from articles where publishedDate <= %s group by authorId having count(distinct link) >=%s)) as ar '
        'join authors au on ar.authorId=au.id group by authorId order by count desc',
        [dateBackInTime, dateBackInTime, minCountOfArticlesAuthorsNeedToHaveToBeDisplayed])
    responseDict = g.cur.fetchall()
    if len(responseDict) == 0:
        return jsonify('error: no data for requested date ' + dateBackInTime.strftime('%Y-%m-%d'))

    return Response(json.dumps(adjustFormatNameStartOnSecondIndex(responseDict)), mimetype='application/json')


@app.route('/api/averageCharactersPerDay', methods=['GET'])
def averageCharactersPerDay():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    g.cur.execute(
        'SELECT ar.authorId, au.name, sum(charCount) as count from '
        '(select distinct(link), d.charCount as charCount, authorId from articles art join documents d on art.documentId=d.id '
        'where publishedDate <= %s and authorId in (select authorId from articles where publishedDate <= %s  group by authorId having count(distinct link) >= %s )) as ar '
        'join authors as au on ar.authorId=au.id group by authorId order by count desc', [dateBackInTime, dateBackInTime, minCountOfArticlesAuthorsNeedToHaveToBeDisplayed])
    entries = g.cur.fetchall()
    if len(entries) == 0:
        return jsonify('error: no data for requested date ' + dateBackInTime.strftime('%Y-%m-%d'))
    responseDict = []
    for e in entries:
        g.cur.execute('SELECT DATEDIFF(MAX(publishedDate),MIN(publishedDate)) as average from articles where authorId=%s and publishedDate <= %s', [str(e[0]), dateBackInTime])
        res = g.cur.fetchone()
        responseDict.append({'name':  e[1], 'count': round(e[2] / res[0])})

    return Response(json.dumps(sorted(responseDict, key=lambda x: x['count'], reverse=True)), mimetype='application/json')


@app.route('/api/ressortAverage', methods=['GET'])
def ressortAverage():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    g.cur.execute(
        'SELECT ressort, round(avg(charcount)) as count from (select distinct(link), d.charCount as charCount,'
        ' ressort from articles ar join documents as d on ar.documentId=d.id where publishedDate <= %s and ressort in'
        ' (select ressort from articles where publishedDate <= %s group by ressort having count(distinct link) >=%s)) as sub '
        'group by ressort order by count desc', [dateBackInTime, dateBackInTime, minCountOfArticlesRessortsNeedToHaveToBeDisplayed])
    responseDict = g.cur.fetchall()
    if len(responseDict) == 0:
        return jsonify('error: no data for requested date ' + dateBackInTime.strftime('%Y-%m-%d'))

    return Response(json.dumps(adjustFormatName(responseDict)), mimetype='application/json')


@app.route('/api/authorTopList', methods=['GET'])
def authorTopList():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    g.cur.execute(
        'SELECT ar.authorId, au.name, count(distinct link) as count FROM articles ar join authors au on ar.authorId=au.id where publishedDate <= %s GROUP BY authorId HAVING count(distinct link) >= %s ORDER BY 3 DESC',
        [dateBackInTime, minCountOfArticlesAuthorsNeedToHaveToBeDisplayed])
    responseDict = g.cur.fetchall()
    if len(responseDict) == 0:
        return jsonify('error: no data for requested date ' + dateBackInTime.strftime('%Y-%m-%d'))

    return Response(json.dumps(adjustFormatNameStartOnSecondIndex(responseDict)), mimetype='application/json')


@app.route('/api/ressortTimeline', methods=['GET'])
def ressortTimeline():
    dateBackInTime = datetime.datetime.strptime(request.args.get('dateBackInTime', type=str), '%Y-%m-%d')
    g.cur.execute(
        'SELECT ressort, MIN(publishedDate), MAX(publishedDate) FROM articles where publishedDate <= %s GROUP BY ressort HAVING count(distinct link) >= %s ORDER BY count(distinct link) DESC',
        [dateBackInTime, minCountOfArticlesRessortsNeedToHaveToBeDisplayed])
    entries = g.cur.fetchall()
    if len(entries) == 0:
        return jsonify('error: no data for requested date ' + dateBackInTime.strftime('%Y-%m-%d'))

    responseDict = []
    for e in entries:
        responseDict.append({'name': e[0], 'min': e[1].strftime('%Y-%m-%d %H:%M:%S'), 'max': e[2].strftime('%Y-%m-%d %H:%M:%S')})

    return Response(json.dumps(responseDict), mimetype='application/json')


@app.route('/api/ranking', methods=['GET'])
def ranking():
    dateBackInTime = request.args.get('dateBackInTime', type=str)
    return Response(json.dumps(calculateRankingForAllAuthors(datetime.datetime.strptime(dateBackInTime, '%Y-%m-%d'))), mimetype='application/json')


@app.route('/api/singleRanking', methods=['GET'])
def singleRanking():
    dateBackInTime = request.args.get('dateBackInTime', type=str)
    name = request.args.get('name', type=str)

    g.cur.execute('SELECT distinct(ar.authorId), au.name  from articles ar join authors au on ar.authorId=au.id where au.name = %s', [name])
    authorId = g.cur.fetchone()[0]

    return calculateValues(authorId, name, datetime.datetime.strptime(dateBackInTime, '%Y-%m-%d'))


@app.route('/api/firstYearAndQuarter', methods=['GET'])
def minYearAndQuarter():
    g.cur.execute('SELECT year, quarter from wordOccurrence order by year asc, quarter asc limit 1')
    lastYearAndQuarter = g.cur.fetchone()
    return Response(json.dumps({'firstYear': lastYearAndQuarter[0], 'firstQuarter': lastYearAndQuarter[1]}), mimetype='application/json')


@app.route('/api/lastYearAndQuarter', methods=['GET'])
def maxYearAndQuarter():
    g.cur.execute('SELECT year, quarter from wordOccurrence order by year desc, quarter desc limit 1')
    lastYearAndQuarter = g.cur.fetchone()
    return Response(json.dumps({'lastYear': lastYearAndQuarter[0], 'lastQuarter': lastYearAndQuarter[1]}), mimetype='application/json')


@app.route('/api/wordOccurrence', methods=['GET'])
def wordOccurrence():
    word = request.args.get('word', type=str)
    if word is None or word == '':
        return jsonify('no string word parameter given for wordOccurrence endpoint')

    responseDict = getOccurrences(word)

    if responseDict is None or len(responseDict) == 0:
        return jsonify('Error. The word does not exist.')

    return Response(json.dumps(responseDict), mimetype='application/json')


@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    word = request.args.get('word', type=str)
    if word is None or word == '':
        return jsonify('no string word parameter given for totalWordOccurrence endpoint')

    occurrences = getTotalOccurrences(word)

    return Response(json.dumps(occurrences),  mimetype='application/json')


def adjustFormatDate(entries):
    arr = []
    for e in entries:
        arr.append({'date': e[0].strftime('%Y-%m-%d %H:%M:%S'), 'count': str(e[1])})
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

