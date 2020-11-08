var rankingTimeSinceLastArticleWeight = 1.4
var rankingCharactersPerDayWeight = 1.4
var rankingArticlesCountWeight = 1.2




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
		var scoreOfLastDataIndex; //um danger zone zu setzen
		var authorArray = [];
		
		for(var i=0;i<data.length;i++) {

			var rankingCPD = cpdFunction(Math.round(data[i]['charcount'] / data[i]['daysSinceFirstArticle']));
			var rankingTSLA = tslaFunction(data[i]['daysSinceLastArticle']);
			var rankingAC = acFunction(data[i]['articleCount']);
			var scoreNow = Math.round(rankingAC + rankingTSLA + rankingCPD);


			var scoreBackInTime = 0;
			if(data[i]['articleCountBackInTime'] > 0) { //die autorin gab es damals noch nicht
				rankingCPD = cpdFunction(Math.round(data[i]['charcountBackInTime'] / data[i]['daysSinceFirstArticleBackInTime']));
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

			var name = (data[i]['firstName'] + " " + data[i]['lastName']).trim();

			authorArray.push({
				"name": name,
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

			addInnterHTML += "<div class=\"ranks\"><div class=\"rankName\"><a href=\"javascript:showAutorinnenSeite()\" class=\"linkToAutorinnenSeite\">" + authorArray[i]['name'] + "</a></div><div class=\"rankScore\">" + authorArray[i]['score'] + "</div><div class=\"rankAdjective\" style=\"color: " + authorArray[i]['color'] + ";\">" + authorArray[i]['adjectiv'] + "</div><div class=\"rankDiff\">" + authorArray[i]['diff'] + " </div></div>";

			scoreOfLastDataIndex = authorArray[i]['score'];

		}

		addInnterHTML += "</div>"; //end danger zone div

		rankingSection.innerHTML = addInnterHTML;

		//show up arrow and footer
		arrow.style.display = "block";
		footer.style.display = "block";
	});


	
}





function tslaFunction(value) {
    // function is using months not days so
    var value = Math.round(value / 30.5)
    // to avoid math overflow when passing month thats to big
    if(value > 5) { //also letzter artikel älter als 5 monate
        return Math.round(-0.5 * value)  // linear loosing points over time
    } else {
		var result = Math.round(-10 / (0.1 + 10 * Math.exp(-1.3 * value)) + 100)
		return Math.round(result * rankingTimeSinceLastArticleWeight)
	}
}

function cpdFunction(value) {
	var result = Math.round(10 / (0.103 + 2.5 * Math.exp(-0.02 * value)))
	return Math.round(result * rankingCharactersPerDayWeight)
}


function acFunction(value) {
	var result = Math.round(10 / (0.1 + Math.exp(-0.4 * value)) - 10)
	return Math.round(result * rankingArticlesCountWeight)
}



function showRanking() {


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
