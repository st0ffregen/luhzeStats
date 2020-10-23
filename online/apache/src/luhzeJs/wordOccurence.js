
var colorArray = ["rgb(102, 176, 50)","rgb(134, 1, 175)","rgb(27,52,9)"];

		var colorArrayAlpha = ["rgba(102, 176, 50,0.5)","rgba(134, 1, 175,0.5)","rgb(27,52,9,0.5)"];



function addDataToWordOccurenceChart(word, chart) {
			
	//only add a word with max 4 words
	var maxValue = 4; //in die env???
	if(chart.data.datasets.length<=maxValue) {
	    fetchParameterAPI("wordOccurence", "word", word, (data) => {
	        //data verarbeiten
	        dataArray = [];
            for(var i=0;i<data.length;i++) {
                dataArray [i] = {t:moment(data[i]['table'],'YYYY-MM-DD').valueOf(),y:data[i]['occurencePerWords']};

            }
	        var newDataset = {label: word,
							borderColor: colorArray[i],
							data: dataArray,
							type: 'line',
							pointRadius: 0,
							fill: false,
							lineTension: 0,
							borderWidth: 2};

			chart.data.datasets.push(newDataset);
            console.log(chart);
			chart.update();
	    });
	}




}


function buildWordOccurenceChartFirstTime() {

//create an array with sample words
var sampleData = [{'word1':'student', 'word2':'studentin'}, {'word1': 'student!','word2':'luhze'},{'word1':'frau','word2':'herr'}, {'word1':'htwk','word2':'uni'},{'word1':'studenten','word2':'studierende'}];

    //fetch data for one of the sample data
    var index = Math.floor(Math.random()*sampleData.length);

	fetchParameterAPI("wordOccurence", "word", sampleData[index]['word1'], (data) => {
        var wordOneData = data;
	    fetchParameterAPI("wordOccurence", "word", sampleData[index]['word2'], (data) => {

        wordOneArray = [];
        wordTwoArray = [];
		for(var i=0;i<data.length;i++) {
		    wordOneArray[i] = {t:moment(wordOneData[i]['table'],'YYYY-MM-DD').valueOf(),y:wordOneData[i]['occurencePerWords']};
            wordTwoArray[i] = {t:moment(data[i]['table'],'YYYY-MM-DD').valueOf(),y:data[i]['occurencePerWords']};
		}

		var configForWordOccurenceChart = configForFinancialCharts;

        configForWordOccurenceChart.data.datasets = [{label: sampleData[index]['word1'],
							borderColor: 'blue',
							data: wordOneArray,
							type: 'line',
							pointRadius: 0,
							fill: false,
							lineTension: 0,
							borderWidth: 2},
							{label: sampleData[index]['word2'],
							borderColor: 'red',
							data: wordTwoArray,
							type: 'line',
							pointRadius: 0,
							fill: false,
							lineTension: 0,
							borderWidth: 2}];

		var wordOccurenceChart = document.getElementById("wordOccurenceChart").getContext("2d");
		console.log(wordOccurenceChart);
		
		window.myLine = new Chart(wordOccurenceChart, configForWordOccurenceChart);


	    });
	});

}