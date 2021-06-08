let colorArray = [
    {
        'color': 'rgb(12, 102, 192)',
        'colorAlpha': 'rgba(12, 102, 192, 0.1)',
        'isUsed': false
    },
    {
        'color': 'rgb(255, 133, 82)',
        'colorAlpha': 'rgba(255, 133, 82, 0.1)',
        'isUsed': false
    },
    {
        'color': 'rgb(170, 220, 4)',
        'colorAlpha': 'rgba(170, 220, 4, 0.1)',
        'isUsed': false
    },
    {
        'color': 'rgb(119, 81, 68)',
        'colorAlpha': 'rgba(119, 81, 68, 0.1)',
        'isUsed': false
    },
    {
        'color': 'rgb(149, 53, 212)',
        'colorAlpha': 'rgba(149, 53, 212, 0.1)',
        'isUsed': false
    },
]

var DateTime = luxon.DateTime;
let maxWordsToBeDisplayed = 5;


function pickNewColor() {
    for (const color of colorArray) {
        if (color['isUsed'] === false) {
            color['isUsed'] = true;
            return [color['color'], color['colorAlpha']];
        }
    }
    return null;
}

function setColorFree(colorToSetFree) {
    for (const color of colorArray) {
        if (color['color'] === colorToSetFree) {
            color['isUsed'] = false;
        }
    }
}

async function addDataToWordOccurrenceChart(word) {
    if (window.luhzeChart.data.datasets.length < maxWordsToBeDisplayed) {

        let data = await fetchWordOccurrenceData([word]);
        let dataset = convertData(data);

        window.luhzeChart.data.datasets.push(dataset.pop());
        window.luhzeChart.update();

    } else {
        let colorFromFirstWord = window.luhzeChart.data.datasets[0]['borderColor'];
        deleteDataFromWordOccurrenceChart(window.luhzeChart.data.datasets[0]['label']);

        setColorFree(colorFromFirstWord);

        await addDataToWordOccurrenceChart(word);
    }

}

function sumUpWordArray(fetchedData, arrayToFill) {

    for (const row of fetchedData) {
        let index = arrayToFill.findIndex(element => {
            if (element.year === row['year'] && element.quarter === row['quarter']) return true;
        });

        if (index === -1) {
            arrayToFill.push({
                'word': row['word'],
                'year': row['year'],
                'quarter': row['quarter'],
                'occurrence': row['occurrence'],
                'quarterWordCount': row['quarterWordCount'],
                'occurrenceRatio': 0
            });
        } else {
            arrayToFill[index]['occurrence'] += row['occurrence'];
            arrayToFill[index]['word'] += ' \u274C ' + row['word'];
        }
    }

    for (const row of arrayToFill) {
        row['occurrenceRatio'] = Math.round(100000 * row['occurrence'] / row['quarterWordCount']);
    }

    return arrayToFill;
}

async function fetchWordOccurrenceData(wordArray) {
    let array = [];

    for (const word of wordArray) {
        if (Array.isArray(word)) { // if term contains several words which should be summed up
            let summedWordArray = [];
            for (const w of word) {
                let data = await fetchApi('wordOccurrence', 'word', w.toUpperCase())
                if (data.includes('error')) {
                    continue;
                }
                summedWordArray = sumUpWordArray(data, summedWordArray);
            }
            array.push(summedWordArray);
        } else {
            let data = await fetchApi('wordOccurrence', 'word', word.toUpperCase());

            if (data.includes('error')) {
                continue;
            }
            array.push(data);
        }
    }
    return array;
}

function convertData(dataArray) {
    let datasets = [];
    for (const word of dataArray) {
        let chartData = [];
        for (const row of word) {
            let date = '';
            let month = ((row['quarter'] * 3) - 2).toString();
            if (month.length < 2) {
                date = row['year'].toString() + "-0" + month + "-01";
            } else {
                date = row['year'].toString() + "-" + month + "-01";
            }

            date = DateTime.fromISO(date).valueOf();

            chartData.push({
                t: date,
                y: row['occurrenceRatio']
            });
        }

        let [color, colorAlpha] = pickNewColor();

        datasets.push({
            label: word[0]['word'].toUpperCase(),
            borderColor: color,
            backgroundColor: colorAlpha,
            data: chartData,
            type: 'line',
            pointRadius: 0,
            fill: true,
            lineTension: 0,
            borderWidth: 2
        });
    }

    return datasets;
}

async function initWordOccurrenceChart(chart, initWordArray) {

    let data = await fetchWordOccurrenceData(initWordArray);
    let datasets = convertData(data);

    let luhzeChartConfig = {
        data: {
            datasets: datasets
        },
        options: {
            animation: {
                duration: 0
            },
            scales: {
                xAxes: [{
                    type: 'time',
                    distribution: 'linear',
                    offset: true,
                    time: {
                        'tooltipFormat': 'q yyyy'
                    },
                    ticks: {
                        major: {
                            enabled: true,
                            fontStyle: 'bold'
                        },
                        source: 'data',
                        autoSkip: true,
                        autoSkipPadding: 75,
                        maxRotation: 0,
                        sampleSize: 100,
                        maxTicksLimit: 7,
                    },
                    afterBuildTicks: afterDeleteTicksFunction
                }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Anzahl pro 100.000 Wörter'
                    }
                }]
            },
            hover: {
                mode: 'nearest',
                intersect: false
            },
            tooltips: {
                mode: 'nearest',
                intersect: false
            },
            legend: {

                labels: {
                    fontFamily: "'Helvetica', 'Arial', sans-serif",
                    fontColor: '#555',
                }
            },
            responsive: true,
            maintainAspectRatio: false,
        }
    };
    window.luhzeChart = new Chart(chart.getContext("2d"), luhzeChartConfig);
}

function deleteDataFromWordOccurrenceChart(word) {

    let datasetsWithoutDeletedWord = [];
    for (let i = 0; i < window.luhzeChart.data.datasets.length; i++) {
        if (word !== window.luhzeChart.data.datasets[i]['label']) {
            datasetsWithoutDeletedWord.push(window.luhzeChart.data.datasets[i]);
        }
    }

    window.luhzeChart.data.datasets = datasetsWithoutDeletedWord;
    window.luhzeChart.update();
}


function afterDeleteTicksFunction (scale, ticks) {
                        if (ticks != null) {
                            let majorUnit = scale._majorUnit;
                            let firstTick = ticks[0];
                            let i, ilen, val, tick, currMajor, lastMajor;

                            val = DateTime.fromISO(ticks[0].value);
                            if ((majorUnit === 'minute' && val.second === 0)
                                || (majorUnit === 'hour' && val.minute === 0)
                                || (majorUnit === 'day' && val.hour === 9)
                                || (majorUnit === 'month' && val.day <= 3 && val.weekday === 1)
                                || (majorUnit === 'year' && val.month === 0)) {
                                firstTick.major = true;
                            } else {
                                firstTick.major = false;
                            }
                            lastMajor = val.get(majorUnit);

                            for (i = 1, ilen = ticks.length; i < ilen; i++) {
                                tick = ticks[i];
                                val = DateTime.fromISO(tick.value);
                                currMajor = val.get(majorUnit);
                                tick.major = currMajor !== lastMajor;
                                lastMajor = currMajor;
                            }
                            return ticks;
                        }
                    }