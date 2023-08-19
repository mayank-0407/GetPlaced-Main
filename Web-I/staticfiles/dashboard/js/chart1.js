
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);
google.charts.setOnLoadCallback(drawChart1);

function drawChart() {
    res=parseInt(document.getElementById("internships_with_result").innerHTML)
    non_res=parseInt(document.getElementById("internships_without_result").innerHTML)
    var data = google.visualization.arrayToDataTable([
    ['Type', 'Count'],
    ['Result Announced', res],
    ['Result not Announced', non_res],
]);
    screen_width=screen.width
    if(screen_width<=700){
        screen_width-=50
    }
    else{
        screen_width/=3
    }
  var options = {'title':'My Internships', 'width':screen_width, 'height':400};

  var chart = new google.visualization.PieChart(document.getElementById('internship_stats_chart'));
  chart.draw(data, options);
}

function drawChart1() {
    selc=parseInt(document.getElementById("selected_students").innerHTML)
    non_selc=parseInt(document.getElementById("unselected_students").innerHTML)
    var data1 = google.visualization.arrayToDataTable([
    ['Type', 'Number of Students'],
    ['Selected Students', selc],
    ['Unselected Students', non_selc],
]);
    screen_width=screen.width
    if(screen_width<=700){
        screen_width-=50
    }
    else{
        screen_width/=3
    }
  var options1 = {'title':'Registrations', 'width':screen_width, 'height':400};

  var chart1 = new google.visualization.PieChart(document.getElementById('registrations_list_chart'));
  chart1.draw(data1, options1);
}