$(document).ready(function(){
        /* If there is a VIAF search box, show a link when a selection is made. */
        $('#id_viaf_id').change(function() {
            $('#viaf_uri').attr('href', $(this).val());
            $('#viaf_uri').html($(this).val());
        });
});