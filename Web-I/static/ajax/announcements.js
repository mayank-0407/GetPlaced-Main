$.fn.dataTable.ext.search.push(
    function( settings, data, dataIndex ) {
        var session_filter=document.getElementById("session_filter").value
        var session = data[3]   //4th column
        if(session_filter=="All")   return true;
        if (session_filter==session)    return true;
        return false;
    }
);