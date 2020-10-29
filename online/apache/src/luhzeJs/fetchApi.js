async function fetchFileAPI(route,useDataFunction) {
	try {
		await fetch("http://localhost/json/" + route)
		.then(res => {
			if(res.ok) {
				return res.json();
			} else {
				return Promise.reject(res.status);
			}
		}).then(data => useDataFunction(data)
		).catch(err => {
			console.log('Error: ', err);
		});

	} catch(e) {
		console.error(e.message);
	}

	return 1;

}

async function fetchParameterAPI(route, parameter, parameterValue, useDataFunction) {


	try {
		await fetch("http://localhost/json/" + route + "?" + parameter + "=" + parameterValue)
		.then(res => {
			if(res.ok) {
				return res.json();
			} else {
				return Promise.reject(res.status);
			}
		}).then(data => useDataFunction(data)

		).catch(err => {
			console.log('Error: ', err);
		});

	} catch(e) {
		console.error(e.message);
	}

	return 1;

}


//fetchChartsSite();

function fetchChartsSite() { 

fetchFileAPI("minAuthor",(data) => {
	document.getElementById("authorP").innerHTML="Nur Autor*innen mit mehr als " + data['minAuthor'] + " miteinbezogen";
});

fetchFileAPI("date",(data) => {
	document.getElementById("dateP").innerHTML="Zuletzt aktualisiert " + data['date'] + "<span><a href=\"javascript:rankingFunction(0)\"> > Zum Ranking</a></span>";
});


fetchFileAPI("articlesTimeline",(data) => {
	financialChart('articlesTimelineChart',articlesTimelineFinancial(data),'month');
	financialChart('articlesTimelineDerivativeChart',articlesTimelineFinancialDerivation(data),'month');
});

fetchFileAPI("authorTimeline",(data) => {
	googleTimeline('authorTimelineChart',data);
}); 

fetchFileAPI("oldestArticle", (data) => {
	var oldestArticle = data;
	fetchFileAPI("newestArticle",(data) => {
		var newestArticle = data;
		fetchFileAPI("activeMembers",(data) => {
			financialChart('activeMembersChart',activeMembersFinancial(data,oldestArticle,newestArticle),'quarter');
		});
	});
});

fetchFileAPI("authorTopList",(data) => {
	barChart('authorTopListChart',data, 'bar', 'Anzahl der Artikel pro Autor*in',true);
});

fetchFileAPI("authorAverage",(data) => {
	barChart('authorAverageChart',data, 'bar', 'Durchschnittliche Anzahl von Zeichen pro Autor*in',true);
});

fetchFileAPI("mostArticlesPerTime", (data) => {
	barChart('mostArticlesPerTimeChart',data, 'bar', 'Zeitspanne zwischen zwei Artikeln in Tagen',true);
});

fetchFileAPI("averageCharactersPerDay",(data) => {
	barChart('averageCharactersPerDayChart',data,'bar','Durchschnittliche Anzahl von geschriebenen Zeichen pro Tag',true);
});

fetchFileAPI("ressortTimeline",(data) => {
	googleTimeline('ressortTimelineChart', data);
}); 

fetchFileAPI("topAuthorsPerRessort", (data) => {
	var func = customTooltip(data);
	fetchFileAPI("ressortTopList",(data) => {
		barChart('ressortTopListChart',data,'bar','Anzahl der Artikel pro Ressort',false, func);
	});
});

fetchFileAPI("oldestArticle",(data) => { //unnötig hier die variablen mehrmals im code abzufragen
	var oldestArticle = data;
	fetchFileAPI("newestArticle",(data) => {
		var newestArticle = data;
		fetchFileAPI("ressortArticlesTimeline",(data) => {
			//create color and hidden array to hide and color the same lines
			var colorArray = getRandomHexColor(data.length);

			

			if(data.length === 1) { //wenn es nur einen datensatz (ein ressort) gibt
				hiddenArray = [0];
			} else {
				//generate two random displayed ressorts
				var hiddenArray = [data.length];
				var randomNumber1 = Math.floor(Math.random() * data.length);
				var randomNumber2 = 0;

				do { //verhindern dass das selbe ressort random ausgewaehlt wird
					randomNumber2 = Math.floor(Math.random() * data.length);
				} while(randomNumber1 === randomNumber2);

				for(var i=0;i<data.length;i++) {
					if(i===randomNumber1 || i===randomNumber2) {
						hiddenArray[i] = 0;//true;
					} else {
						hiddenArray[i] = 1;//false;
					}
					
				}
			}
			financialChart('ressortArticlesTimelineChart',ressortArticlesTimelineFinancial(data,colorArray,hiddenArray, oldestArticle, newestArticle),'month');
			financialChart('ressortArticlesTimelineDerivativeChart',ressortArticlesTimelineFinancialDerivation(data,colorArray,hiddenArray,oldestArticle, newestArticle),'quarter');
		});
	});
	
});

fetchFileAPI("ressortAverage",(data) => {
	barChart('ressortAverageChart',data,'bar','Durchschnittliche Anzahl an Zeichen pro Ressort',true);
});

}