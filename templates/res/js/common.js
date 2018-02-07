function init_progress() {
    setInterval(update_progress, 500);
}

function update_progress() {

    axios.get("/flashrom_progress")
        .then(function (response) {
            document.getElementById("progress_indicator").innerText = response.data.progress.toString();
        })
        .catch(function (error) {
            console.log("Oops, request failed!");
            console.log(error.response.data);
            console.log(error.response.status);
            console.log(error.response.headers);
        });
}

function after_operation(isRead) {

    if(isRead === true) {
        // Download the file
        var iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = '/flashrom.bin';
        document.body.appendChild(iframe);
    }

    // Return to home page
    alert('Done!');
    window.location.replace('/');
}