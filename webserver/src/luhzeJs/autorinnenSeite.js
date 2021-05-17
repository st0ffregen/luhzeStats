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

		var cpd = data['charsPerDay'];
		var tsla = data['daysSinceLastArticle'];
		var ac = data['articleCount'];

		var rankingCPD = cpdFunction(cpd);
		var rankingTSLA = tslaFunction(tsla);
		var rankingAC = acFunction(ac);

		var cpdBackInTime = data['charsPerDayBackInTime'];
		var tslaBackInTime = data['daysSinceLastArticleBackInTime'];
		var acBackInTime = data['articleCountBackInTime'];

		var rankingCPDBackInTime = cpdFunction(cpdBackInTime);
		var rankingTSLABackInTime = tslaFunction(tslaBackInTime);
		var rankingACBackInTime = acFunction(acBackInTime);

		var scoreNow = Math.round(rankingAC + rankingTSLA + rankingCPD);

		var scoreBacKInTime = Math.round(rankingACBackInTime + rankingTSLABackInTime + rankingCPDBackInTime);

		addAuthorRankingChart(backInTime, tslaFunction, "Punkte", "Punkte",
			"Tage seit dem letzten Artikel", firstName, lastName, 0, 200, 1, tslaChart,
			tsla, tslaBackInTime, "time since last article function");

		addAuthorRankingChart(backInTime, cpdFunction, "Punkte", "Punkte",
			"Geschriebene Zeichen pro Tag", firstName, lastName, 0, 500, 1, cpdChart,
			cpd, cpdBackInTime, "characters per day function");

		addAuthorRankingChart(backInTime, acFunction, "Punkte", "Punkte",
			"Anzahl der Artikel", firstName, lastName, 0, 70, 1, acChart,
			ac, acBackInTime, "article count function");


		addMathToDiv("tslaMathDiv", "$$tslaFunc(x) = tslaWeight \\cdot \\begin{cases} 100\e^{-0.01x}, & \\text{if } x<100\\cdot ln(5) \\\\  -\\frac{\\sqrt{2}x}{100} , & \\text{otherwise} \\end{cases}$$");

		addMathToDiv("cpdMathDiv", "$$cpdFunc(x) = -100(\e^{-0.01x}-1) \\cdot cpdWeight$$");

		addMathToDiv("acMathDiv", "$$acFunc(x) = -100(\e^{-0.1x} - 1) \\cdot acWeight$$");

		addMathToDiv("calculationMathDiv", "Für " + firstName + " " + lastName + "" +
			" ergibt sich am Datum !!! eine aktuelle Punktzahl aus $$tslaFunc(" + tsla + ") + cpdFunc" +
			"(" + cpd + ") + acFunc(" + ac + ") = " + scoreNow + "$$");

		MathJax.typeset(); //lädt das neue mathjax ein

	});
}


function addMathToDiv(divName, math) {

	var mathDiv = document.getElementById(divName);

	var mathParagraph = document.createElement("p");

	mathParagraph.className = "math";

	var math = document.createTextNode(math);

	mathParagraph.appendChild(math);

	mathDiv.appendChild(mathParagraph);

}


function addAuthorRankingChart(backInTime, functionToPass, labelString, yLabelString, xLabelString, firstName, lastName, start, stop, step, chart, firstIndex, secondIndex, functionName) {

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
					text: functionName
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

