/* Custom filtering function which will search data in column four between two values */
var current_session=document.getElementById("current_session").innerHTML
$.fn.dataTable.ext.search.push(
    function( settings, data, dataIndex ) {
        var session_filter=document.getElementById("session_filter").value
        // var session = data[1]   2nd column
        if(session_filter=="All")   return true;
        if(session_filter=="Current Session"){
            if(data[0]==current_session)    return true;
            else    return false;
        }
        if(session_filter==data[5])     return true;
        return false;

    }
);

// var table = $('#myTable').DataTable();
