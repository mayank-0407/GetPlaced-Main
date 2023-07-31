function send_message(){
    chat_message=document.getElementById("chat_message").value;
    if(chat_message==""){
        document.getElementById("chat_message").placeholder="Can't send an empty message."
        return false;
    }
    document.getElementById("chat_message").value=""
    $('#all_chatss').append(add_message_mine(chat_message))
    serializedData='chat_message='+ chat_message
    chat_re_id=document.getElementById("chat_re_id").innerHTML
    $.ajax({
        type: 'GET',
        url: "../send/"+chat_re_id,
        data: serializedData,
        success: function (response) {
            
        },
        error: function (response) {
            alert(response["responseJSON"]["error"]);
            location.reload()
        }
    })

    scroll_down()

}

total_new_messages=0

function add_message_mine(message){
    username=document.getElementById("user_name").innerHTML
    time1=new Date()
    time=get_month(time1.getMonth())+" "+time1.getDate()+", "+time1.getFullYear()+", "+formatAMPM(time1)
    image=document.getElementById("pr_image").innerHTML
    if(image==0){
        url="/static/img/us_ma.png"
        message=`
            <li class="out">
                <div class="chat-img">
                    <img src="`+ url +`" alt="{% static 'img/us_ma.png' %}">
                </div>
                <div class="chat-body">
                    <div class="chat-message">
                        <h5>`+username+` - `+time+`</h5>
                        <p>`+message+`</p>
                    </div>
                </div>
            </li>
        `
    }
    else{
        base_url="/media/"
        next_url=image
        message=`
                    <li class="out">
        				<div class="chat-img">
        					<img src="`+ base_url+next_url +`" alt="{% static 'img/us_ma.png' %}">
        				</div>
    					<div class="chat-body">
    						<div class="chat-message">
        						<h5>`+username+` - `+time+`</h5>
        						<p>`+message+`</p>
        					</div>
        				</div>
        			</li>
        `
    }
    return message
}

function add_message_staff(message, username, time){
    url="/static/img/staff.png"
    message=`
                    <li class="in new_chat">
        				<div class="chat-img">
        					<img src="`+url+`">
        				</div>
    					<div class="chat-body">
    						<div class="chat-message">
        						<h5>`+username+` - `+time+`</h5>
        						<p>`+message+`</p>
        					</div>
        				</div>
        			</li>
        `
    return message
}

    
function get_month(id){
    if(id==0)   return "Jan"
    if(id==1)   return "Feb"
    if(id==2)   return "Mar"
    if(id==3)   return "Apr"
    if(id==4)   return "May"
    if(id==5)   return "June"
    if(id==6)   return "July"
    if(id==7)   return "Aug"
    if(id==8)   return "Sept"
    if(id==9)   return "Oct"
    if(id==10)   return "Nov"
    if(id==11)   return "Dec"
}

function formatAMPM(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes + ' ' + ampm;
    return strTime;
  }



function get_new_messages(){
    if(chat_receiving==0)   return false;
    chat_re_id=document.getElementById("chat_re_id").innerHTML
    $.ajax({
        type: 'GET',
        url: "../receive/"+chat_re_id,
        success: function (response) {
            data=response.data
            data=JSON.parse(data)
            if(data!=0){
                n=Object.keys(data).length
                total_new_messages+=n
                document.getElementById("total_new_messages").innerHTML=total_new_messages+" New Messages"
                for(var i=0;i<n;i++){
                    $("#all_chatss").append(add_message_staff(data[i].fields.message, data[i].fields.username, data[i].fields.mess_time_str))
                }
            }
        },
        error: function (response) {
            alert(response["responseJSON"]["error"]);
            location.reload()
        }
    })
}

function scroll_down(){
    var elem = document.getElementById('scroller');
    elem.scrollTop = elem.scrollHeight;
}

scroll_down()
chat_receiving=document.getElementById('chat_receiver').innerHTML
if(chat_receiving!=0){
    window.setInterval(function() {
            get_new_messages();
    }, 1000);
}

function end_chat(){
    chat_re_id=document.getElementById("chat_re_id").innerHTML
    $.ajax({
        type: 'GET',
        url: "../end/"+chat_re_id,
        success: function (response) {
            alert("Chat has been ended. Now, no new messages can be sent.")
            location.reload();
        },
        error: function (response) {
            alert(response["responseJSON"]["error"]);
            location.reload()
        }
    })
}