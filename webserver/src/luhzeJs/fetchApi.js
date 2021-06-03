async function fetchApi(route, parameter = '', parameterValue = '') {
    let response;

    if (parameter === '' && parameterValue === '') {
        response = await fetch('http://localhost/api/' + route);
    } else {
        response = await fetch('http://localhost/api/' + route + '?' + parameter + '=' + parameterValue);
    }

    return await response.json();
}

async function displayMinAuthor() {
    let data = await fetchApi('minAuthor');
    document.getElementById("authorP").innerHTML = "Nur Autor*innen mit mehr als " + data['minAuthor'] + " Artikeln miteinbezogen";
}

async function displayMinRessort() {
    let data = await fetchApi('minRessort');
    document.getElementById("ressortP").innerHTML = "Nur Ressorts mit mehr als " + data['minRessort'] + " Artikeln miteinbezogen";
}

async function displayDate() {
    let data = await fetchApi('date');
    document.getElementById("dateP").innerHTML = "Zuletzt aktualisiert: " + data['date'];
}

async function displayArticlesTimeline() {
    let fetchedData = await fetchApi('articlesTimeline');
    let articlesTimelineChart = document.getElementById('articlesTimelineChart');
    let chartData = convertFinancialData(fetchedData, 'Anzahl der veröffentlichten Artikel');
    financialChart(articlesTimelineChart, chartData, 'MMM yyyy');
}

async function displayArticlesTimelineDerivative() {
    let fetchedData = await fetchApi('articlesTimeline');
    let articlesTimelineDerivativeChart = document.getElementById('articlesTimelineDerivativeChart');
    let chartData = convertFinancialDataDerivative(fetchedData, 'Anzahl der veröffentlichten Artikel pro Monat');
    financialChart(articlesTimelineDerivativeChart, chartData, 'MMM yyyy');
}

async function displayActiveMembers() {
    let fetchedData = await fetchApi('activeMembers');
    let activeMembersChart = document.getElementById('activeMembersChart');
    let chartData = convertFinancialDataDerivative(fetchedData, 'Anzahl der aktiven Autor*innen pro Monat');
    financialChart(activeMembersChart, chartData, 'q yyyy');
}

async function displayGoogleAuthorTimelineChart() {
    let fetchedData = await fetchApi('authorTimeline');
    let authorTimelineChart = document.getElementById('authorTimelineChart');
    googleTimeline(authorTimelineChart, fetchedData);
}

async function displayAuthorTopListChart() {
    let fetchedData = await fetchApi('authorTopList');
    let authorTopListChart = document.getElementById('authorTopListChart');
    barChart(authorTopListChart, fetchedData, 'bar', 'Anzahl der Artikel pro Autor*in', true);
}

async function displayAuthorAverageChart() {
    let fetchedData = await fetchApi('authorAverage');
    let authorAverageChart = document.getElementById('authorAverageChart');
    barChart(authorAverageChart, fetchedData, 'bar', 'Durchschnittliche Anzahl von Zeichen pro Autor*in', true);
}

async function displayMostArticlesPerTimeChart() {
    let fetchedData = await fetchApi('mostArticlesPerTime');
    let mostArticlesPerTimeChart = document.getElementById('mostArticlesPerTimeChart');
    barChart(mostArticlesPerTimeChart, fetchedData, 'bar', 'Zeitspanne zwischen zwei Artikeln in Tagen', true);
}

async function displayAverageCharactersPerDayChart() {
    let fetchedData = await fetchApi('averageCharactersPerDay');
    let averageCharactersPerDayChart = document.getElementById('averageCharactersPerDayChart');
    barChart(averageCharactersPerDayChart, fetchedData, 'bar', 'Durchschnittliche Anzahl von geschriebenen Zeichen pro Tag', true);
}

async function displayGoogleRessortTimelineChart() {
    let fetchedData = await fetchApi('ressortTimeline');
    let ressortTimelineChart = document.getElementById('ressortTimelineChart');
    googleTimeline(ressortTimelineChart, fetchedData);
}

async function displayTopAuthorsPerRessortChart() {
    let fetchedDataTopAuthorsPerRessort = await fetchApi('topAuthorsPerRessort');
    let fetchedDataRessortTopList = await fetchApi('ressortTopList');
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

async function displayRessortArticlesTimelineCharts() {

    let fetchedData = await fetchApi('ressortArticlesTimeline');
    let colorArray = getRandomHexColorArray(fetchedData.length);

    let firstRessortToBeDisplayed = Math.floor(Math.random() * fetchedData.length);
    let secondRessortToBeDisplayed = 0;

    do { //verhindern dass das selbe ressort random ausgewaehlt wird
        secondRessortToBeDisplayed = Math.floor(Math.random() * fetchedData.length);
    } while (firstRessortToBeDisplayed === secondRessortToBeDisplayed);

    displayRessortArticlesTimelineChart(colorArray, fetchedData, firstRessortToBeDisplayed, secondRessortToBeDisplayed);
    displayRessortArticlesTimelineDerivativeChart(colorArray, fetchedData, firstRessortToBeDisplayed, secondRessortToBeDisplayed);
}

async function displayRessortAverageChart() {
    let fetchedData = await fetchApi('ressortAverage');
    let ressortAverageChart = document.getElementById('ressortAverageChart');
    barChart(ressortAverageChart, fetchedData, 'bar', 'Durchschnittliche Anzahl an Zeichen pro Ressort pro Artikel', true);
}

function generateGraphs() {
    displayMinAuthor();
    displayMinRessort();
    displayDate();
    displayArticlesTimeline();
    displayArticlesTimelineDerivative();
    displayActiveMembers();
    displayGoogleAuthorTimelineChart();
    displayAuthorTopListChart();
    displayAuthorAverageChart();
    displayMostArticlesPerTimeChart();
    displayAverageCharactersPerDayChart();
    displayGoogleRessortTimelineChart();
    displayTopAuthorsPerRessortChart();
    displayRessortArticlesTimelineCharts();
    displayRessortAverageChart();
}
