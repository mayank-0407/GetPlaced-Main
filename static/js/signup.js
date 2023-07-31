function validate() {
    email = document.getElementById('email').value
    if(email==""){
        document.getElementById("myerror").innerHTML="Email must not be empty."
        fader('#myerror')
        return false;
    }
    if(validateEmail(email)==false){
        document.getElementById("myerror").innerHTML="Email is not in proper format."
        fader('#myerror')
        return false;
    }
    document.getElementById('email').value=email.toLowerCase()
    email = document.getElementById('email').value
    username = document.getElementById('username').value
    if(username==""){
        document.getElementById("myerror").innerHTML="Username must not be empty."
        fader('#myerror')
        return false;
    }
    fname = document.getElementById('fname').value
    if(fname==""){
        document.getElementById("myerror").innerHTML="First Name must not be empty."
        fader('#myerror')
        return false;
    }
    lname = document.getElementById('lname').value
    if(lname==""){
        document.getElementById("myerror").innerHTML="Last Name must not be empty."
        fader('#myerror')
        return false;
    }
    var n = email.search('@gmail.com');
    if (n == -1) {
        document.getElementById("myerror").innerHTML = "Email entered is not associated";
        fader('#myerror')
        return false;
    }
    if (email.length >= 35)
        return false;
    password1 = document.getElementById('password3').value
    password2 = document.getElementById('password4').value
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
        document.getElementById("button1").disabled = true;
        return true
    }
}

function validate_passwords() {
    email = document.getElementById('email1').value
    if(email==""){
        document.getElementById("myerror").innerHTML="Email must not be empty."
        fader('#myerror')
        return false;
    }
    if(validateEmail(email)==false){
        document.getElementById("myerror").innerHTML="Email is not in proper format."
        fader('#myerror')
        return false;
    }
    document.getElementById('email1').value=email.toLowerCase()
    username = document.getElementById('username1').value
    if(username==""){
        document.getElementById("myerror").innerHTML="Username must not be empty."
        fader('#myerror')
        return false;
    }
    fname = document.getElementById('fname1').value
    if(fname==""){
        document.getElementById("myerror").innerHTML="Company Name must not be empty."
        fader('#myerror')
        return false;
    }
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
        document.getElementById("button2").disabled = true;
        return true
    }
}

function fader(ID){
    $(ID).fadeIn()
    $(ID).delay(4000).fadeOut(4000)
}

function passwordchecker(str) {
    if ((str.match(/[a-z]/g) || str.match(/[A-Z]/g)) && str.match(
            /[0-9]/g) && str.match(
            /[^a-zA-Z\d]/g) && str.length >= 8)
        return true;
    return false;
}


function disablemybutton(MY_ID) {
    document.getElementById(MY_ID).disabled = true;
    return true;
}

function checktimersettings(){
    current_date=new Date()
    prev=document.getElementById("mytimercountdown").innerHTML
    prev_date=new Date(prev)
    if((current_date-prev_date)>=90000){
        document.getElementById("mytimercountdown").innerHTML=new Date();
        return true;
    }
    var seconds=(90000 - (current_date-prev_date))/1000;
    var error = "You can resend OTP after : " + seconds + " seconds"
    document.getElementById("myerror").innerHTML = error;
    $('#myerror').fadeIn();
    $('#myerror').delay(2000).fadeOut(2000);
    return false;
}

function validateEmail (emailAdress)
{
  return true;
}
// function validateEmail (emailAdress)
// {
//   let regexEmail = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
//   if (emailAdress.match(regexEmail)) {
//     return true; 
//   } else {
//     return false; 
//   }
// }

$("#login").submit(function (e) {
    e.preventDefault();
    if(validate()==false) {
        alert("Please enter")
        return false;
    }
    document.getElementById("button1").disabled = true;
    var serializedData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: "",
        data: serializedData,
        success: function (response) {
            $("#login").trigger('reset');
            document.getElementById("myerror").innerHTML="Signup Successful"
            fader('#myerror')
            document.getElementById("phase_1").style.display="none"
            document.getElementById("phase_2").style.display="block"
            // location.reload();
        },
        error: function (response) {
            document.getElementById("password3").value=""
            document.getElementById("password4").value=""
            document.getElementById("myerror").innerHTML=response["responseJSON"]["error"]
            fader('#myerror')
            document.getElementById("button1").disabled = false;
        }
    })
})

$("#register").submit(function (e) {
    e.preventDefault();
    if(validate_passwords()==false) {
        return false;
    }
    document.getElementById("button2").disabled = true;
    var serializedData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: "",
        data: serializedData,
        success: function (response) {
            $("#register").trigger('reset');
            document.getElementById("myerror").innerHTML="Signup Successful"
            fader('#myerror')
            document.getElementById("phase_1").style.display="none"
            document.getElementById("phase_2").style.display="block"
            // location.reload();
        },
        error: function (response) {
            document.getElementById("password3").value=""
            document.getElementById("password4").value=""
            document.getElementById("myerror").innerHTML=response["responseJSON"]["error"]
            fader('#myerror')
            document.getElementById("button2").disabled = false;
        }
    })
})