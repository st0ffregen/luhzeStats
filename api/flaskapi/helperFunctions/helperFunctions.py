from flask import g


def createYearAndMonthArray():
    g.cur.execute('SELECT YEAR(MIN(publishedDate)), MONTH(MIN(publishedDate)) FROM articles')
    minDate = g.cur.fetchone()

    g.cur.execute('SELECT YEAR(MAX(publishedDate)), MONTH(MAX(publishedDate)) FROM articles')
    maxDate = g.cur.fetchone()

    monthArray = []
    minYear, minMonth = minDate
    maxYear, maxMonth = maxDate

    for year in range(int(minYear), int(maxYear) + 1):  # +1 da maxYear exklusive Grenze
        monthLimit = 12
        if year == int(maxYear):
            monthLimit = maxMonth
        for month in range(minMonth, monthLimit + 1):  # +1 ist hier wieder exklusiv
            monthArray.append((year, month))
        minMonth = 1  # setzt initquarter wieder auf 1, s.d. die for schleife jetzt von 1 anfängt

    return monthArray


def createYearAndQuarterArray():
    g.cur.execute('SELECT YEAR(MIN(publishedDate)), QUARTER(MIN(publishedDate)) FROM articles')
    minDate = g.cur.fetchone()

    g.cur.execute('SELECT YEAR(MAX(publishedDate)), QUARTER(MAX(publishedDate)) FROM articles')
    maxDate = g.cur.fetchone()

    quarterArray = []
    minYear, minQuarter = minDate
    maxYear, maxQuarter = maxDate

    for year in range(int(minYear), int(maxYear) + 1):  # +1 da maxYear exklusive Grenze
        quarterLimit = 4
        if year == int(maxYear):
            quarterLimit = maxQuarter
        for quarter in range(minQuarter, quarterLimit + 1):  # +1 ist hier wieder exklusiv
            quarterArray.append((year, quarter))
        minQuarter = 1  # setzt initquarter wieder auf 1, s.d. die for schleife jetzt von 1 anfängt

    return quarterArray

