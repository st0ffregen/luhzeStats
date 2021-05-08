import os
import sys
from flask import Flask
from flask import jsonify
from flask import Response
from flask import request
from flask import g
import MySQLdb
import json
from flaskapi import app
from flaskapi.helperFunctions.rankingHelperFunctions import calculateRankingForAllAuthors, calculateValues
from flaskapi.helperFunctions.wordOccurenceHelperFunctions import getOccurrences, getTotalOccurrences


minCountOfArticlesAuthorsNeedToHaveToBeDisplayed = 10
minCountOfArticlesRessortsNeedToHaveToBeDisplayed = 10


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


@app.route('/api/oldestArticle', methods=['GET'])
def oldestArticle():
    g.cur.execute('SELECT MIN(created) FROM articles')
    entries = g.cur.fetchall()
    return Response(json.dumps({'oldestArticle': entries[0][0]}, default=str), mimetype='application/json')


@app.route('/api/newestArticle', methods=['GET'])
def newestArticle():
    g.cur.execute('SELECT MAX(created) FROM articles')
    entries = g.cur.fetchall()
    return Response(json.dumps({'newestArticle': entries[0][0]}, default=str), mimetype='application/json')


@app.route('/api/activeMembers', methods=['GET'])
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
        responseDict.append({'ame': authorId[0], 'articles': dateArray})
    return Response(json.dumps(responseDict), mimetype='application/json')


@app.route('/api/ressortTopList', methods=['GET'])
def ressortTopList():
    g.cur.execute(
        'SELECT ressort, count(distinct link) FROM articles GROUP BY ressort HAVING count(distinct link) >= %s ORDER BY 2 DESC',
        [str(minCountOfArticlesRessortsNeedToHaveToBeDisplayed)])
    responseDict = g.cur.fetchall()
    return Response(json.dumps(adjustFormatName(responseDict)), mimetype='application/json')


@app.route('/api/ressortArticlesTimeline', methods=['GET'])
def ressortArticlesTimeline():
    # respone: [{ressort: hopo, articles: [{date: some month, 5},{date: some month, 4}]}]

    g.cur.execute(
        'SELECT ressort, cast(date_format(created,\'%Y-%%m-01\') as date),count(distinct link) as countPerMonth from articles'
        ' where ressort in (select ressort from articles group by ressort having count(distinct link) >= %s) '
        'group by ressort, year(created), month(created)',
        [str(minCountOfArticlesRessortsNeedToHaveToBeDisplayed)])
    fetchedRessortDateCountPerMonthArray = g.cur.fetchall()
    responseDict = []
    ressort = fetchedRessortDateCountPerMonthArray[0][0]  # set ressort to first in fetched list
    monthArray = []
    for e in fetchedRessortDateCountPerMonthArray:
        if ressort == e[0]:
            monthArray.append({'date': e[1], 'count': e[2]})
        else:
            responseDict.append({'ressort': ressort, 'countPerMonth': monthArray})
            monthArray = [{'date': e[1], 'ount': e[2]}]
            ressort = e[0]

        if e == fetchedRessortDateCountPerMonthArray[len(fetchedRessortDateCountPerMonthArray) - 1]:  # if it is last element
            responseDict.append({'ressort': ressort, 'countPerMonth': monthArray})

    return Response(json.dumps(responseDict), mimetype='application/json')


@app.route('/api/topAuthorsPerRessort', methods=['GET'])
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
            name = (e[2] + ' ' + e[3]).strip()
            authorArray.append({'name': name, 'count': e[4]})
        else:
            responseDict.append({'ressort': ressort, 'authors': authorArray[:3]})
            name = (e[2] + ' ' + e[3]).strip()
            authorArray = [{'name': name, 'count': e[4]}]
            ressort = e[0]

        if e == entries[len(entries) - 1]:  # if it is last element
            responseDict.append({'ressort': ressort, 'authors': authorArray[:3]})

    return Response(json.dumps(responseDict), mimetype='application/json')


@app.route('/api/authorTimeline', methods=['GET'])
def authorTimeline():
    g.cur.execute(
        'SELECT ar.authorId, au.name, MIN(created), MAX(created) FROM articles ar join authors au on ar.authorId=au.id GROUP BY authorId HAVING count(distinct link) >= %s ORDER BY count(distinct link) DESC',
        [str(minCountOfArticlesAuthorsNeedToHaveToBeDisplayed)])
    entries = g.cur.fetchall()
    responseDict = []
    for e in entries:
        responseDict.append({'name': e[1], 'min': e[2], 'max': e[3]})

    return Response(json.dumps(responseDict, default=str), mimetype='application/json')


@app.route('/api/articlesTimeline', methods=['GET'])
def articlesTimeline():
    g.cur.execute(
        'select cast(date_format(created,\'Y-%m-01\') as date),count(distinct link) as countPerMonth from articles'
        ' group by year(created),month(created) order by 1 asc')
    responseDict = g.cur.fetchall()

    return Response(json.dumps(adjustFormatDate(responseDict)[::-1]), mimetype='application/json')


@app.route('/api/mostArticlesPerTime', methods=['GET'])
def mostArticlesPerTime():
    g.cur.execute(
        'SELECT ar.authorId, au.name, ROUND(((DATEDIFF(MAX(created),MIN(created)))/count(distinct link)),1) as diff '
        'FROM articles ar join authors au on ar.authorId=au.id GROUP BY authorId HAVING count(distinct link) >= %s ORDER BY diff',
        [str(minCountOfArticlesAuthorsNeedToHaveToBeDisplayed)])
    responseDict = g.cur.fetchall()

    return Response(json.dumps(adjustFormatNameStartOnSecondIndex(responseDict)), mimetype='application/json')


