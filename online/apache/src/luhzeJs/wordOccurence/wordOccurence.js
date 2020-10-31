
var colorArray = ["rgb(189, 154, 66)","rgb(119, 204, 102)","rgb(151, 172, 211)"];

var colorArrayAlpha = ["rgba(189, 154, 66,0.5)","rgba(119, 204, 102,0.5)","rgba(151, 172, 211,0.5)"];

var DateTime = luxon.DateTime;

async function addDataToWordOccurenceChart(word, chart) {
			
	//only add a word with max 4 words
	var maxValue = 4; //in die env???
	if(chart.data.datasets.length<=maxValue) {
	    fetchFileAPI("minAndMaxYearAndQuarter", function (data) {

            var button = document.getElementsByClassName("hideYearsButton")[0];

            if(button.innerHTML.startsWith("Zeige Daten vor ")) {
                var firstYear = "2015";
                var firstQuarter = 2;

            } else {
                var firstYear = data['minYearAndQuarter'].toString().substring(0, 4);
                var firstQuarter = data['minYearAndQuarter'].toString().slice(-1);
            }

            var lastYear = data['maxYearAndQuarter'].toString().substring(0, 4);
            var lastQuarter = data['maxYearAndQuarter'].toString().slice(-1);


            //data verarbeiten
            dataArray = [];
            //erstellen eines array mit durchgehenden daten
            fetchParameterAPI("wordOccurence", "word", word, (data) => {
                if("Error. The word does not exists." === data) {
                    console.log("Error. The word " + word + " does not exists.");
                    var input = document.getElementById("wordInput");
                    input.value = "";
                    input.placeholder = "Wort nicht gefunden";
                    return 1;
                }

                for(var i=firstYear;i<=lastYear;i++) {
                    for(var q=firstQuarter;q<=4;q++) {
                        // translate quarter to date
                        var month = ((q * 3) -2).toString();
                        var date = i.toString() + "-" + month + "-01";

                        //check if current date (i+q) is in data array
                        var foundInDataSet = false;
                        for(var k=0;k<data.length;k++) { //overwrites den eintrag von zuvor
                            if(data[k]['yearAndQuarter'] == i.toString() + q.toString()) {

                                foundInDataSet = true;
                                dataArray.push({t:DateTime.fromISO(date).valueOf(),y:data[k]['occurencePerWords']});
                            }
                        }
                        if(foundInDataSet == false) dataArray.push({t:DateTime.fromISO(date).valueOf(),y:0});

                    }
                    firstQuarter = 1;
                }


                var newDataset = {label: word.toUpperCase(),
                                borderColor: colorArray[chart.data.datasets.length],
                                backgroundColor: colorArrayAlpha[chart.data.datasets.length],
                                data: dataArray,
                                type: 'line',
                                pointRadius: 0,
                                fill: true,
                                lineTension: 0,
                                borderWidth: 2};

                chart.data.datasets.push(newDataset);

                chart.update();
                });




	    });
	} else {
	    //handle errors
	    //delete first word and add the givin input word
        chart.data.datasets = deleteDataFromWordOccurenceChart(chart.data.datasets[0]['label'], chart);

	    //add the givin input word
	    addDataToWordOccurenceChart(word, chart);
	}

}


async function hideOrShowDateBeforeYear(chart, button) {

    if(button.innerHTML.startsWith("Verberge Daten vor ")) {
        //the data before 2017 is pretty löchrig und verzieht das ganze imens
        for(var i=0;i<chart.data.datasets.length;i++) { //loop durch die dargestellten woerter
            var newArray = [];
            for(var k=0;k<chart.data.datasets[i]['data'].length;k++) {
                var momentDate = DateTime.fromMillis(chart.data.datasets[i]['data'][k]['t']);
                console.log(momentDate.month);
                if(momentDate.year >= 2015 && !(momentDate.month < 3 && momentDate.year == 2015 )) {

                    newArray.push(chart.data.datasets[i]['data'][k]);
                }
            }
            chart.data.datasets[i]['data'] = newArray;
        }

        button.innerHTML = "Zeige Daten vor 2015, 2. Quartal";

        chart.update();

    } else {
        var wordsToFetchAgain = []

        for(var i=0;i<chart.data.datasets.length;i++) {
            wordsToFetchAgain.push(chart.data.datasets[i]['label']);
        }

        chart.data.datasets = [];

        button.innerHTML = "Verberge Daten vor 2015, 2. Quartal";

        for(var i=0;i<wordsToFetchAgain.length;i++) {
            addDataToWordOccurenceChart(wordsToFetchAgain[i], chart);
            await Sleep(500);
        }




    }

}

