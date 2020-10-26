
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
	} else {
	    //handle errors
	    //delete first word and add the givin input word
        chart.data.datasets = deleteDataFromWordOccurenceChart(chart.data.datasets[0]['label'], chart);

	    //add the givin input word
	    addDataToWordOccurenceChart(word, chart);
	}

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
