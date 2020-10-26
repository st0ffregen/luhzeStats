
var colorArray = ["rgb(102, 176, 50)","rgb(134, 1, 175)","rgb(27,52,9)"];

var colorArrayAlpha = ["rgba(102, 176, 50,0.5)","rgba(134, 1, 175,0.5)","rgb(27,52,9,0.5)"];

function addDataToWordOccurenceChart(word, chart) {
			
	//only add a word with max 4 words
	var maxValue = 4; //in die env???
	if(chart.data.datasets.length<=maxValue) {
	    fetchFileAPI("minAndMaxYearAndQuarter", function (data) {

            var firstYear = data['minYearAndQuarter'].toString().substring(0, 4);
            var firstQuarter = data['minYearAndQuarter'].toString().slice(-1);

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
                                dataArray.push({t:moment(date,'YYYY-MM-DD').valueOf(),y:data[k]['occurencePerWords']});
                            }
                        }
                        if(foundInDataSet == false) dataArray.push({t:moment(date,'YYYY-MM-DD').valueOf(),y:0});

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
