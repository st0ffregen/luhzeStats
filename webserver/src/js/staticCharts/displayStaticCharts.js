let currentGraphContentDate = new Date();
const allCharts = [];


async function displayMinAuthor() {
    let data = await fetchApi('minAuthor');

    if (data.length === 0) return;

    document.getElementById("authorP").innerHTML = "Nur Autor*innen mit mehr als " + data['minAuthor'] + " Artikeln miteinbezogen";
}

async function displayMinRessort() {
    let data = await fetchApi('minRessort');

    if (data.length === 0) return;

    document.getElementById("ressortP").innerHTML = "Nur Ressorts mit mehr als " + data['minRessort'] + " Artikeln miteinbezogen";
}

async function displayDate() {
    let data = await fetchApi('date');

    if (data.length === 0) return;

    let date = new Date(data['date']);
    document.getElementById("dateP").innerHTML = "Zuletzt aktualisiert: " + date.toLocaleString();
}

async function displayArticlesTimeline(date) {
    let fetchedData = await fetchApi('articlesTimeline', 'dateBackInTime', date);

    if (fetchedData.includes('error')) return;

    let articlesTimelineChart = document.getElementById('articlesTimelineChart');
    let chartData = convertFinancialData(fetchedData, 'Anzahl der veröffentlichten Artikel');
    financialChart(articlesTimelineChart, chartData, 'MMM yyyy');
}

async function displayArticlesTimelineDerivative(date) {
    let fetchedData = await fetchApi('articlesTimeline', 'dateBackInTime', date);

    if (fetchedData.includes('error')) return;

    let articlesTimelineDerivativeChart = document.getElementById('articlesTimelineDerivativeChart');
    let chartData = convertFinancialDataDerivative(fetchedData, 'Anzahl der veröffentlichten Artikel pro Monat');
    financialChart(articlesTimelineDerivativeChart, chartData, 'MMM yyyy');
}

async function displayActiveMembers(date) {
    let fetchedData = await fetchApi('activeMembers', 'dateBackInTime', date);

    if (fetchedData.includes('error')) return;

    let activeMembersChart = document.getElementById('activeMembersChart');
    let chartData = convertFinancialDataDerivative(fetchedData, 'Anzahl der aktiven Autor*innen pro Quartal');
    financialChart(activeMembersChart, chartData, 'q yyyy');
}

async function displayGoogleAuthorTimelineChart(date) {
    let fetchedData = await fetchApi('authorTimeline', 'dateBackInTime', date);

    if (fetchedData.includes('error')) return;

    let authorTimelineChart = document.getElementById('authorTimelineChart');
    googleTimeline(authorTimelineChart, fetchedData);
}

async function displayAuthorTopListChart(date) {
    let fetchedData = await fetchApi('authorTopList', 'dateBackInTime', date);

    if (fetchedData.includes('error')) return;

    let authorTopListChart = document.getElementById('authorTopListChart');
    barChart(authorTopListChart, fetchedData, 'bar', 'Anzahl der Artikel pro Autor*in', true);
}

async function displayAuthorAverageChart(date) {
    let fetchedData = await fetchApi('authorAverage', 'dateBackInTime', date);

    if (fetchedData.includes('error')) return;

    let authorAverageChart = document.getElementById('authorAverageChart');
    barChart(authorAverageChart, fetchedData, 'bar', 'Durchschnittliche Anzahl von Zeichen pro Autor*in', true);
}

async function displayMostArticlesPerTimeChart(date) {
    let fetchedData = await fetchApi('mostArticlesPerTime', 'dateBackInTime', date);

    if (fetchedData.includes('error')) return;

    let mostArticlesPerTimeChart = document.getElementById('mostArticlesPerTimeChart');
    barChart(mostArticlesPerTimeChart, fetchedData, 'bar', 'Zeitspanne zwischen zwei Artikeln in Tagen', true);
}

async function displayAverageCharactersPerDayChart(date) {
    let fetchedData = await fetchApi('averageCharactersPerDay', 'dateBackInTime', date);

    if (fetchedData.includes('error')) return;

    let averageCharactersPerDayChart = document.getElementById('averageCharactersPerDayChart');
    barChart(averageCharactersPerDayChart, fetchedData, 'bar', 'Durchschnittliche Anzahl von geschriebenen Zeichen pro Tag', true);
}

async function displayGoogleRessortTimelineChart(date) {
    let fetchedData = await fetchApi('ressortTimeline', 'dateBackInTime', date);

    if (fetchedData.includes('error')) return;

    let ressortTimelineChart = document.getElementById('ressortTimelineChart');
    googleTimeline(ressortTimelineChart, fetchedData);
}

