var rankingTimeSinceLastArticleWeight = Math.sqrt(2);
var rankingCharactersPerDayWeight = Math.sqrt(2);
var rankingArticlesCountWeight = 1;

function rankingFunction(backInTime) {


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
		var scoreOfLastDataIndex; //um danger zone zu setzen
		var authorArray = [];
		
		for(var i=0;i<data.length;i++) {

			var rankingCPD = cpdFunction(data[i]['charsPerDay']);
			var rankingTSLA = tslaFunction(data[i]['daysSinceLastArticle']);
			var rankingAC = acFunction(data[i]['articleCount']);
			var scoreNow = Math.round(rankingAC + rankingTSLA + rankingCPD);


			var scoreBackInTime = 0;
			if(data[i]['articleCountBackInTime'] > 0) { //die autorin gab es damals noch nicht
				rankingCPD = cpdFunction(data[i]['charsPerDayBackInTime']);
				rankingTSLA = tslaFunction(data[i]['daysSinceLastArticleBackInTime']);
				rankingAC = acFunction(data[i]['articleCountBackInTime']);
				scoreBackInTime = Math.round(rankingAC + rankingTSLA + rankingCPD);
			}

			var diff = scoreNow - scoreBackInTime;



			var adjectiv = "";
			var color = "";

			if (diff >= 50) {
				adjectiv = "rising star";
				color = "#32CD32";
			} else if (diff >= 10) {
				adjectiv = "ascending";
				color = "#6B8E23";
			} else if (diff < 10 && diff > -10) {
				adjectiv = "stagnating";
				color = "#FFA500";
			} else if (diff <= -50) {
				adjectiv = "free falling";
				color = "#FF0000";
			} else if (diff <= -10) {
				adjectiv = "decending";
				color = "#8B0000";
			}

			if(diff > -1) {
				diff = "+" + diff.toString();
			}

			authorArray.push({
				"firstName": data[i]['firstName'],
				"lastName": data[i]['lastName'],
				"score": scoreNow.toString(),
				"color": color,
				"adjectiv": adjectiv,
				"diff": diff
			});

		}

		authorArray.sort(function (a, b) {
		  return b.score - a.score;
		});

		for(var i=0;i<authorArray.length;i++) {

			if (i != 0 && authorArray[i]['score'] < 0 && scoreOfLastDataIndex >= 0) { //put danger zone
				addInnterHTML += "<hr><h1 class=\"dangerzone\">!!!DANGER ZONE!!!</h1><div class=\"danger\">";
			}

			addInnterHTML += '<div class="ranks"><div class="rankName"><a href=\'javascript:showAutorinnenSeite("' + authorArray[i]['firstName'] + '","' + authorArray[i]['lastName']  +  '","' +  backInTimeString + '")\' class="linkToAutorinnenSeite">' + (authorArray[i]['firstName'] + ' ' + authorArray[i]['lastName']).trim() + '</a></div><div class="rankScore">' + authorArray[i]['score'] + '</div><div class="rankAdjective" style="color: ' + authorArray[i]['color'] + ';">' + authorArray[i]['adjectiv'] + '</div><div class="rankDiff">' + authorArray[i]['diff'] + ' </div></div>';

			scoreOfLastDataIndex = authorArray[i]['score'];

		}

		addInnterHTML += "</div>"; //end danger zone div

		rankingSection.innerHTML = addInnterHTML;

		//show up arrow and footer
		arrow.style.display = "block";
		footer.style.display = "block";
	});


	
}



function showRanking() {

	var mathDivArray = document.getElementsByClassName("mathDiv");
	for(var i=0;i<mathDivArray.length;i++) {
		mathDivArray[i].innerHTML = "";
	}

	document.getElementsByClassName("graphContent")[0].style.display = "none";
	document.getElementsByClassName("autorinnenSeite")[0].style.display = "none";
	rankingFunction('Default');
	
}

function hideRanking() {

	document.getElementsByClassName("ranking")[0].style.display = "none";
	document.getElementsByClassName("autorinnenSeite")[0].style.display = "none";
	document.getElementsByClassName("graphContent")[0].style.display = "block";

	fetchChartsSite();

}
