var alpha = 0.45;

function getSingleRandomColor(alpha) {
	var colorString = "rgba(";
	for (var i = 0; i < 3; i++ ) {
		colorString += Math.floor(Math.random() * 256).toString() + ",";
	}
	colorString += alpha.toString() + ")";
	return colorString;
}

function getRandomHexColor(length) {
	var letters = "0123456789ABCDEF"; 
	var colorArray = [];

    // generating 6 times as HTML color code consist 
    // of 6 letter or digits 
    for(var k=0;k<length;k++) {
    	// html color code starts with # 
    	var color = '#'; 
    	for (var i = 0; i < 6; i++) {
    		color += letters[(Math.floor(Math.random() * 16))]; 
    	}
    	colorArray.push(color);

    }	
    return colorArray;
}


function monthArray(oldestDate,newestDate) {
    var dateArray = [];
    //fill an array with all months so that we can make sure that we have for all months data
    while((oldestDate.getMonth() <= newestDate.getMonth() && oldestDate.getFullYear()<=newestDate.getFullYear()) || oldestDate.getFullYear()<newestDate.getFullYear()) {//till its the same month and year

        dateArray.push([oldestDate.getFullYear(), oldestDate.getMonth(),0]);
        oldestDate.setMonth(oldestDate.getMonth()+1);
    } 
    return dateArray;
}


function quarterArray(oldestDate,newestDate) {
    var dateArray = [];
    //fill an array with all quartes so that we can make sure that we have for all quartes data
    while((Math.floor(oldestDate.getMonth()/3) <= Math.floor(newestDate.getMonth()/3) && oldestDate.getFullYear()<=newestDate.getFullYear()) || oldestDate.getFullYear()<newestDate.getFullYear()) {//till its the same quarter and year
        
        dateArray.push([oldestDate.getFullYear(),Math.floor(oldestDate.getMonth()/3),0]);
        oldestDate.setMonth(oldestDate.getMonth()+3);
    } 
    return dateArray;
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0; // For Safari
  document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
} 