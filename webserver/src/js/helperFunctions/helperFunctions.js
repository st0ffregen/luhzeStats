let alpha = 0.45;

function getSingleRandomColor(alpha) {
	let colorString = "rgba(";
	for (let i = 0; i < 3; i++ ) {
		colorString += Math.floor(Math.random() * 256).toString() + ",";
	}
	colorString += alpha.toString() + ")";
	return colorString;
}

function getRandomHexColorArray(length) {
	let letters = "0123456789ABCDEF";
	let colorArray = [];

    // generating 6 times as HTML color code consist 
    // of 6 letter or digits 
    for(let k=0;k<length;k++) {
    	// html color code starts with # 
    	let color = '#';
    	for (let i = 0; i < 6; i++) {
    		color += letters[(Math.floor(Math.random() * 16))]; 
    	}
    	colorArray.push(color);

    }	
    return colorArray;
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0; // For Safari
  document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}


function calculateDateToGetDataFor(direction, step, date) {

    switch (direction) {
        case 'today':
            date = new Date();
            break;

        case 'back':
            switch (step) {
                case 'day':
                    date.setDate(date.getDate() - 1);
                    break;
                case 'month':
                    date.setMonth(date.getMonth() - 1);
                    break;
                case 'year':
                    date.setFullYear(date.getFullYear() - 1);
                    break;
            }
            break;
        case 'forth':
            switch (step) {
                case 'day':
                    date.setDate(date.getDate() + 1);
                    break;
                case 'month':
                    date.setMonth(date.getMonth() + 1);
                    break;
                case 'year':
                    date.setFullYear(date.getFullYear() + 1);
                    break;
            }
            break;
    }

    if (date > new Date()) {
        date = new Date();
    }

    return date;
}

function writeDateToDomElement(elementId, date) {
    document.getElementById(elementId).innerHTML = date.toLocaleDateString();
}