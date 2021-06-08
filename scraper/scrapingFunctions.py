from bs4 import BeautifulSoup
from urllib.request import urlopen

textToBeIgnoredArray = [
    'Hochschuljournalismus wie dieser ist teuer. Dementsprechend schwierig ist es, eine unabhängige, '
    'ehrenamtlich betriebene Zeitung am Leben zu halten. Wir brauchen also eure Unterstützung: Schon für '
    'den Preis eines veganen Gerichts in der Mensa könnt ihr unabhängigen, jungen Journalismus für Studierende, '
    'Hochschulangehörige und alle anderen Leipziger*innen auf Steady unterstützen.',
    'Hochschuljournalismus wie dieser ist teuer. Dementsprechend schwierig ist es, eine unabhängige, '
    'ehrenamtlich betriebene Zeitung am Leben zu halten. Wir brauchen also eure Unterstützung: Schon für den Preis '
    'eines veganen Gerichts in der Mensa könnt ihr unabhängigen, jungen Journalismus für Studierende, '
    'Hochschulangehörige und alle anderen Leipziger*innen auf Steady unterstützen. Wir freuen uns über jeden Euro, '
    'der dazu beiträgt, luhze erscheinen zu lassen.'
]


def scrapeRessort(text):
    footer = text.find('div', {'class': 'articleFooter'})
    ressorts = footer.find_all('a')
    ressortArray = []
    for ressort in ressorts:
        if 'category' in ressort['href']:
            ressortArray.append(ressort.string)
    return ressortArray


def scrapeAuthor(text):
    authorDiv = text.find('div', {'class': 'authorStyle'})
    authors = authorDiv.find_all('a')
    authorsArray = []
    for author in authors:
        if author.string is None:
            authorsArray = ['Anonym']
            break
        else:
            authorsArray.append(author.string)
    return authorsArray


def scrapeTitle(text):
    return text.find('h2', {'class': 'titleStyle'}).string


def scrapeDate(text):
    footer = text.find('div', {'class': 'articleFooter'})
    writtenDate = footer.find('span').string

    writtenDateInPartsArray = writtenDate.split(' ')
    year = writtenDateInPartsArray[2]
    monthString = writtenDateInPartsArray[1]
    dayInWrongFormat = writtenDateInPartsArray[0][:-1]
    month = ''

    if len(str(dayInWrongFormat)) == 1:
        day = '0' + dayInWrongFormat
    else:
        day = dayInWrongFormat

    if monthString == 'Januar':
        month = '01'
    elif monthString == 'Februar':
        month = '02'
    elif monthString == 'März':
        month = '03'
    elif monthString == 'April':
        month = '04'
    elif monthString == 'Mai':
        month = '05'
    elif monthString == 'Juni':
        month = '06'
    elif monthString == 'Juli':
        month = '07'
    elif monthString == 'August':
        month = '08'
    elif monthString == 'September':
        month = '09'
    elif monthString == 'Oktober':
        month = '10'
    elif monthString == 'November':
        month = '11'
    elif monthString == 'Dezember':
        month = '12'

    date = year + '-' + month + '-' + day + ' 00:00:00'
    return date


def fillFooterArray(text):
    footer = text.find('div', {'class': 'articleFooter'})
    paragraphsInFooter = footer.find_all('p')
    paragraphsInFooterTextArray = []
    for p in paragraphsInFooter:
        paragraphsInFooterTextArray.append(p.get_text().strip())

    return paragraphsInFooterTextArray


def scrapeTextAndWordcountFromOldArticle(text, paragraphsInFooterTextArray):
    wordcount = 0
    articleText = ''
    allParagraphs = text.find('div', {'class': 'field-content'}).find_all('p')
    for p in allParagraphs:
        if len(p.find_all('p')) > 0:  # seems like a bs4 bug
            continue
        paragraphText = p.get_text().strip()
        if paragraphText in textToBeIgnoredArray:
            continue
        if paragraphText not in paragraphsInFooterTextArray:
            wordcount += len(paragraphText)
            articleText += paragraphText + ' '

    return [wordcount, articleText]


def scrapeTextAndWordcountFromNewerArticle(article, paragraphsInFooterTextArray):
    wordcount = 0
    articleText = ''
    allParagraphs = article.find_all('p')
    for p in allParagraphs:
        if len(p.find_all('p')) > 0:  # seems like a bs4 bug
            continue
        paragraphText = p.get_text().strip()
        if paragraphText in textToBeIgnoredArray:
            continue
        if paragraphText is not None and p.get('id') is None and paragraphText not in paragraphsInFooterTextArray:
            wordcount += len(paragraphText)
            articleText += paragraphText + ' '

    return [wordcount, articleText]


def scrapeTextAndWordcountFromNewestArticle(article, paragraphsInFooterTextArray):
    wordcount = 0
    articleText = ''
    allParagraphs = article.find_all('p')
    for p in allParagraphs:
        if len(p.find_all('p')) > 0:  # seems like a bs4 bug
            continue
        paragraphText = p.get_text().strip()
        if paragraphText in textToBeIgnoredArray:
            continue
        if paragraphText is not None and p.get('id') is None and \
                'contentWrapper' in p.find_parent('div')['class'] and paragraphText not in paragraphsInFooterTextArray:
            wordcount += len(paragraphText)
            articleText += paragraphText + ' '

    return [wordcount, articleText]


def scrapeWordcountAndText(text, title):
    article = text.find('article', {'id': 'mainArticle'})
    paragraphsInFooterTextArray = fillFooterArray(text)

    if article is None:  # very old article
        textAndWordcount = scrapeTextAndWordcountFromOldArticle(text, paragraphsInFooterTextArray)

    elif article.find_all('div', {'class': 'field-content'}) is not None:  # old article but not so old
        textAndWordcount = scrapeTextAndWordcountFromNewerArticle(article, paragraphsInFooterTextArray)

    else:  # newest kind of article
        textAndWordcount = scrapeTextAndWordcountFromNewestArticle(article, paragraphsInFooterTextArray)

    wordcount = textAndWordcount[0]
    articleText = textAndWordcount[1]
    articleText = title + ' ' + articleText
    return [wordcount, articleText]


def readInSite(url):
    return BeautifulSoup(urlopen(url).read(), 'html.parser')


def getLinksToSingleArticlesFromOverviewPages(numberOfOverviewPagesToScrapeAgain, luhzeArticleOverviewPageUrl):

    linksToArticleArray = []

    for i in range(0, numberOfOverviewPagesToScrapeAgain + 1):
        
        parsedPage = readInSite(luhzeArticleOverviewPageUrl + str(i))
        articlePreviews = parsedPage.findAll('article')

        for preview in articlePreviews[::-1]:
            linkToArticle = preview.find('a')['href']
            if not linkToArticle.startswith('https://www.luhze.de'):  # advertisement
                continue
            linksToArticleArray.append(linkToArticle)

    return linksToArticleArray

