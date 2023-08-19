$("#new_session").submit(function (e) {
    e.preventDefault();
    if(document.getElementById("session_name").value=="") {
        alert("Session name must not be empty.")
        return false;
    }
    document.getElementById("button").disabled = true;
    var serializedData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: "",
        data: serializedData,
        success: function (response) {
            $("#new_session").trigger('reset');
            alert("New Session has been created.")
            location.reload();
        },
        error: function (response) {
            alert(response["responseJSON"]["error"])
            document.getElementById("button").disabled = false;
        }
    })
})