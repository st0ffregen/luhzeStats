
window.onload = async function () {
    window.myLine = new Chart(document.getElementById("wordOccurenceChart").getContext("2d"), configForFinancialCharts);
    autocomplete(document.getElementById("wordInput"));

    //create an array with sample words
    var sampleData = [{'word1':'student', 'word2':'studentin'}, {'word1': 'student!','word2':'luhze'},{'word1':'frau','word2':'herr'}, {'word1':'htwk','word2':'uni'},{'word1':'studenten','word2':'studierende'}];

    //fetch data for one of the sample data
    var index = Math.floor(Math.random()*sampleData.length);

    document.getElementById("wordOccurenceChart").style.display = "none";
    addDataToWordOccurenceChart(sampleData[index]['word1'], window.myLine);
    await Sleep(400);
    addDataToWordOccurenceChart(sampleData[index]['word2'], window.myLine);
    await Sleep(100);
    document.getElementById("wordOccurenceChart").style.display = "block";
}

function Sleep(milliseconds) {
 return new Promise(resolve => setTimeout(resolve, milliseconds));
}