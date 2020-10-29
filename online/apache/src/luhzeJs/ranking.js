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

	fetchFileAPI("ranking" + backInTimeString,(data) => {

		var addInnterHTML = "";
		
		for(var i=0;i<data.length;i++) {

			
			if(i!=0 && data[i]['score']<0 && data[i-1]['score']>=0) { //put danger zone
				addInnterHTML += "<hr><h1 class=\"dangerzone\">!!!DANGER ZONE!!!</h1><div class=\"danger\">";
			}
			 
			addInnterHTML += "<div class=\"ranks\"><div class=\"rankName\">" + data[i]['name'] + "</div><div class=\"rankScore\">" + data[i]['score'] + "</div><div class=\"rankAdjective\" style=\"color: "+ data[i]['color'] + ";\">" + data[i]['adjectiv'] + "</div><div class=\"rankDiff\">" + data[i]['div'] + " </div></div>";
			

		}
		addInnterHTML += "</div>"; //end danger zone div

		rankingSection.innerHTML = addInnterHTML;

		//show up arrow and footer
		arrow.style.display = "block";
		footer.style.display = "block";
	});


	
}




function showRanking(el, graphContent) {


	document.getElementsByClassName("graphContent")[0].style.display = "none";
	rankingFunction('Default');
	
}

function hideRanking(el) {

	document.getElementsByClassName("ranking")[0].style.display = "none";
	document.getElementsByClassName("graphContent")[0].style.display = "block";

	fetchChartsSite();

}
