/*document.addEventListener('DOMContentLoaded', function() {

});*/

var socket;
jQuery(document).ready(function(){
    // connect web location
    socket = io.connect('http://127.0.0.1:5000/addCourse')

    // add events
    $('#submit_all_info_button').click(function() {
        // socket.emit('newmsg', $('.ddl_information').html());
        $('.ddl_information').each(function() {
            socket.emit('newddl', $(this).html());
        });
        $('.ddl_date').each(function() {
            socket.emit('newdate', $(this).html());
        });
    });

    $('#ddl_button').click(function(){
        // socket.emit('newddl', 'zoo');
    });

});

// add new ddl to ddl_table
function addDDL() {
    // get messages
    var information = document.getElementById('newddl');
    var date = document.getElementById("ddl");

    // load new row
    var content = 
        '<tr>' +
        '<td class="ddl_information">' + information.value + '</td>' +
        '<td class="ddl_date">' + date.value + '</td>' +
        '<td><button name="delete" class="editbtn" type="button" onclick="deleterow(this)">Delete</button></td>' +
        '</tr>';
    // update the table
    var table = document.getElementById('ddl_table');
    table.innerHTML += content;
}

// delete created row
function deleterow(row) {
    var i = row.parentNode.parentNode.rowIndex;
    document.getElementById("ddl_table").deleteRow(i)
}