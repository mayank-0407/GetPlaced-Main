function validate(){
    user_email=document.getElementById("user_email").value
    if(user_email==""){
        document.getElementById("message_red").innerHTML="Username cannot be empty"
        delay('#message_red')
        return false
    }
    password=document.getElementById("password").value
    if(password==""){
        document.getElementById("message_red").innerHTML="Password cannot be empty"
        delay('#message_red')
        return false
    }
    return true
}

$("#login").submit(function (e) {
    e.preventDefault();
    if(validate()==false) {
        return false;
    }
    document.getElementById("login_button").disabled = true;
    var serializedData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: "",
        data: serializedData,
        success: function (response) {
            $("#login").trigger('reset');
            document.getElementById("message_green").innerHTML="Login is Successful"
            delay('#message_green')
            location.reload();
        },
        error: function (response) {
            document.getElementById("password").value=""
            document.getElementById("message_red").innerHTML=response["responseJSON"]["error"]
            delay('#message_red')
            document.getElementById("login_button").disabled = false;
        }
    })
})
function delay(ID){
    $(ID).fadeIn();
    $(ID).delay(2000).fadeOut(1500);
}