function Sleep(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

function initLuhzeChart(chart, word1, word2) {


	fetchFileAPI("minAndMaxYearAndQuarter", function (data) {

            var firstYear = data['minYearAndQuarter'].toString().substring(0, 4);
            var firstQuarter = data['minYearAndQuarter'].toString().slice(-1);

            var lastYear = data['maxYearAndQuarter'].toString().substring(0, 4);
            var lastQuarter = data['maxYearAndQuarter'].toString().slice(-1);

            //data verarbeiten
            dataArrayWord1 = [];
            dataArrayWord2 = [];
            //erstellen eines array mit durchgehenden daten
            fetchParameterAPI("wordOccurence", "word", word1, (data) => {
                if("Error. The word does not exists." === data) {
                    console.log("Error. The word " + word1 + " does not exists.");
                    var input = document.getElementById("wordInput");
                    input.value = "";
                    input.placeholder = "Wort nicht gefunden";
                    return 1;
                }
                var word1Data = data;
                fetchParameterAPI("wordOccurence", "word", word2, (data) => {

                if("Error. The word does not exists." === data) {
                    console.log("Error. The word " + word2 + " does not exists.");
                    var input = document.getElementById("wordInput");
                    input.value = "";
                    input.placeholder = "Wort nicht gefunden";
                    return 1;
                }

                var word2Data = data;

                for(var i=firstYear;i<=lastYear;i++) {
                    for(var q=firstQuarter;q<=4;q++) {
                        // translate quarter to date
                        var month = ((q * 3) -2).toString();
                        if(month.length < 2) {
                            var date = i.toString() + "-0" + month + "-01";
                        } else {
                            var date = i.toString() + "-" + month + "-01";
                        }
                        //check if current date (i+q) is in data array
                        var foundInDataSetWord1 = false;
                        for(var k=0;k<word1Data.length;k++) { //overwrites den eintrag von zuvor
                            if(word1Data[k]['yearAndQuarter'] == i.toString() + q.toString()) {

                                foundInDataSetWord1 = true;
                                console.log(date + " | " + DateTime.fromISO(date).valueOf());
                                dataArrayWord1.push({t:DateTime.fromISO(date).valueOf(),y:word1Data[k]['occurencePerWords']});
                            }
                        }
                        if(foundInDataSetWord1 == false) dataArrayWord1.push({t:DateTime.fromISO(date).valueOf(),y:0});

                        //check if current date (i+q) is in data array
                        var foundInDataSetWord2 = false;
                        for(var k=0;k<word2Data.length;k++) { //overwrites den eintrag von zuvor
                            if(word2Data[k]['yearAndQuarter'] == i.toString() + q.toString()) {

                                foundInDataSetWord2 = true;
                                console.log(date + " | " + DateTime.fromISO(date).valueOf());
                                dataArrayWord2.push({t:DateTime.fromISO(date).valueOf(),y:word2Data[k]['occurencePerWords']});
                            }
                        }
                        if(foundInDataSetWord2 == false) dataArrayWord2.push({t:DateTime.fromISO(date).valueOf(),y:0});

                    }
                    firstQuarter = 1;
                }


                var configForFinancialCharts = {
		data: {
			datasets: [{label: word1.toUpperCase(),
                                borderColor: colorArray[0],
                                backgroundColor: colorArrayAlpha[0],
                                data: dataArrayWord1,
                                type: 'line',
                                pointRadius: 0,
                                fill: true,
                                lineTension: 0,
                                borderWidth: 2},
                                {label: word2.toUpperCase(),
                                borderColor: colorArray[1],
                                backgroundColor: colorArrayAlpha[1],
                                data: dataArrayWord2,
                                type: 'line',
                                pointRadius: 0,
                                fill: true,
                                lineTension: 0,
                                borderWidth: 2}]
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
					afterBuildTicks: function(scale, ticks) {
					    if(ticks != null) {
                            var majorUnit = scale._majorUnit;
                            var firstTick = ticks[0];
                            var i, ilen, val, tick, currMajor, lastMajor;

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
		  			fontSize: 15,
		  		}
		  	}

		}
	};
 window.myLine = new Chart(document.getElementById("wordOccurenceChart").getContext("2d"), configForFinancialCharts);

                });

            });

	    });



}

function deleteDataFromWordOccurenceChart(word, chart) {

    var newArray = [];
   for(var i=0;i<chart.data.datasets.length;i++) {
            if(word === chart.data.datasets[i]['label']) {
               //do nothing
        } else {
            newArray.push(chart.data.datasets[i]);
        }
    }
    return newArray;
}
