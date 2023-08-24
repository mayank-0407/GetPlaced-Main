function close_modal() {
    var modal = document.getElementById("deleteModal");
    modal.style.display = "none";
    document.getElementById("myusername").value = "";
    text_changed("--1--")
}

// Get the modal
var modal = document.getElementById("deleteModal");

// Get the button that opens the modal
var btn = document.getElementById("delete_account");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal 
btn.onclick = function() {
    modal.style.display = "block";
    var activatebtn = document.getElementById("deel")
    activatebtn.style.backgroundColor = "#FFECEC";
    activatebtn.style.pointerEvents = "none";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
    document.getElementById("myusername").value = "";
    text_changed("--1--")
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
        document.getElementById("myusername").value = "";
        text_changed("--1--")
    }
}

function text_changed(myval) {
    var orgvalbtn = document.getElementById("usersname")
    if (myval == orgvalbtn.innerHTML) {
        var activatebtn = document.getElementById("deel")
        activatebtn.style.backgroundColor = "red";
        activatebtn.style.pointerEvents = "auto";
    } else {
        var activatebtn = document.getElementById("deel")
        activatebtn.style.backgroundColor = "#FFECEC";
        activatebtn.style.pointerEvents = "none";
    }
}

function call_slider(){
        var serializedData = $(this).serialize();
        myid=document.getElementById("myid").innerHTML
        $.ajax({
            type: 'GET',
            url: "../company/change/mode/"+myid,
            data: serializedData,
            success: function (response) {
                alert('Mode Changed Successfully')
                location.reload()
            },
            error: function (response) {
                alert(response["responseJSON"]["error"])
            }
        })
}