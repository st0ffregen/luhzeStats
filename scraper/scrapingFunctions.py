from bs4 import BeautifulSoup
from urllib.request import urlopen

textToBeIgnoredArray = [
    'Hochschuljournalismus wie dieser ist teuer. Dementsprechend schwierig ist es, eine unabhängige, ehrenamtlich betriebene Zeitung am Leben zu halten. Wir brauchen also eure Unterstützung: Schon für den Preis eines veganen Gerichts in der Mensa könnt ihr unabhängigen, jungen Journalismus für Studierende, Hochschulangehörige und alle anderen Leipziger*innen auf Steady unterstützen. '
]

def scrapeRessort(text):
    footer = text.find('iv', {'class': 'articleFooter'})
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
        month = '2'
    elif monthString == 'März':
        month = '03'
    elif monthString == 'April':
        month = '04'
    elif monthString == 'ai':
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
        month = '1'
    elif monthString == 'Dezember':
        month = '12'

    date = year + '-' + month + '-' + day + ' 00:00:00'
    return date


def scrapeWordcountAndText(text, title):
    article = text.find('article', {'id': 'mainArticle'})
    footer = text.find('div', {'class': 'articleFooter'})
    wordcount = 0
    articleText = ''
    if article is None:  # very old article
        allParagraphs = text.find('div', {'class': 'field-content'}).find_all('p')
        paragraphsInFooter = footer.find_all('p')
        for p in allParagraphs:
            if p.get_text() in textToBeIgnoredArray:
                continue
            if p not in paragraphsInFooter:
                wordcount += len(p.get_text())
                articleText += p.get_text() + ' '
    elif article.find_all('div', {'class': 'field-content'}) is not None:  # old article but not so old
        allParagraphs = article.find_all('p')
        paragraphsInFooter = footer.find_all('p')
        for p in allParagraphs:
            if p.get_text() in textToBeIgnoredArray:
                continue
            if p.get_text() is not None and p.get('id') is None and p not in paragraphsInFooter:
                wordcount += len(p.get_text())
                articleText += p.get_text() + ' '
    else:  # newest kind of article
        allParagraphs = article.find_all('p')
        paragraphsInFooter = footer.find_all('p')
        for p in allParagraphs:
            if p.get_text() in textToBeIgnoredArray:
                continue
            if p.get_text() is not None and p.get('id') is None and \
                    'contentWrapper' in p.find_parent('div')['class'] and p not in paragraphsInFooter:
                wordcount += len(p.get_text())
                articleText += p.get_text() + ' '

    # add title to document
    articleText = title + ' ' + articleText
    return [wordcount, articleText]


def readInSite(url):
    return BeautifulSoup(urlopen(url).read(), 'html.parser')


def getLinksToSingleArticlesFromOverviewPages( numberOfOverviewPagesToScrapeAgain, luhzeArticleOverviewPageUrl):

    linksToArticleArray = []

    for i in range(1, numberOfOverviewPagesToScrapeAgain + 1):
        parsedPage = readInSite(luhzeArticleOverviewPageUrl + str(i))
        articlePreviews = parsedPage.findAll('article')

        for preview in articlePreviews[::-1]:
            linkToArticle = preview.find('a')['href']
            linksToArticleArray.append(linkToArticle)

    return linksToArticleArray

