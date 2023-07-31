function open_description(blog_id){
    if(blog_id=='contact_us'){
        document.getElementById("blog_description").innerHTML="Contact Numbers: +91 6284648753 , +91 85868 87785 , +91 80049 70046 , +91 78372 55890<br><br>Email Address: cleanframeiiit@gmail.com"
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
