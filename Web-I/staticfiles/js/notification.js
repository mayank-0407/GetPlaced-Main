// Get the modal
var modal = document.getElementById("notificationform");

// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];




// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

function display(myid){
    document.getElementById("user_id").value=myid
    document.getElementById("enter_user_id").innerHTML="Send Notification to user " + myid
    modal.style.display = "block";
}

function close_modal(){
    modal.style.display = "none";
    document.getElementById("user_id").value=""
    document.getElementById("enter_user_id").innerHTML=myid
    return false
}

function to_all(myid){
    document.getElementById("user_id").value=myid
    if(myid==-1){
        message="Send Notification to Staffs"
    }
    if(myid==-2){
        message="Send Notification to all Companies"
    }
    if(myid==-3){
        message="Send Notification to all Students"
    }
    document.getElementById("enter_user_id").innerHTML=message
    modal.style.display = "block";
}
