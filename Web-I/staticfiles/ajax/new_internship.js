function validate_announcement_internship() {
    if (document.getElementById("internship_name").value.length <= 0) {
        alert("Internship Name can not be empty.")
        return false
    }
    if (document.getElementById("duration").value.length <= 0) {
        alert("Internship Duration can not be empty.")
        return false
    }
    if (document.getElementById("internship_position").value.length <= 0) {
        alert("Internship Position can not be empty.")
        return false
    }
    cgpa = document.getElementById("minimum_cgpa").value
    if (validate_cgpa(cgpa) == false) {
        alert("CGPA is not in proper format.")
        return false
    }
    stipend = document.getElementById("stipend").value
    if (validate_float(stipend) == false) {
        alert("Stipend is not in proper format.")
        return false
    }
    return true
}

$("#new_internship").submit(function (e) {
    e.preventDefault();
    if(validate_announcement_internship()==false) {
        return false;
    }
    document.getElementById("new_internship_button").disabled = true;
    var serializedData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: "",
        data: serializedData,
        success: function (response) {
            $("#new_internship").trigger('reset');
            alert("New internship has been created. Now, first round must be announced in the new round section.")
            document.getElementById("new_internship_button").disabled = false;
        },
        error: function (response) {
            alert(response["responseJSON"]["error"])
            document.getElementById("new_internship_button").disabled = false;
        }
    })
})