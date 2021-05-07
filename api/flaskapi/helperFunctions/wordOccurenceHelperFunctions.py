from flask import g


def getOccurrences(word, responseDict):
    if word == '':
        return None

    g.cur.execute(
        'SELECT yearAndQuarter, occurrencePerWords, occurrence FROM wordOccurrenceOverTheQuarters WHERE word = %s',
        [word])
    entries = g.cur.fetchall()

    if entries is None or len(entries) == 0:
        return None

    for e in entries:
        if len(responseDict) > 0:
            # wenn es den result array schon mit werten gibt search in result array for same yearAndQuarter
            # wenn aber das spezifische yearAndQuarter noch nicht gibt wird es neu hinzugefügt -> found variable
            found = False
            for yearAndQuarterEntry in responseDict:
                if yearAndQuarterEntry['yearAndQuarter'] == e[0]:
                    found = True
                    yearAndQuarterEntry['occurrencePerWords'] += e[1]  # aufaddieren
                    yearAndQuarterEntry['occurrence'] += e[2]  # aufaddieren
            if not found:
                # muss dann im frontend nach datum sortiert werden
                responseDict.append(
                    {'yearAndQuarter': e[0], 'occurrencePerWords': e[1], 'occurrence': e[2]})
        else:
            responseDict.append(
                {'yearAndQuarter': e[0], 'occurrencePerWords': e[1], 'occurrence': e[2]})


def getTotalOccurrences(word):
    responseDict = []

    if word == '':
        return None

    g.cur.execute(
        'SELECT word, occurrencePerWords, occurrence, totalWordCount FROM totalWordoccurrence WHERE BINARY word like CONCAT(%s,\'%%\') order by occurrencePerWords desc limit 5',
        [ecscapeSpecialCharacters(word)])
    entries = g.cur.fetchall()

    if entries is None or len(entries) == 0:
        return None

    for e in entries:
        if e[0] == word:
            dictToBeExtended = [{'word': word, 'occurrencePerWords': e[1], 'occurrence': e[2]}]
            responseDict = dictToBeExtended.extend(responseDict)
        else:
            responseDict.append({'word': word, 'occurrencePerWords': e[1], 'occurrence': e[2]})

    return responseDict

def ecscapeSpecialCharacters(wordToEscapeCharactersIn):
    # die methode escapet im string special charcters in der mysql like funktion
    # das ist % welches wildcard fuer mehrere zeichen ist und _ was fuer ein zeichen ist
    specialCharactersInMySQL = ['_', '%']
    if wordToEscapeCharactersIn is not None and wordToEscapeCharactersIn != '':
        return wordToEscapeCharactersIn.replace('_', '\_').replace('%', '\%')

