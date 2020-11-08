function showAutorinnenSeite(firstName, lastName, backInTime) {


	document.getElementsByClassName("graphContent")[0].style.display = "none";
	document.getElementsByClassName("ranking")[0].style.display = "none";
	document.getElementsByClassName("autorinnenSeite")[0].style.display = "block";

	displayAuthorSite(firstName, lastName, backInTime);


}

function displayAuthorSite(firstName, lastName, backInTime) {
	var tslaChart = document.getElementById("tslaChart");
	var cpdChart = document.getElementById("cpdChart");
	var acChart = document.getElementById("acChart");

	document.getElementsByClassName("autorinnenName")[0].innerHTML = (firstName + " " +  lastName).trim();
	document.getElementsByClassName("backInTimeHeader")[0].innerHTML = backInTime;

	addAuthorRankingChart(backInTime, tslaFunction, "Punkte", "Punkte", "Tage seit dem letzten Artikel", firstName, lastName, 0,200,10, tslaChart);

	addAuthorRankingChart(backInTime, cpdFunction, "Punkte", "Punkte", "Geschriebene Zeichen pro Tag", firstName, lastName, 0,500,20, cpdChart);

	addAuthorRankingChart(backInTime, acFunction, "Punkte", "Punkte", "Anzahl der Artikel", firstName, lastName, 0,70,5, acChart);

}


function addAuthorRankingChart(backInTime, functionToPass, labelString, yLabelString, xLabelString, firstName, lastName, start, stop, step, chart) {

	fetchTwoParameterAPI("singleRanking" + backInTime, "firstName", "lastName", firstName, lastName, function (data) {

		dataArray = [];
		labelArray = [];

		for(var i=start;i<stop;i+=step) {
			dataArray.push(functionToPass(i).toFixed(2));
			labelArray.push(i);
		}

		var config = {
			type: 'line',
			data: {labels: labelArray,
					datasets: [{
					label: labelString,
					backgroundColor: "red",
					borderColor: "red",
					pointRadius: 0,
					fill: false,
					lineTension: 0,
					borderWidth: 2	,
					data: dataArray


				}]},
			options: {
				responsive: true,
				title: {
					display: true,
					text: 'Vielleicht was statt den <p im graphContent??'
				},
				tooltips: {
					mode: 'index',
					intersect: false,
				},
				hover: {
					mode: 'nearest',
					intersect: true
				},
				scales: {
					xAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: xLabelString
						}
					}],
					yAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: yLabelString
						}
					}]
				}
			}
		};

		new Chart(chart.getContext('2d'), config);

	});



}



