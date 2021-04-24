
window.onload = async function () {


    autocomplete(document.getElementById("wordInput"));

    //create an array with sample words
    var sampleData = [{'word1':'student', 'word2':'studentin'}, {'word1': 'luhze','word2':'student!'},{'word1':'frau+++frauen+++dame+++damen','word2':'mann+++männer+++herr+++herren'}, {'word1':'htwk','word2':'uni'},{'word1':'studenten','word2':'studierende+++studierenden'}];

    //fetch data for one of the sample data
    var index = Math.floor(Math.random()*sampleData.length);

    initLuhzeChart(document.getElementById("wordOccurenceChart"), sampleData[index]['word1'], sampleData[index]['word2']);


    fetchChartsSite();
}

