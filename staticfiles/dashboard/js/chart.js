
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);
google.charts.setOnLoadCallback(drawChart1);

function drawChart() {
    student=parseInt(document.getElementById("student_count").innerHTML)
    company=parseInt(document.getElementById("company_count").innerHTML)
    staff=parseInt(document.getElementById("staff_count").innerHTML)
    admin=parseInt(document.getElementById("admin_count").innerHTML)
    var data = google.visualization.arrayToDataTable([
    ['User Type', 'Number of Users'],
    ['Students', student],
    ['Staffs', staff],
    ['Companies', company],
    ['Admins', admin],
]);
    screen_width=screen.width
    if(screen_width<=700){
        screen_width-=50
    }
    else{
        screen_width/=3
    }
  var options = {'title':'Users', 'width':screen_width, 'height':400};

  var chart = new google.visualization.PieChart(document.getElementById('userschart'));
  chart.draw(data, options);
}

function drawChart1() {
    student=parseInt(document.getElementById("student_count").innerHTML)
    students_with_internship=parseInt(document.getElementById("students_with_internship").innerHTML)
    students_without_internship=student-students_with_internship
    var data1 = google.visualization.arrayToDataTable([
    ['Type', 'Number of Students'],
    ['Non Intern Students', students_without_internship],
    ['Interned Students', students_with_internship],
]);
    screen_width=screen.width
    if(screen_width<=700){
        screen_width-=50
    }
    else{
        screen_width/=3
    }
  var options1 = {'title':'Interns', 'width':screen_width, 'height':400};

  var chart1 = new google.visualization.PieChart(document.getElementById('internshipschart'));
  chart1.draw(data1, options1);
}