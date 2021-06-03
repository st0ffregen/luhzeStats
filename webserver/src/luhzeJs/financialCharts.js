Chart.defaults.global.defaultFontColor = '#555';
var DateTime = luxon.DateTime;

function customTooltip(data) {
    return function(tooltip) {
        let displayData = [];
        let displayLabel = [];
        let colorArray = [];

        //parse data to data array
        for (let i = 0; i < data.length; i++) {
            if (data[i]['ressort'] === tooltip.title[0]) {

                for (let k = 0; k < data[i]['authors'].length; k++) {
                    colorArray.push(getSingleRandomColor(alpha));
                    displayData.push(data[i]['authors'][k]['count']);
                    //split name
                    let split = data[i]['authors'][k]['name'].split(" ");
                    let firstName = "";

                    for (let l = 0; l < split.length - 1; l++) {
                        firstName += split[l] + " ";

                    }

                    let name = firstName + split[split.length - 1].charAt(0) + ".";
                    displayLabel.push(name);
                }
                break;
            }
        }

        // Tooltip Element
        let tooltipEl = document.getElementById('chartjs-tooltip');

        // Hide if no tooltip
        if (tooltip.opacity === 0) {
            tooltipEl.style.opacity = 0;
            return;
        }

        while (tooltipEl.firstChild) {
            tooltipEl.removeChild(tooltipEl.firstChild);
        }

        let label = document.createElement('p');

        if (displayData.length > 0) {
            label.innerHTML = tooltip.title[0] + ": " + tooltip.dataPoints[0].yLabel + "; Top Autor*innen:";
            label.className = "chartjs";
            tooltipEl.appendChild(label);
            let child = document.createElement('canvas');
            child.id = 'tooltipChart';
            tooltipEl.appendChild(child);
        } else {
            label.innerHTML = tooltip.title[0] + ": " + tooltip.dataPoints[0].yLabel;
            tooltipEl.appendChild(label);
        }

        // Set caret Position
        tooltipEl.classList.remove('above', 'below', 'no-transform');
        if (tooltip.yAlign) {
            tooltipEl.classList.add(tooltip.yAlign);
        } else {
            tooltipEl.classList.add('no-transform');
        }

        // Set Text
        if (tooltip.body && displayData.length > 0) {

            let chart = tooltipEl.children[1].getContext('2d');
            // For a pie chart
            new Chart(chart, {
                type: 'bar',
                data: {
                    datasets: [{
                        data: displayData,
                        label: displayLabel,
                        borderWidth: 1,
                        fill: false,
                        backgroundColor: colorArray,
                    }],
                    labels: displayLabel,


                }, options: {
                    tooltips: {
                        enabled: false
                    },
                    legend: false,
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                precision: 0
                            }
                        }]
                    }
                }
            });
        }

        let positionY = this._chart.canvas.offsetTop;
        let positionX = this._chart.canvas.offsetLeft + 50; //+50 so the most left chart wont be cut of by the computer screen

        // Display, position, and set styles for font
        tooltipEl.style.opacity = 1;
        tooltipEl.style.left = positionX + tooltip.caretX + 'px';
        tooltipEl.style.top = positionY + tooltip.caretY + 'px';
        tooltipEl.style.fontFamily = tooltip._bodyFontFamily;
        tooltipEl.style.fontSize = tooltip.bodyFontSize + 'px';
        tooltipEl.style.fontStyle = tooltip._bodyFontStyle;
        tooltipEl.style.padding = tooltip.yPadding + 'px ' + tooltip.xPadding + 'px';
    };
}

function convertFinancialDataDerivative(data, label, color = '#ff6384', hidden = 0) {

    let dataset = [];

    for (const date of data) {
        dataset.push({t: DateTime.fromISO(date['date'].split(' ')[0]).valueOf(), y: date['count']});
    }

    return [
        {
            label: label,
            borderColor: color,
            data: dataset,
            type: 'line',
            pointRadius: 0,
            fill: false,
            lineTension: 0,
            borderWidth: 2,
            hidden: hidden
        }
    ];
}

function convertFinancialData(data, label, color = '#ff6384', hidden = 0) {
    let dataset = [];
    let summedUpCount = 0;

    for (const date of data) {
        summedUpCount += parseInt(date['count']);
        dataset.push({t: DateTime.fromISO(date['date'].split(' ')[0]).valueOf(), y: summedUpCount});
    }

    return [
        {
            label: label,
            borderColor: color,
            data: dataset,
            type: 'line',
            pointRadius: 0,
            fill: false,
            lineTension: 0,
            borderWidth: 2,
            hidden: hidden
        }
    ];
}

function ressortArticlesTimelineFinancial(data, colorArray, hiddenArray, oldestArticle, newestArticle) {

    let datasetArray = [];
    for (let k = 0; k < data.length; k++) {// get a ressort



        datasetArray.push({
            label: data[k]['ressort'],
            borderColor: colorArray[k],
            data: returnArray,
            type: 'line',
            pointRadius: 0,
            fill: false,
            lineTension: 0,
            borderWidth: 2,
            hidden: hiddenArray[k],
        });
    }
    return datasetArray;
}


function ressortArticlesTimelineFinancialDerivation(data, colorArray, hiddenArray, oldestArticle, newestArticle) {

    let datasetArray = [];

    for (let k = 0; k < data.length; k++) { //gives me a ressort

        let returnArray = [];
        //use a init date to determine if next date is in same quarter or not
        let dateArray = quarterArray(new Date(oldestArticle['oldestArticle']), new Date(newestArticle['newestArticle']));
        for (let i = 0; i < dateArray.length; i++) {
            //loop through the empty date array (only dates in it by now) find the articles with another for loop
            articlesCount = 0;
            for (let l = 0; l < data[k]['countPerMonth'].length; l++) {

                currentDate = new Date(data[k]['countPerMonth'][l]['date'] + "T00:00:00Z");
                currentQuarter = Math.floor(currentDate.getMonth() / 3);
                if (currentQuarter === dateArray[i][1] && currentDate.getFullYear() === dateArray[i][0]) {
                    articlesCount += data[k]['countPerMonth'][l]['count']
                }
            }
            //after finding all articles and adding them up to articlesCount, we can change the dateArray entry to what we want for the chartjs

            let month = ((dateArray[i][1] * 3) + 1).toString();
            if (month.length < 2) month = "0" + month;
            returnArray[i] = {
                t: DateTime.fromISO(dateArray[i][0].toString() + "-" + month + "-01").valueOf(),
                y: articlesCount
            };//calculating the first month in each quarter
        }

        datasetArray.push({
            label: data[k]['ressort'],
            borderColor: colorArray[k],
            data: returnArray,
            type: 'line',
            pointRadius: 0,
            fill: false,
            lineTension: 0,
            borderWidth: 2,
            hidden: hiddenArray[k],
        });
    }
    return datasetArray;
}


function financialChart(chartElement, data, tooltipFormat) {

    let configForFinancialCharts = {
        data: {
            datasets: data
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
                        'tooltipFormat': tooltipFormat
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
                    afterBuildTicks: function (scale, ticks) {
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
                }],
                yAxes: [{}]
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
                    fontSize: 15,
                }
            }

        }
    };
    console.log(chartElement.getContext('2d'));
    console.log(configForFinancialCharts);
    new Chart(chartElement.getContext('2d'), configForFinancialCharts);
}
