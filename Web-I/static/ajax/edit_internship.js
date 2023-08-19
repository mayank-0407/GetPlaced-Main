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

$("#edit_internship").submit(function (e) {
    e.preventDefault();
    if(validate_announcement_internship()==false) {
        return false;
    }
    var serializedData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: "",
        data: serializedData,
        success: function (response) {
            $("#edit_internship").trigger('reset');
            alert('Internship Details Updated')
            location.reload()
        },
        error: function (response) {
            alert(response["responseJSON"]["error"])
        }
    })
})