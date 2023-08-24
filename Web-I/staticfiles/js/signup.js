function validate() {
    email = document.getElementById('email').value
    var n = email.search('@iiita.ac.in');
    if (n == -1) {
        document.getElementById("myerror").innerHTML = "Email entered is not associated with IIITA";
        $('#myerror').fadeIn();
        $('#myerror').delay(4000).fadeOut(4000);
        return false;
    }
    if (email.length >= 25)
        return false;
    password1 = document.getElementById('password3').value
    password2 = document.getElementById('password4').value
    if (password1 != password2) {
        document.getElementById("myerror").innerHTML = "Both the passwords are diferent";
        $('#myerror').fadeIn();
        $('#myerror').delay(4000).fadeOut(4000);
        return false;
    } else {
        var val = passwordchecker(password1)
        if (!val) {
            document.getElementById("myerror").innerHTML = "Password must have atleast 8 characters with digits, letters and special characters";
            $('#myerror').fadeIn();
            $('#myerror').delay(4000).fadeOut(4000);
            return false
        }
        document.getElementById("button1").disabled = true;
        return true
    }
}


function validate_passwords() {
    password1 = document.getElementById('password1').value
    password2 = document.getElementById('password2').value
    if (password1 != password2) {
        document.getElementById("myerror").innerHTML = "Both the passwords are diferent";
        $('#myerror').fadeIn();
        $('#myerror').delay(4000).fadeOut(4000);
        return false;
    } else {
        var val = passwordchecker(password1)
        if (!val) {
            document.getElementById("myerror").innerHTML = "Password must have atleast 8 characters with digits, letters and special characters";
            $('#myerror').fadeIn();
            $('#myerror').delay(4000).fadeOut(4000);
            return false
        }
        document.getElementById("button2").disabled = true;
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