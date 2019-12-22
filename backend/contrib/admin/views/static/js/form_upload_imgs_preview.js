// File extension extract regex
const getFileExtension = /(?:\.([^.]+))?$/;

/* Helper functions */
function renameFile(inFile, newName) {
    //const token = document.getElementsByName("csrf_token").value;
    const token = getCookie('csrf_token')
    var file = inFile.files[0];
    var results = new FormData();
    results.append('file', file, newName);
    results.append('csrf_token', token)
    return results;
}

function sendFile(url, formData) {
    var request = new XMLHttpRequest();
    request.open("POST", url);
    console.log("Endpoint: " + url);
    request.send(formData);
}

function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

var handleFileSelect = function(e) {

    if(!e.target.files || !window.FileReader) return;

    var selDiv = document.querySelector("#file-preview-list");
    // Clear the previously added elements
    selDiv.innerHTML = "";

    var files = e.target.files;
    var filesArr = Array.prototype.slice.call(files);
    filesArr.forEach(function(f) {
        if(!f.type.match("image.*")) {
            return;
        }

        var reader = new FileReader();
        reader.onload = function (e) {
            // Creating a DIV element
            var divSection = document.createElement('div');
            divSection.setAttribute("class", "image-name-container");

            const imgHtml = "<img class=\"img-preview\" src=\"" + e.target.result + "\">";
            const nameHtml = "<input class=\"img-name\" type=text placeholder=\"" + f.name + "\"  >" + "<br clear=\"left\"/>";

            divSection.innerHTML = imgHtml + nameHtml;
            selDiv.appendChild(divSection);
        }
        reader.readAsDataURL(f);
    });
}

var handleSubmit = function(e) {
    e.preventDefault();
    const imgNameDiv = document.querySelector('#file-preview-list');
    for (const imgDiv of imgNameDiv.querySelectorAll('.image-name-container')) {
        const placeholder = imgDiv.querySelector('input').placeholder;
        const userName = imgDiv.querySelector('input').value;
        // If the user does not provided an extension, keep the original extension
        const name = userName ? ((!getFileExtension.exec(userName)[1]) ? userName + '.' + getFileExtension.exec(placeholder)[1] : userName) : placeholder;
        sendFile(this.action, renameFile(document.querySelector('input[type=file]'), name));
    }
}

document.addEventListener("DOMContentLoaded", function(e) {
    document.querySelector('input[type=file]').addEventListener('change', handleFileSelect, false);
    document.getElementById('upload-files').addEventListener('submit', handleSubmit, false);
});
