var selected_entries = new Set();

function change_checkbox(checkbox, checked) {
    var id = checkbox.attr('id');
    if(checked) {
        selected_entries.add(id);
    } else {
        selected_entries.delete(id);
        $("#checkbox_column").prop('checked', false);
    }
//    console.log(selected_entries);
}

$(document).ready(function(){
    // Check all boxes if column header is checked
    // Uncheck all boxes if column header is unchecked
    $("#checkbox_column").change(function(){
        var all_checked = false;
        if($(this).is(":checked")) {
            all_checked = true;
        }
        $(".checkbox").each(function(index) {
            $(this).prop('checked', all_checked);
            change_checkbox($(this), all_checked);
        });
    });

    // An individual checkbox is changed
    $(".checkbox").change(function() {
        change_checkbox($(this), $(this).is(":checked"));
    });

    // When the batch edit modal is opened, remove all inputs of selected entries
    // and move the form of the current batch edit type to the modal
    $('#batchEditModal').on('show.bs.modal', function(event) {
        // If no selection is made, don't open the modal
        if(selected_entries.size == 0) {
//            alert("Please, first select one or more entries.");
            // Move the form to the modal
            $('#batcheditformcontainer').children().each(function(index) {
                $(this).appendTo('#batch-edit-modal-content');
            });
            $('#no-selected-entries-warning').appendTo('#batcheditformcontainer');
        } else {
            var batcheditoptionid = $('#open-batch-edit').attr('batcheditoptionid')

            // Remove and add all selected entries
            $(".selected-entry").remove();
            selected_entries.forEach(entry => {
                $('#form_'+batcheditoptionid).append($('<input>', {
                    class: "selected-entry",
                    type: 'hidden',
                    name: "items",
                    value: entry
                }));
            });

            // Move the form to the modal
            $('#batcheditformcontainer').children().each(function(index) {
                $(this).appendTo('#batch-edit-modal-content');
            });
            $('#form_'+batcheditoptionid).appendTo('#batcheditformcontainer');
        }
    });
});