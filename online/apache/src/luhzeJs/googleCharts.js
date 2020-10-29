window.onresize = function() { //traffic aufwending
	fetchFileAPI("authorTimeline",(data) => {
		googleTimeline('authorTimelineChart', data);
		fetchFileAPI("ressortTimeline", (data) => {
			googleTimeline('ressortTimelineChart', data);
		});
	}); 
}

function googleTimeline(chartAttr,dataArrayAttr) {

	google.charts.load("current", {packages:["timeline"]});
	google.charts.setOnLoadCallback(drawChart);
	var chartString = chartAttr;
	var dataArray = dataArrayAttr;

	function drawChart() {

		var container = document.getElementById(chartString);
		var chart = new google.visualization.Timeline(container);
		var dataTable = new google.visualization.DataTable();
		dataTable.addColumn({ type: 'string', id: 'Term' });
		dataTable.addColumn({ type: 'string', id: 'Name' });
		dataTable.addColumn({ type: 'date', id: 'Start' });
		dataTable.addColumn({ type: 'date', id: 'End' });

		for(var i=0;i<dataArray.length;i++) {

			dataTable.addRows([["", dataArray[i]['name'], new Date(dataArray[i]['min']), new Date(dataArray[i]['max'])]]); //name is here equivilant to ressort name

		}

		var options = {
			timeline: { 
				showRowLabels: false 
			},
			backgroundColor: '#eee'
		};

		chart.draw(dataTable, options);
	}
}