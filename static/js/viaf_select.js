$(document).ready(function(){
        // For VIAF search box, ...
        $('#id_viaf_id').change(function() {
            // ... show a link when a selection is made;
            $('#viaf_uri').attr('href', $(this).val());
            $('#viaf_uri').html($(this).val());

            // ... copy the title to the Title field;
            var title = $('#id_viaf_id option').last().text()
            $('#id_title').val(title)
        });
});