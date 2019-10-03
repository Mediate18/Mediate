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
    $('.batchEditModal').on('show.bs.modal', function(event) {
        // If no selection is made, show a warning
        if(selected_entries.size == 0) {
            $('#batcheditmessagecontainer-'+batch_edit_option).show();
            $('#batcheditformcontainer-'+batch_edit_option).hide();
        } else {
            $('#batcheditmessagecontainer-'+batch_edit_option).hide();
            $('#batcheditformcontainer-'+batch_edit_option).show();

            // Remove and add all selected entries
            $(".selected-entry").remove();
            selected_entries.forEach(entry => {
                $('#form_'+batch_edit_option).append($('<input>', {
                    class: "selected-entry",
                    type: 'hidden',
                    name: "items",
                    value: entry
                }));
            });

            // Reset the form
            $('#form_'+batch_edit_option).trigger("reset").find(".django-select2").val(null).trigger('change');
        }
    });
});