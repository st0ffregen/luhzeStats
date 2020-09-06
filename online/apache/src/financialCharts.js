
function customTooltip(data) {

	return customTooltips = function(tooltip) {

		var displayData = [];
		var displayLabel = [];
		var colorArray = [];

		try {
				//parse data to data array
				for(var i=0;i<data.length;i++) {
					if(data[i]['ressort'] == tooltip.title[0]) {

						for(var k=0;k<data[i]['authors'].length;k++) {
							colorArray.push(getSingleRandomColor(alpha));
							displayData.push(data[i]['authors'][k]['count']);
							//split name
							var split = data[i]['authors'][k]['name'].split(" ");
							var firstName = "";
							var lastName = "";
							//check if person has more that two names
							if(split.length > 2) {

								for(var l=0;l<split.length-1;l++) {
									firstName += split[l] + " ";

								}
								lastName = split[split.length-1].charAt(0) + ".";

							} else {
								firstName = split[0];
								lastName = " " + split[1].charAt(0) + ".";
							}	

							displayLabel.push(firstName+lastName);

						}
						break;
					}
				}
			} catch(error) { 
				if(!error instanceof TypeError) console.log(error);
			}

			// Tooltip Element
			var tooltipEl = document.getElementById('chartjs-tooltip');


			 // Hide if no tooltip
			 if (tooltip.opacity === 0) {
			 	tooltipEl.style.opacity = 0;
			 	return;
			 }

			 while (tooltipEl.firstChild) {    
			 	tooltipEl.removeChild(tooltipEl.firstChild);
			 }

			 var label = document.createElement('p');

			 if(displayData.length >0) {
			 	label.innerHTML = tooltip.title[0] + ": "  + tooltip.dataPoints[0].yLabel + "; top authors:";
			 	label.className = "chartjs";
			 	tooltipEl.appendChild(label);
			 	var child = document.createElement('canvas');
			 	child.id = 'tooltipChart';
			 	tooltipEl.appendChild(child);
			 } else {
			 	label.innerHTML = tooltip.title[0] + ": "  + tooltip.dataPoints[0].yLabel;
			 	tooltipEl.appendChild(label);
			 }

			// Set caret Position
			tooltipEl.classList.remove('above', 'below', 'no-transform');
			if (tooltip.yAlign) {
				tooltipEl.classList.add(tooltip.yAlign);
			} else {
				tooltipEl.classList.add('no-transform');
			}

			function getBody(bodyItem) {
				return bodyItem.lines;
			}

			// Set Text
			if (tooltip.body && displayData.length>0) {

				var chart = tooltipEl.children[1].getContext('2d');

				// For a pie chart
				var barChart = new Chart(chart, {
					type: 'bar',
					data: {
						datasets: [{
							data:displayData,
							label:displayLabel,
							borderWidth:1,
							fill:false,
							backgroundColor: colorArray,}],
							labels: displayLabel,


						}, options: {
							tooltips: {
								enabled: false
							},
							legend:false,
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

			var positionY = this._chart.canvas.offsetTop;
			var positionX = this._chart.canvas.offsetLeft + 50; //+50 so the most left chart wont be cut of by the computer screen

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

function articlesTimelineFinancial(data) {

	var totalArticleCount = 0;
	var dateArray = monthArray(new Date(data[data.length-1]['date']+"T00:00:00Z"),new Date(data[0]['date']+"T00:00:00Z"));
	
	var returnArray = [];
	for(var i=0;i<dateArray.length;i++) { //get a month
		for(var k=0;k<data.length;k++) { //get a date, check if in the month, then increase month count by one
			currentDate = new Date(data[k]['date']+"T00:00:00Z");
			if(currentDate.getMonth() === dateArray[i][1] && currentDate.getFullYear() === dateArray[i][0]) {
				totalArticleCount += data[k]['count'];
			}
		}

		returnArray[i] = {t:moment(dateArray[i][0]+"-"+(dateArray[i][1]+1).toString()+"-01",'YYYY-MM-DD').valueOf(),y:totalArticleCount};

	}

	return [{label: 'number of articles published',
	borderColor: '#ff6384',
	data: returnArray,
	type: 'line',
	pointRadius: 0,
	fill: false,
	lineTension: 0,
	borderWidth: 2}];

}

function articlesTimelineFinancialDerivation(data) {
	var dateArray = monthArray(new Date(data[data.length-1]['date']+"T00:00:00Z"),new Date(data[0]['date']+"T00:00:00Z"));
	
	var returnArray = [];
	for(var i=0;i<dateArray.length;i++) { //get a month
		for(var k=0;k<data.length;k++) { //get a date, check if in the month, then increase month count by one
			currentDate = new Date(data[k]['date']+"T00:00:00Z");
			if(currentDate.getMonth() === dateArray[i][1] && currentDate.getFullYear() === dateArray[i][0]) {
				dateArray[i][2] += data[k]['count']
			}
		}

		returnArray[i] = {t:moment(dateArray[i][0]+"-"+(dateArray[i][1]+1).toString()+"-01",'YYYY-MM-DD').valueOf(),y:dateArray[i][2]};

	}

	return [{label: 'number of articles published each month',
	borderColor: '#ff6384',
	data: returnArray,
	type: 'line',
	pointRadius: 0,
	fill: false,
	lineTension: 0,
	borderWidth: 2}];

}

function ressortArticlesTimelineFinancial(data,colorArray,hiddenArray, oldestArticle, newestArticle) {

	var datasetArray = [];
	for(var k=0;k<data.length;k++) {// get a ressort
		var returnArray = [];
		var dateArray = monthArray(new Date(oldestArticle['oldestArticle']+"T00:00:00Z"),new Date(newestArticle['newestArticle']+"T00:00:00Z"));
		var totalMonthlyArticles = 0;
		for(var i=0;i<dateArray.length;i++) { //loop through months

			if((dateArray[i][1]+1).toString().length === 1) {
				currentDateFromDateArray = dateArray[i][0]+"-0"+(dateArray[i][1]+1).toString()+"-01";
			} else {
				currentDateFromDateArray = dateArray[i][0]+"-"+(dateArray[i][1]+1).toString()+"-01";
			}
			
			if(data[k]['countPerMonth'].some(countPerMonth => countPerMonth.date ===  currentDateFromDateArray )) { //if there is a month in data array which is the same as the current month in dateArray
				//(dateArray[i][1]+1).toString() cause january is 0 in dateArray but not in sql
				var index = data[k]['countPerMonth'].map(function(e) {return e.date;}).indexOf(currentDateFromDateArray); //gives me the index 	
				totalMonthlyArticles += data[k]['countPerMonth'][index]['count']

			} 
		returnArray[i] = {t:moment(dateArray[i][0]+"-"+(dateArray[i][1]+1).toString()+"-01",'YYYY-MM-DD').valueOf(),y:totalMonthlyArticles}; //(dateArray[i][1]+1).toString()
		}

		datasetArray.push({label: data[k]['ressort'],
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



function ressortArticlesTimelineFinancialDerivation(data,colorArray,hiddenArray,oldestArticle, newestArticle) {

	var datasetArray = [];

	for(var k=0;k<data.length;k++) { //gives me a ressort

		var returnArray = [];
		//use a init date to determine if next date is in same quarter or not
		var dateArray = quarterArray(new Date(oldestArticle['oldestArticle']+"T00:00:00Z"),new Date(newestArticle['newestArticle']+"T00:00:00Z"));
		for(var i=0;i<dateArray.length;i++) {
			//loop through the empty date array (only dates in it by now) find the articles with another for loop
			articlesCount = 0;
			for(var l=0;l<data[k]['countPerMonth'].length;l++) {

				currentDate = new Date(data[k]['countPerMonth'][l]['date']+"T00:00:00Z");
				currentQuarter = Math.floor(currentDate.getMonth()/3);
				if(currentQuarter === dateArray[i][1] && currentDate.getFullYear() === dateArray[i][0]) {
					articlesCount += data[k]['countPerMonth'][l]['count']
				}
			}
			//after finding all articles and adding them up to articlesCount, we can change the dateArray entry to what we want for the chartjs
			returnArray[i] = {t:moment(dateArray[i][0]+"-"+((dateArray[i][1]*3)+1).toString()+"-01",'YYYY-MM-DD').valueOf(),y:articlesCount};//calculating the first month in each quarter
		}

		datasetArray.push({label: data[k]['ressort'],
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

function activeMembersFinancial(data, oldestArticle, newestArticle) {

	var dateArray = quarterArray(new Date(oldestArticle['oldestArticle']+"T00:00:00Z"),new Date(newestArticle['newestArticle']+"T00:00:00Z"));
	var returnArray = [];
	
	for(var i=0;i<dateArray.length;i++) { //gives me an quarter
		//loop through the empty date array (only dates in it by now) find the active authors with another for loop
		for(var k=0;k<data.length;k++) { //gives me an author
			for(var l=0;l<data[k]['articles'].length;l++) { //gives me the article array for the k author

				currentDate = new Date(data[k]['articles'][l]+"T00:00:00Z");
				currentQuarter = Math.floor(currentDate.getMonth()/3);
				if(currentQuarter === dateArray[i][1] && currentDate.getFullYear() === dateArray[i][0]) {
					dateArray[i][2]++;
					break;
					//breaks the article for loop, because we only need one article per quarter to prove that the author was active in that quarter
				}
			}
		}
		//after finding all articles and adding them up to articlesCount, we can change the dateArray entry to what we want for the chartjs
		returnArray[i] = {t:moment(dateArray[i][0]+"-"+((dateArray[i][1]*3)+1).toString()+"-01",'YYYY-MM-DD').valueOf(),y:dateArray[i][2]};//calculating the first month in each quarter
	}

	return [{label: 'active authors per quarter',
	borderColor: '#02a0e4',
	data: returnArray,
	type: 'line',
	pointRadius: 0,
	fill: false,
	lineTension: 0,
	borderWidth: 2}];

}

function financialChart(chart, dataFunc, tooltipString) {

	var ctx = document.getElementById(chart).getContext('2d');

	var cfg = {
		data: {
			datasets: dataFunc
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
						var majorUnit = scale._majorUnit;
						var firstTick = ticks[0];
						var i, ilen, val, tick, currMajor, lastMajor;

						val = moment(ticks[0].value);
						if ((majorUnit === 'minute' && val.second() === 0)
							|| (majorUnit === 'hour' && val.minute() === 0)
							|| (majorUnit === 'day' && val.hour() === 9)
							|| (majorUnit === 'month' && val.date() <= 3 && val.isoWeekday() === 1)
							|| (majorUnit === 'year' && val.month() === 0)) {
							firstTick.major = true;
						} else {
							firstTick.major = false;
						}
						lastMajor = val.get(majorUnit);

						for (i = 1, ilen = ticks.length; i < ilen; i++) {
							tick = ticks[i];
							val = moment(tick.value);
							currMajor = val.get(majorUnit);
							tick.major = currMajor !== lastMajor;
							lastMajor = currMajor;
						}
						return ticks;
					}

				}],
				yAxes: [{}] //not sure why i need this
			},
			hover: {
				mode: 'nearest',
				intersect: false
			},
			tooltips: {
				mode: 'nearest',
				intersect: false
			}
				
		}
	};


			if(tooltipString == 'month') {
				cfg.options.scales.xAxes[0].time['tooltipFormat'] = "MMM yyyy"
			} else if(tooltipString == 'quarter') {
				cfg.options.scales.xAxes[0].time['tooltipFormat'] = "q yyyy"
			}

			var chart = new Chart(ctx, cfg);
		
}