async function displayTopAuthorsPerRessortChart(date) {
    let fetchedDataTopAuthorsPerRessort = await fetchApi('topAuthorsPerRessort', 'dateBackInTime', date);

    if (fetchedDataTopAuthorsPerRessort.length === 0) return;

    let fetchedDataRessortTopList = await fetchApi('ressortTopList', 'dateBackInTime', date);

    if (fetchedDataRessortTopList.length === 0) return;

    let ressortTopListChart = document.getElementById('ressortTopListChart');
    let tooltipFunctionToDisplayTopAuthors = customTooltip(fetchedDataTopAuthorsPerRessort);
    barChart(ressortTopListChart, fetchedDataRessortTopList, 'bar', 'Anzahl der Artikel pro Ressort', false, tooltipFunctionToDisplayTopAuthors);
}

function displayRessortArticlesTimelineDerivativeChart(colorArray, fetchedData, firstRessortToBeDisplayed, secondRessortToBeDisplayed) {
    let ressortArticlesTimelineDerivativeChart = document.getElementById('ressortArticlesTimelineDerivativeChart');

    let datasets = [];
    for (let i = 0; i < fetchedData.length; i++) {
        if (i === firstRessortToBeDisplayed || i === secondRessortToBeDisplayed) {
            let newDataset = convertFinancialDataDerivative(fetchedData[i]['articles'], fetchedData[i]['ressort'], colorArray[i], 0);
            datasets.push(newDataset[0]);
        } else {
            let newDataset = convertFinancialDataDerivative(fetchedData[i]['articles'], fetchedData[i]['ressort'], colorArray[i], 1);
            datasets.push(newDataset[0]);
        }
    }

    financialChart(ressortArticlesTimelineDerivativeChart, datasets, 'MMM yyyy');
}

function displayRessortArticlesTimelineChart(colorArray, fetchedData, firstRessortToBeDisplayed, secondRessortToBeDisplayed) {
    let ressortArticlesTimelineChart = document.getElementById('ressortArticlesTimelineChart');
    let datasets = [];
    for (let i = 0; i < fetchedData.length; i++) {

        if (i === firstRessortToBeDisplayed || i === secondRessortToBeDisplayed) {
            let newDataset = convertFinancialData(fetchedData[i]['articles'], fetchedData[i]['ressort'], colorArray[i], 0);
            datasets.push(newDataset[0]);
        } else {
            let newDataset = convertFinancialData(fetchedData[i]['articles'], fetchedData[i]['ressort'], colorArray[i], 1);
            datasets.push(newDataset[0]);
        }

    }
    financialChart(ressortArticlesTimelineChart, datasets, 'MMM yyyy');
}

async function displayRessortArticlesTimelineCharts(date) {

    let fetchedData = await fetchApi('ressortArticlesTimeline', 'dateBackInTime', date);

    if (fetchedData.includes('error')) return;

    let colorArray = getRandomHexColorArray(fetchedData.length);

    let firstRessortToBeDisplayed = Math.floor(Math.random() * fetchedData.length);
    let secondRessortToBeDisplayed = 0;

    do { //verhindern dass das selbe ressort random ausgewaehlt wird
        secondRessortToBeDisplayed = Math.floor(Math.random() * fetchedData.length);
    } while (firstRessortToBeDisplayed === secondRessortToBeDisplayed);

    displayRessortArticlesTimelineChart(colorArray, fetchedData, firstRessortToBeDisplayed, secondRessortToBeDisplayed);
    displayRessortArticlesTimelineDerivativeChart(colorArray, fetchedData, firstRessortToBeDisplayed, secondRessortToBeDisplayed);
}

async function displayRessortAverageChart(date) {
    let fetchedData = await fetchApi('ressortAverage', 'dateBackInTime', date);

    if (fetchedData.includes('error')) return;

    let ressortAverageChart = document.getElementById('ressortAverageChart');
    barChart(ressortAverageChart, fetchedData, 'bar', 'Durchschnittliche Anzahl an Zeichen pro Ressort pro Artikel', true);
}

function generateGraphs(date) {

    showLoader();
    destroyAllExistingCharts();

    displayMinAuthor();
    displayMinRessort();
    displayDate();
    displayArticlesTimeline(date);
    displayArticlesTimelineDerivative(date);
    displayActiveMembers(date);
    displayGoogleAuthorTimelineChart(date);
    displayAuthorTopListChart(date);
    displayAuthorAverageChart(date);
    displayMostArticlesPerTimeChart(date);
    displayAverageCharactersPerDayChart(date);
    displayGoogleRessortTimelineChart(date);
    displayTopAuthorsPerRessortChart(date);
    displayRessortArticlesTimelineCharts(date).then(r => removeLoader()); // not the most beautiful way
    displayRessortAverageChart(date);


}


function displayGraphContent(direction, step) {
    currentGraphContentDate = calculateDateToGetDataFor(direction, step, currentGraphContentDate);
    writeDateToDomElement('go-back-in-time-date-graph-content', currentGraphContentDate);
    generateGraphs(currentGraphContentDate.toISOString().slice(0, -5));
}

function destroyAllExistingCharts() {
    for (const chart of allCharts) {
        chart.destroy();
    }
}


window.onresize = function() { //traffic aufwending
	displayGoogleAuthorTimelineChart();
	displayGoogleRessortTimelineChart();
}
