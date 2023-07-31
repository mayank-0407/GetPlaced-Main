$("#login").submit(function (e) {
    e.preventDefault();
    if(validate_email()==false) return false;
    document.getElementById("idnois3").disabled = true;
    var serializedData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: "",
        data: serializedData,
        success: function (response) {
            email=document.getElementById("email").value
            $("#login").trigger('reset');
            document.getElementById("myerror").innerHTML="Notification has been sent to your email"
            fader('#myerror')
            document.getElementById("phase_1").style.display="none"
            document.getElementById("messenger").innerHTML="A Password change notification has been sent to "+ email + ", click it to change your password."
            document.getElementById("phase_2").style.display="block"
            // location.reload();
        },
        error: function (response) {
            document.getElementById("myerror").innerHTML=response["responseJSON"]["error"]
            fader('#myerror')
            document.getElementById("idnois3").disabled = false;
        }
    })
})

function validate_email(){
    email=document.getElementById("email").value
    if(email==""){
        document.getElementById("myerror").innerHTML="Email must not be empty."
        fader('#myerror')
        return false
    }
    if(validateEmail(email)==false){
        document.getElementById("myerror").innerHTML="Email is not in proper format."
        fader('#myerror')
        return false
    }
    document.getElementById('email').value=email.toLowerCase()
    return true
}

function validateEmail (emailAdress)
{
  let regexEmail = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
  if (emailAdress.match(regexEmail)) {
    return true; 
  } else {
    return false; 
  }
}

function fader(ID){
    $(ID).fadeIn()
    $(ID).delay(4000).fadeOut(4000)
}


$("#login2").submit(function (e) {
    e.preventDefault();
    if(validate_passwords()==false) return false
    document.getElementById("button2").disabled = true;
    var serializedData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: "",
        data: serializedData,
        success: function (response) {
            email=document.getElementById("email").value
            $("#login2").trigger('reset');
            document.getElementById("code_phase_1").style.display="none"
            document.getElementById("messenger").innerHTML="Password has been changed for your account linked with "+email
            document.getElementById("code_phase_2").style.display="block"
            // location.reload();
        },
        error: function (response) {
            document.getElementById("myerror").innerHTML=response["responseJSON"]["error"]
            fader('#myerror')
            document.getElementById("button2").disabled = false;
        }
    })
})

function validate_passwords() {
    password1 = document.getElementById('password1').value
    password2 = document.getElementById('password2').value
    if(password1=="" || password2==""){
        document.getElementById("myerror").innerHTML="Password must not be empty."
        fader('#myerror')
        return false;
    }
    if (password1 != password2) {
        document.getElementById("myerror").innerHTML = "Both the passwords are diferent";
        fader('#myerror')
        return false;
    } else {
        var val = passwordchecker(password1)
        if (!val) {
            document.getElementById("myerror").innerHTML = "Password must have atleast 8 characters with digits, letters and special characters";
            fader('#myerror')
            return false
        }
        return true
    }
}

function passwordchecker(str) {
    if ((str.match(/[a-z]/g) || str.match(/[A-Z]/g)) && str.match(
            /[0-9]/g) && str.match(
            /[^a-zA-Z\d]/g) && str.length >= 8)
        return true;
    return false;
}