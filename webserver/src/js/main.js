
window.onload = async function () {

    let sampleData = [
        ['STUDENT', 'STUDENTIN'],
        ['LUHZE', 'STUDENT!'],
        [['FRAU', 'FRAUEN', 'DAME', 'DAMEN'], ['MANN', 'MÄNNER', 'HERR', 'HERREN']],
        ['STUDENTEN', ['STUDIERENDE', 'STUDIERENDEN']],
        ['KRISE', ['CORONA', 'PANDEMIE', 'CORONA-PANDEMIE'], ['KLIMA', 'KLIMAWANDEL', 'KLIMAKRISE']]
    ];
    let index = Math.floor(Math.random() * sampleData.length);

    let wordOccurrenceInput = document.getElementById("wordOccurrenceInput");
    let wordOccurrenceChart = document.getElementById('wordOccurrenceChart');

    initWordOccurrenceAutocomplete(wordOccurrenceInput);
    await initWordOccurrenceChart(wordOccurrenceChart, sampleData[index]);

    displayGraphContent('today');
}

