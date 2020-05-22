const url = 'process.php';
const form = document.querySelectorAll('form')[1];

// event-listener for submit event(s)
form.addEventListener('submit', event => {
    event.preventDefault(); // prevents default action

    // reset result(s)
    document.getElementById("spc-string").innerHTML = " ";
    document.getElementById("sys-string").innerHTML = " ";
    document.getElementById("final-result").innerHTML = " ";

    // set verification status
    var verifStatus = document.getElementById("verification-status");
    verifStatus.innerHTML = "Verifying...";

    // retrieve file from form data
    const files = document.querySelector('[type=file]').files;
    const formData = new FormData();

    console.log("File: " + files[0]);

    // add file to formData
    let file = files[0];
    formData.append('fileToUpload', file);

    // add selection to formData
    var selection = document.getElementById("solutions");
    formData.append('solutionSelection', selection.options[selection.selectedIndex].value);

    // post the data to the URL (php file)
    fetch(url, {
        method: 'POST',
        body: formData,
    }).then(response => {
        // return JSON response
        return response.json();
    }).then(data => {
        // work with JSON data
        console.log(data);

        // get JSON data
        var status = data.message;
        var spcString = data.spcString;
        var sysString = data.sysString;

        var uploadStatus = document.getElementById("upload-status");

        if(status == "NOT UPLOADED") {
            uploadStatus.innerHTML = "<b>Error</b>: File not uploaded. Please try again.";
        }
        else {
            // update table accordingly
            uploadStatus.innerHTML = " "; // no upload error

            // html element(s)
            var spcStringResult = document.getElementById("spc-string");
            var sysStringResult = document.getElementById("sys-string");
            var finalResult = document.getElementById("final-result");

            // set string(s)
            spcStringResult.innerHTML = spcString;
            sysStringResult.innerHTML = sysString;

            // final result string
            if(status == "PASS") {
                // model matches solution
                finalResult.innerHTML = '<span style="color: #008000">' + status + '</span>';
            }
            else {
                // model does not match solution
                finalResult.innerHTML = '<span style="color: #FF0000">' + status + '</span>';
            }
        }

        verifStatus.innerHTML = " ";
    }).catch(err => {
        // catch errors
    });
});
