var input = document.getElementById("wordInput");


input.addEventListener("keyup", function(event) {
  // Number 13 is the "Enter" key on the keyboard
  if (event.keyCode === 13) {
        // Cancel the default action, if needed
        event.preventDefault();
        // Trigger the button element with a click
        var val = input.value;
        input.value = "";

        addDataToWordOccurenceChart(val,window.myLine);
    }

  });