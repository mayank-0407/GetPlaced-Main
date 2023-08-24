$(window).scroll(function() {
  var scroll = $(window).scrollTop(),
    dh = $(document).height(),
    wh = $(window).height();
  scrollPercent = (scroll / (dh - wh)) * 100;
  $('#progressbar').css('height', scrollPercent + '%');
})
$(window).scroll(function() {
  var scroll = $(window).scrollTop(),
    dh = $(document).height();
    wh = $(window).height();
    gh = Math.max(dh,wh);
  $('.sidebar').css('height', gh + 'px');
})

$(document).ready(function() {
  window.setTimeout(doc_height, 10);
});
function doc_height() {
  alpha=Math.max($(document).height(), $(window).height())
  $('.sidebar').css('height',Math.max(screen.height,alpha))
};

  var table=$("#myTable").DataTable({
    "paging": true,
    "ordering": true,
    "bLengthChange": true,
    "searching": true,
  });

  
  function draw(){  
    table.draw();
  }

  function myFunction() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("myTable");
    tr = table.getElementsByTagName("tr");

    // Loop through all table rows, and hide those who don't match the search query
    for (i = 1; i < tr.length; i++) {
      td = tr[i].getElementsByTagName("td")[0];
      if (td) {
        txtValue = td.textContent || td.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
        } else {
          tr[i].style.display = "none";
        }
      }
    }
  }
