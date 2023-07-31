/* Custom filtering function which will search data in column four between two values */
$.fn.dataTable.ext.search.push(
    function( settings, data, dataIndex ) {
        var session_filter=document.getElementById("session_filter").value
        var session = data[1]   //2nd column
        if(session_filter=="All")   return true;
        if (session_filter==session)    return true;
        return false;
    }
);

// var table = $('#myTable').DataTable();
