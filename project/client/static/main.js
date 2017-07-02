// custom javascript
$(document).ready(function() {
    console.log('Sanity Check!');
});

var renderResponse = function(data) {
    if ($("#formatedlatex")[0] != undefined) {
        $("#formatedlatex").val(data);
    } else {
        var wrapper = $("#result");
        $(wrapper).append('<div><textarea readonly rows = "10" cols="50" type="text" id="formatedlatex" name="mytext[]"/></div>');
        $("#formatedlatex").val(data);
        $(wrapper).append("<button id='copytext' data-clipboard-target='#formatedlatex' class='btn btn-primary'>Copy to clipboard</button>");
    }
}

$("#formatbutton").click(function() {

    var latex_data = $('#latexcode').val();
    $.post("/format/", {
        latex_data: latex_data
    }, renderResponse);
});

$("#result").click(function() {
    new Clipboard('.btn');
});

$("#file").on("change", function(e){

    var filename = $("#file").val();
    if (filename.split('.').pop() != 'tex'){
        alert("only latex files!");
        $("#file").val("");
    }

});


var form = document.forms.namedItem("fileinfo");
form.addEventListener('submit', function(ev) {

    var oOutput = document.querySelector("div"),
        oData = new FormData(form);

    oData.append("CustomField", "This is some extra data");

    spacesOrTab = $('input[name="options"]:checked').val();

    numberOf = $('#numberof').val();

    oData.append("spaces_or_tabs", spacesOrTab)
    oData.append("number_of", numberOf)

    var oReq = new XMLHttpRequest();
    oReq.open("POST", "/formatfile/", true);

    oReq.onreadystatechange = function() {
        if (oReq.readyState == 4 && oReq.status == 200) {
            renderResponse(oReq.responseText);
        }
    }

    oReq.send(oData);
    ev.preventDefault();
}, false);
