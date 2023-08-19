function open_description(blog_id){
    if(blog_id=='contact_us'){
        document.getElementById("blog_description").innerHTML="Contact Numbers: +91 94655-*****<br><br>Email Address: mayankdatabase04@gmail.com"
    }
    else{
        document.getElementById("blog_description").innerHTML=document.getElementById(blog_id).innerHTML
    }
    document.getElementById('blog').style.display='block'
}


$(document).ready(function() {
    $("#disappear").fadeIn('slow', function() {
        $("#disappear").delay(500).fadeOut(2500);
    });
});
