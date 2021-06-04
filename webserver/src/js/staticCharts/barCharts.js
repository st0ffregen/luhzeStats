Chart.defaults.global.defaultFontColor = '#555';

function barChart(chartElement, data, type, label, tooltipBoolean, customTooltip) {

	let colorArray = [];
	let nameArray = [];
	let valueArray = [];

	for(let i=0;i<data.length;i++) {
		nameArray.push(data[i]['name']);
		valueArray.push(data[i]['count']);
		colorArray.push(getSingleRandomColor(alpha));
	}

	let barChartConfig = {
		type: type,
		data: {
			labels: nameArray,
			datasets: [{
				backgroundColor: colorArray,
				fill:false,
				data: valueArray,
				label: label,
				borderWidth:1,
			}]
		},
		options: {
			tooltips: {
  			// Disable the on-canvas tooltip
	  		enabled: tooltipBoolean,
	  		mode: 'index',
	  		position: 'nearest',
	  		custom: customTooltip,
	  		},
		  	scales: {
		  		yAxes: [{
		  			ticks: {

		  				precision: 0
		  			}
		  		}]
		  	},
		  	animations: {
		  		duration:1000,
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

	const newGraph = new Chart(chartElement.getContext('2d'), barChartConfig);
    allCharts.push(newGraph);
}

