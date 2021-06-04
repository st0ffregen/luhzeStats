async function rankingFunction(daysBackInTime) {

    prepareSiteForRanking();

    const response = await fetch('http://localhost/api/ranking?daysBackInTime=' + daysBackInTime.toString());
    const fetchedData = await response.json();

    let newRankingInnerHTML = processRankingData(fetchedData);
    writeChangesToDom(newRankingInnerHTML);
}


function prepareSiteForRanking() {
    let rankingDiv = document.getElementsByClassName('ranking')[0];
    let rankingSectionDiv = rankingDiv.getElementsByClassName('rankingSection')[0];
    rankingSectionDiv.innerHTML = '';
    rankingDiv.style.display = "block";

    //delete arrow and footer
    let arrow = document.getElementsByClassName('upArrowButtonDiv')[0];
    let footer = document.getElementsByClassName('footer')[0];
    arrow.style.display = 'none';
    footer.style.display = 'none';
}


function writeChangesToDom(newRankingInnerHTML) {
    let rankingDiv = document.getElementsByClassName('ranking')[0];
    let rankingSectionDiv = rankingDiv.getElementsByClassName('rankingSection')[0];
    rankingSectionDiv.innerHTML = newRankingInnerHTML;
    let arrow = document.getElementsByClassName('upArrowButtonDiv')[0];
    let footer = document.getElementsByClassName('footer')[0];
    arrow.style.display = 'block';
    footer.style.display = 'block';
}


function processRankingData(fetchedData) {
    let newRankingInnerHTML = '';
    let authorArray = [];

    for (let i = 0; i < fetchedData.length; i++) {

        let diff = fetchedData[i]['rankingScoreDiff'];
        let description = '';
        let color = '';

        if (diff >= 50) {
            description = 'rising underdog';
            color = "#32CD32";
        } else if (diff >= 10) {
            description = 'ascending';
            color = "#6B8E23";
        } else if (diff < 10 && diff > -10) {
            description = 'stagnating';
            color = "#FFA500";
        } else if (diff <= -50) {
            description = 'free falling';
            color = "#FF0000";
        } else if (diff <= -10) {
            description = 'decending';
            color = "#8B0000";
        }

        if (diff > -1) {
            diff = "+" + diff.toString();
        }

        authorArray.push({
            'name': fetchedData[i]['name'],
            'score': fetchedData[i]['rankingScore'].toString(),
            'color': color,
            'description': description,
            'diff': diff
        });
    }

    authorArray.sort(function (a, b) {
        return b.score - a.score;
    });

    for (let i = 0; i < authorArray.length; i++) {
        let scoreOfLastDataIndex = 0;

        if (i !== 0 && authorArray[i]['score'] < 0 && scoreOfLastDataIndex >= 0) { //put danger zone
            newRankingInnerHTML += '<hr><h1 class="dangerZone">!!!DANGER ZONE!!!</h1><div class=\"danger\">';
        }

        newRankingInnerHTML += '<div class="ranks"><div class="rankName">' + authorArray[i]['name'] + '</div><div class="rankDescription">' + authorArray[i]['score'] + '</div><div class="rankAdjective" style="color: ' + authorArray[i]['color'] + ';">' + authorArray[i]['description'] + '</div><div class="rankDiff">' + authorArray[i]['diff'] + ' </div></div>';
        scoreOfLastDataIndex = authorArray[i]['score'];
    }

    newRankingInnerHTML += '</div>'; //end danger zone div
    return newRankingInnerHTML;
}


function showRanking() {
    document.getElementsByClassName("graphContent")[0].style.display = "none";
    rankingFunction(0);
}


function hideRanking() {
    document.getElementsByClassName("ranking")[0].style.display = "none";
    document.getElementsByClassName("graphContent")[0].style.display = "block";
    fetchChartsSite();
}