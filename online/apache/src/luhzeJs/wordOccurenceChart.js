
var config = {
	type: 'line',
	data: { datasets: []},
	options: {
		scales: {
					xAxes: [{
						type: 'time',
						distribution: 'linear',
						offset: true,
						time: {
							 unit: 'year'
						},
						
					}],
					yAxes: [{
						ticks: {
							beginAtZero: true
						}
					}]  				},
 				tooltips: {
      mode: 'nearest',
      intersect: false
    }
	}
	};


window.onload = function() {
	chart = document.getElementById('wordChart').getContext('2d');
window.myLine = new Chart(chart,config);

		};

