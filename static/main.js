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

// Grey out "Spaces per level" for tabs and "Line length" when not wrapping
var updateDependentFields = function() {
    $('#numberof').prop('disabled', $('input[name="indent_type"]:checked').val() == "tabs");
    $('#wrap_columns').prop('disabled', $('input[name="wrap"]:checked').val() != "on");
}
$('input[name="indent_type"], input[name="wrap"]').on('change', updateDependentFields);
updateDependentFields();

// Line length the server accepts: whole number, 20 to 500 (80 if left blank)
var wrapColumns = function() {
    if ($('input[name="wrap"]:checked').val() != "on") {
        return "0";
    }
    var columns = parseInt($('#wrap_columns').val(), 10);
    if (isNaN(columns)) {
        columns = 80;
    }
    columns = Math.min(500, Math.max(20, columns));
    $('#wrap_columns').val(columns);
    return String(columns);
}

// Every formatting option, as the form fields the server expects
var collectOptions = function() {
    var options = {
        spaces_or_tabs: $('input[name="indent_type"]:checked').val(),
        number_of: $('#numberof').val(),
        wrap_columns: wrapColumns()
    };
    $('input.option').each(function() {
        options[this.id] = this.checked ? "1" : "0";
    });
    return options;
}

$("#formatbutton").click(function() {
     var data = collectOptions();
     data.latex_data = $('#latexcode').val();
     $.post("/format/", data, renderResponse);
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

    $.each(collectOptions(), function(name, value) {
        oData.append(name, value);
    });

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
