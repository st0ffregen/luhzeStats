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

	fetchTwoParameterAPI("singleRanking" + backInTime, "firstName", "lastName", firstName, lastName, function (data) {

		var tsla = tslaFunction(data['daysSinceLastArticle']).toFixed(1);
		var tslaBackInTime = tslaFunction(data['daysSinceLastArticleBackInTime']).toFixed(1);

		var cpd = cpdFunction(data['charsPerDay']).toFixed(1);
		var cpdBackInTime = cpdFunction(data['charsPerDayBackInTime']).toFixed(1);

		var ac = acFunction(data['articleCount']).toFixed(1);
		var acBackInTime = acFunction(data['articleCountBackInTime']).toFixed(1);

		addAuthorRankingChart(backInTime, tslaFunction, "Punkte", "Punkte", "Tage seit dem letzten Artikel", firstName, lastName, 0, 200, 0.5, tslaChart, data['daysSinceLastArticle'], data['daysSinceLastArticleBackInTime']);

		addAuthorRankingChart(backInTime, cpdFunction, "Punkte", "Punkte", "Geschriebene Zeichen pro Tag", firstName, lastName, 0, 500, 0.5, cpdChart, data['charsPerDay'], data['charsPerDayBackInTime']);

		addAuthorRankingChart(backInTime, acFunction, "Punkte", "Punkte", "Anzahl der Artikel", firstName, lastName, 0, 70, 0.5, acChart, data['articleCount'], data['articleCountBackInTime']);

	});
}




function addAuthorRankingChart(backInTime, functionToPass, labelString, yLabelString, xLabelString, firstName, lastName, start, stop, step, chart, firstIndex, secondIndex) {

		var dataArray = [];
		var labelArray = [];

		for(var i=start;i<stop;i+=step) {
			dataArray.push(functionToPass(i).toFixed(1));
			labelArray.push(i);
		}


		var config = {
			type: 'line',
			cubicInterpolationMode: 'default',
			data: {labels: labelArray,
					datasets: [{
					label: labelString,
					backgroundColor: function(context) {
						var index = context.dataIndex;
						if(index === firstIndex) {
							return "red";
						} else if (index === secondIndex) {
							return "blue";
						}
						return "red";
					},
					borderColor: function(context) {
						var index = context.dataIndex;
						if(index === firstIndex) {
							return "red";
						} else if (index === secondIndex) {
							return "blue";
						}
						return "red";
					},
					pointRadius: function(context) {
						var index = context.dataIndex;
						if(index === firstIndex) {
							return 10;
						} else if (index === secondIndex) {
							return 10;
						}
						return 0;
					},
					fill: false,
					borderWidth: 2,
					data: dataArray
				}]},
			options: {
				responsive: true,
				title: {
					display: true,
					text: 'Vielleicht was statt den <p im graphContent??'
				},
				tooltips: {
					// Disable the on-canvas tooltip
					enabled: true,
					intersect: false,
					mode: 'index',
					/*filter: function (tooltipItem) {
						return tooltipItem.datasetIndex === 10;
					}*/
					//custom: customTooltip,
				},
				hover: {
					mode: 'nearest',
					intersect: false,
				},
				scales: {
					xAxes: [{
						display: true,
						distribution: 'linear',
						offset: true,
						ticks: {
							maxTicksLimit: 10
						},
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


}

