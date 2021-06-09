from flask import g


def getOccurrences(word):
    responseDict = []

    g.cur.execute('SELECT year, quarter, occurrence, quarterWordCount FROM wordOccurrence WHERE word = %s '
                  'AND year >= 2015 EXCEPT SELECT year, quarter, occurrence, quarterWordCount FROM wordOccurrence '
                  'WHERE word = %s and year = 2015 and quarter = 1', [word, word])
    entries = g.cur.fetchall()

    if entries is None or len(entries) == 0:
        return None

    for row in entries:
        if row[2] == 0:
            occurrenceRatio = 0
        else:
            occurrenceRatio = round(100000 * row[2]/row[3])

        responseDict.append({'word': word, 'year': row[0], 'quarter': row[1], 'occurrence': round(row[2]), 'quarterWordCount': round(row[3]), 'occurrenceRatio': round(occurrenceRatio)})

    return responseDict


def getTotalOccurrences(word):
    responseDict = []
    wordWithoutSpecialChars = escapeSpecialCharacters(word).upper()

    g.cur.execute(
        'SELECT word, sum(occurrence) FROM wordOccurrence WHERE word like CONCAT(%s,\'%%\') group by word order by 2 desc limit 5',
        [wordWithoutSpecialChars])
    entries = g.cur.fetchall()

    if entries is None or len(entries) == 0:
        return [{'word': word, 'occurrence': 0}]

    for row in entries:
        if row[0] == wordWithoutSpecialChars:
            responseDict = list([{'word': row[0], 'occurrence': int(row[1])}]) + list(responseDict)
        else:
            responseDict.append({'word': row[0], 'occurrence': int(row[1])})

    return responseDict


def escapeSpecialCharacters(wordToEscapeCharactersIn):
    # die methode escapet im string special charcters in der mysql like funktion
    # das ist % welches wildcard fuer mehrere zeichen ist und _ was fuer ein zeichen ist
    specialCharactersInMySQL = ['_', '%']
    if wordToEscapeCharactersIn is not None and wordToEscapeCharactersIn != '':
        return wordToEscapeCharactersIn.replace('_', '\_').replace('%', '\%')

