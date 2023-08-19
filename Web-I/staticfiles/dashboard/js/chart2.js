
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);
google.charts.setOnLoadCallback(drawChart1);

function drawChart() {
    res=parseInt(document.getElementById("my_selections").innerHTML)
    non_res=parseInt(document.getElementById("my_registrations").innerHTML) - res
    var data = google.visualization.arrayToDataTable([
    ['Type', 'Count'],
    ['Selections', res],
    ['Rejections', non_res],
]);
    screen_width=screen.width
    if(screen_width<=700){
        screen_width-=50
    }
    else{
        screen_width/=3
    }
  var options = {'title':'My Selections', 'width':screen_width, 'height':400};

  var chart = new google.visualization.PieChart(document.getElementById('selections'));
  chart.draw(data, options);
}

function drawChart1() {
    selc=parseInt(document.getElementById("internships_accepted").innerHTML)
    non_selc=parseInt(document.getElementById("internships_reverted").innerHTML)
    var data1 = google.visualization.arrayToDataTable([
    ['Type', 'Number of Students'],
    ['Accepted by Me', selc],
    ['Reverted by Me', non_selc],
]);
    screen_width=screen.width
    if(screen_width<=700){
        screen_width-=50
    }
    else{
        screen_width/=3
    }
  var options1 = {'title':'My Internships', 'width':screen_width, 'height':400};

  var chart1 = new google.visualization.PieChart(document.getElementById('accepted'));
  chart1.draw(data1, options1);
}