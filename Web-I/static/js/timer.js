$(document).ready(function() {
    $('#message').fadeIn('slow', function() {
        $('#message').delay(4000).fadeOut(4000);
    });
    document.getElementById("mytimercountdown").innerHTML=new Date();
});