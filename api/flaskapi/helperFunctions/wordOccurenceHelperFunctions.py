from flask import g


def sumOccurrences(occurrenceDict):
    totalOccurrence = 0
    for row in occurrenceDict:
        totalOccurrence += int(row['occurrence'])

    return totalOccurrence


def getOccurrences(word, wordArray):

    if word == '' or wordArray is None:
        return None

    responseDict = []

    g.cur.execute(
        'SELECT year, quarter, 100000 * sum(occurrence)/quarterWordCount, quarterWordCount , sum(occurrence) '
        'FROM wordOccurrence WHERE word in %s group by year, quarter;',
        [wordArray])
    entries = g.cur.fetchall()

    if entries is None or len(entries) == 0:
        return None

    for row in entries:
        occurrenceRatio = row[2]
        if occurrenceRatio is None:
            occurrenceRatio = 0
        responseDict.append({'word': word, 'year': row[0], 'quarter': row[1], 'occurrenceRatio': round(occurrenceRatio), 'occurrence': round(row[4])})

    return responseDict


def getTotalOccurrences(word):
    responseDict = []

    if word == '':
        return None

    g.cur.execute(
        'SELECT word, sum(occurrence) FROM wordOccurrence WHERE BINARY word like CONCAT(%s,\'%%\') group by word order by 2 desc limit 5',
        [ecscapeSpecialCharacters(word)])
    entries = g.cur.fetchall()

    if entries is None or len(entries) == 0:
        return None

    for row in entries:
        if row[0] == word:
            dictToBeExtended = [{'word': word, 'occurrence': row[2]}]
            responseDict = dictToBeExtended.extend(responseDict)
        else:
            responseDict.append({'word': word, 'occurrence': row[2]})

    return responseDict


def ecscapeSpecialCharacters(wordToEscapeCharactersIn):
    # die methode escapet im string special charcters in der mysql like funktion
    # das ist % welches wildcard fuer mehrere zeichen ist und _ was fuer ein zeichen ist
    specialCharactersInMySQL = ['_', '%']
    if wordToEscapeCharactersIn is not None and wordToEscapeCharactersIn != '':
        return wordToEscapeCharactersIn.replace('_', '\_').replace('%', '\%')

