function rankingFunction(backInTime) {

	document.getElementsByClassName("graphContent")[0].style.display = "none";
	var div = document.getElementsByClassName("ranking")[0];
	var rankingSection = div.getElementsByClassName("rankingSection")[0];
	rankingSection.innerHTML = "";
	div.style.display = "block";

	//delete arrow and footer
	var arrow = document.getElementsByClassName("upArrowButtonDiv")[0];
	arrow.style.display = "none";
	var footer = document.getElementsByClassName("footer")[0];
	footer.style.display = "none";

	var backInTimeString = "Default";
	if(backInTime === 0) {
		backInTimeString = "Default";
	} else if(backInTime === 1) {
		backInTimeString = "Month";
	} else if(backInTime === 2) {
		backInTimeString = "Year";
	} else if(backInTime === 3) {
		backInTimeString = "TwoYears";
	} else if(backInTime === 4) {
		backInTimeString = "FiveYears";
	}

	fetchAPI("ranking" + backInTimeString,(data) => {
		
		for(var i=0;i<data.length;i++) {
			rankingSection.innerHTML += "<p class=\"ranks\">" + data[i]['name'] + " <span>" + data[i]['div'] + " <span style=\"color: "+ data[i]['color'] + ";\">" + data[i]['adjectiv'] + "</span> " + data[i]['score'] + "</span></p>";
		}

		//show up arrow and footer
		arrow.style.display = "block";
		footer.style.display = "block";
	});


	
}




function showRanking(el, graphContent) {
	
}

function hideRanking(el) {

	document.getElementsByClassName("ranking")[0].style.display = "none";
	document.getElementsByClassName("graphContent")[0].style.display = "block";

	fetchChartsSite();

}
