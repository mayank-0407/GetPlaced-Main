// Get the modal
var modal = document.getElementById("supportform");

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

function respond(myid){
    document.getElementById("support_id").value=myid
    document.getElementById("enter_user_id").innerHTML="Reply to message id " + myid
    modal.style.display = "block";
}

function close_modal(){
    modal.style.display = "none";
    document.getElementById("support_id").value=""
    document.getElementById("enter_user_id").innerHTML=myid
    return false;
}

function new_thread(){
    document.getElementById("support_id").value="0"
    document.getElementById("enter_user_id").innerHTML="New Thread"
    modal.style.display = "block";
}
