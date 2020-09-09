async function fetchAPI(file,useDataFunction) {
	try {
		await fetch("http://localhost/json/" + file)
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

rankingFunction(0);

function fetchChartsSite() { 

fetchAPI("minAuthor",(data) => {
	document.getElementById("authorP").innerHTML="only authors with " + data['minAuthor'] + " and more articles included";
});

fetchAPI("date",(data) => {
	document.getElementById("dateP").innerHTML="last updated " + data['date'] + "<span><a href=\"javascript:rankingFunction(0)\"> >Take me to the ranking</a></span>";
});

fetchAPI("articlesTimeline",(data) => {
	financialChart('articlesTimelineChart',articlesTimelineFinancial(data),'month');
	financialChart('articlesTimelineDerivativeChart',articlesTimelineFinancialDerivation(data),'month');
});

fetchAPI("authorTimeline",(data) => {
	googleTimeline('authorTimelineChart',data);
}); 

fetchAPI("oldestArticle", (data) => {
	var oldestArticle = data;
	fetchAPI("newestArticle",(data) => {
		var newestArticle = data;
		fetchAPI("activeMembers",(data) => {
			financialChart('activeMembersChart',activeMembersFinancial(data,oldestArticle,newestArticle),'quarter');
		});
	});
});

fetchAPI("authorTopList",(data) => {
	barChart('authorTopListChart',data, 'bar', 'number of articles per author',true);
});

fetchAPI("authorAverage",(data) => {
	barChart('authorAverageChart',data, 'bar', 'average number of characters per author',true);
});

fetchAPI("mostArticlesPerTime", (data) => {
	barChart('mostArticlesPerTimeChart',data, 'bar', 'time span between two articles in days',true);
});

fetchAPI("averageCharactersPerDay",(data) => {
	barChart('averageCharactersPerDayChart',data,'bar','average number of characters written every day',true);
});

fetchAPI("ressortTimeline",(data) => {
	googleTimeline('ressortTimelineChart', data);
}); 

fetchAPI("topAuthorsPerRessort", (data) => {
	var func = customTooltip(data);
	fetchAPI("ressortTopList",(data) => {
		barChart('ressortTopListChart',data,'bar','number of articles per ressort',false, func);
	});
});

fetchAPI("oldestArticle",(data) => { //unnötig hier die variablen mehrmals im code abzufragen
	var oldestArticle = data;
	fetchAPI("newestArticle",(data) => {
		var newestArticle = data;
		fetchAPI("ressortArticlesTimeline",(data) => {
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

fetchAPI("ressortAverage",(data) => {
	barChart('ressortAverageChart',data,'bar','average number of characters per ressort',true);
});

}