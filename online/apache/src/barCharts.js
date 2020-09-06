function barChart(id, data, type,label, tooltipBoolean, customTooltip) {

	var colorArray = [];
	var nameArray = [];
	var valueArray = [];
	for(var i=0;i<data.length;i++) {
		nameArray.push(data[i]['name']);
		valueArray.push(data[i]['count']);
		colorArray.push(getSingleRandomColor(alpha));
	}

	var getChart = document.getElementById(id).getContext('2d');
	var chart = new Chart(getChart, {
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
		  	}
		}
	});

}