@app.route('/api/authorAverage', methods=['GET'])
def authorAverage():
    g.cur.execute(
        'SELECT ar.authorId, au.name, round(avg(charcount)) as count'
        ' from (select distinct(link), d.charcount as charcount, authorId from articles art join documents d on art.documentId=d.id '
        'where authorId in (select authorId from articles group by authorId having count(distinct link) >=%s)) as ar '
        'join authors au on ar.authorId=au.id group by authorId order by count desc',
        [str(minCountOfArticlesAuthorsNeedToHaveToBeDisplayed)])
    responseDict = g.cur.fetchall()

    return Response(json.dumps(adjustFormatNameStartOnSecondIndex(responseDict)), mimetype='application/json')


@app.route('/api/averageCharactersPerDay', methods=['GET'])
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
        responseDict.append({'name':  e[1], 'count': round(e[2] / res[0])})

    return Response(json.dumps(sorted(responseDict, key=lambda x: x['count'], reverse=True)), mimetype='application/json')


@app.route('/api/ressortAverage', methods=['GET'])
def ressortAverage():
    g.cur.execute(
        'SELECT ressort, round(avg(charcount)) as count from (select distinct(link), d.charcount as charcount,'
        ' ressort from articles ar join documents as d on ar.documentId=d.id where ressort in'
        ' (select ressort from articles group by ressort having count(distinct link) >=%s)) as sub '
        'group by ressort order by count desc', [str(minCountOfArticlesRessortsNeedToHaveToBeDisplayed)])
    responseDict = g.cur.fetchall()

    return Response(json.dumps(adjustFormatName(responseDict)), mimetype='application/json')


@app.route('/api/authorTopList', methods=['GET'])
def authorTopList():
    g.cur.execute(
        'SELECT ar.authorId, au.name, count(distinct link) FROM articles ar join authors au on ar.authorId=au.id GROUP BY authorId HAVING count(distinct link) >= %s ORDER BY 4 DESC', [str(minAuthor)])
    responseDict = g.cur.fetchall()

    return Response(json.dumps(adjustFormatNameStartOnSecondIndex(responseDict)), mimetype='application/json')


@app.route('/api/ressortTimeline', methods=['GET'])
def ressortTimeline():
    g.cur.execute(
        'SELECT ressort, MIN(created), MAX(created) FROM articles GROUP BY ressort ORDER BY count(distinct link) DESC')
    entries = g.cur.fetchall()
    responseDict = []
    for e in entries:
        responseDict.append({'name': e[0], 'min': e[1], 'max': e[2]})

    return Response(json.dumps(responseDict), mimetype='application/json')


@app.route('/api/ranking', methods=['GET'])
def ranking():
    daysBackInTime = request.args.get('daysBackInTime', type=int)
    if daysBackInTime is None:
        return jsonify('no integer daysBackInTime parameter given for ranking endpoint')

    return Response(json.dumps(calculateRankingForAllAuthors(daysBackInTime)), mimetype='application/json')


@app.route('/api/singleRanking', methods=['GET'])
def singleRanking():
    daysBackInTime = request.args.get('daysBackInTime', type=int)
    name = request.args.get('name', type=str)
    if daysBackInTime is None or name is None:
        return jsonify('no daysBackInTime or name parameter given for singleRanking endpoint')

    g.cur.execute('SELECT distinct(ar.authorId), au.name  from articles ar join authors au on ar.authorId=au.id where au.name = %s', [name])
    authorId = g.cur.fetchone()[0]

    return calculateValues(authorId, name, daysBackInTime)


@app.route('/api/minAndMaxYearAndQuarter', methods=['GET'])
def minYearAndQuarter():
    g.cur.execute('SELECT MIN(yearAndQuarter), MAX(yearAndQuarter) from wordOccurrenceOverTheQuarters')
    res = g.cur.fetchone()
    return Response(json.dumps({'minYearAndQuarter': res[0], 'maxYearAndQuarter': res[1]}), mimetype='application/json')


@app.route('/api/maxYearAndQuarter', methods=['GET'])
def maxYearAndQuarter():
    g.cur.execute('SELECT MAX(yearAndQuarter) from wordoccurrenceOverTheQuarters')
    return Response(json.dumps({'maxYearAndQuarter': g.cur.fetchone()[0]}), mimetype='application/json')


@app.route('/api/wordOccurrence', methods=['GET'])
def wordOccurrence():

    word = request.args.get('word', type=str)
    if word is  None:
        return jsonify('no string word parameter given for wordOccurrence endpoint')

    word = word.upper()
    responseDict = []


    for word in word.split('+++'):
        occurrences = getOccurrences(word, responseDict)
        if occurrences is None:
            continue

        responseDict.append(occurrences)

    if len(responseDict) == 0:
        return jsonify('Error. The word ' + word + ' does not exist.')

    return Response(json.dumps(sorted(responseDict, key=lambda x: x['yearAndQuarter'])), mimetype='application/json')


@app.route('/api/autocomplete', methods=['GET'])
def totalWordOccurrence():

    word = request.args.get('word', type=str)
    if word is None:
        return jsonify('no string word parameter given for totalWordOccurrence endpoint')

    word = word.upper()
    responseDict = []

    if '+++' in word:
        for word in word.split('+++'):
            responseDict.append(getTotalOccurrences(word))


    return Response(json.dumps(responseDict),  mimetype='application/json')


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

