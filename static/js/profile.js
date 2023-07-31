function validate_number() {
    var number = document.getElementById("contact_number").value;
    if (number.length != 10) {
        alert("Invalid Phone Number entered")
        return false;
    }
    document.getElementById("mybutton").disabled = true;
    return true;
}

function disable_button() {
    document.getElementById("mybutton").disabled = true;
    return true;
}

function show_hide(myval){
  if(myval==1){
    $("#prev_round").hide()
    $("#prev_round_for_result").val(0)
    $("#last_date").show()
    $("#last_date_to_apply").val("")
    $("#last_date_to_apply").prop('required', true);
  }
  else{
    $("#prev_round").show()
    $("#prev_round_for_result").val(parseInt(myval)-1)
    $("#last_date").hide()
    $("#last_date_to_apply").prop('required', false);
  }
}

function check_last_round(event) {
    var selectElement = event.target;
    var value = parseInt(selectElement.value);
    if(value==2){
        $("#last_date").hide()
        $("#last_date_to_apply").prop('required', false);
    }
    else{
        $("#last_date").show()
        $("#last_date_to_apply").val("")
        $("#last_date_to_apply").prop('required', true);
    }
}