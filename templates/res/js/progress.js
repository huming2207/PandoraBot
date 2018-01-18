function init_progress() {
    setInterval(update_progress, 500);
}

function update_progress() {
    var httpRequest = new XMLHttpRequest();

    httpRequest.onreadystatechange = function (ev) {

        if(this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            if(this.responseText.length > 0) {

                var response;
                var flashrom_progress;

                try {
                    response = JSON.parse(this.responseText);
                    flashrom_progress = response.progress();
                } catch(error) {
                    console.log(error);
                }

                // If the progress does not exist, set a implicit indicator value.
                if(flashrom_progress !== undefined && flashrom_progress !== null) {
                    document.getElementById("progress_indicator").innerText = flashrom_progress.toString();
                } else {
                    document.getElementById("progress_indicator").innerText = "Working...";
                }

            }
        }

    };

    // ...Fire in the hole!
    httpRequest.open("GET", endPoint + "?" + setting, true);
    httpRequest.send();
}