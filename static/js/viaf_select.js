$(document).ready(function(){
        // For VIAF search box, ...
        var viaf_select_id = 'viaf_id';
        if('viaf_select_id' in js_variables) {
            viaf_select_id = js_variables['viaf_select_id'];
        }
        $('#id_'+viaf_select_id).change(function() {
            // ... show a link when a selection is made;
            var link = $('#id_viaf_id').select2('data')[0].external_url;
            if(link != "") {
                $('#viaf_uri').attr('href', link);
                $('#viaf_uri').html(link);
            }

            // ... copy the title to the Title field;
            var result_class_name = $('#id_viaf_id').select2('data')[0].class_name;
            console.log("Class_name: " + result_class_name);
            if(result_class_name == "local_work") {
                $('#id_title').attr('readonly', true);
            } else {
                $('#id_title').removeAttr("readonly");
            }
            var title = $('#id_viaf_id').select2('data')[0].clean_text;
            $('#id_title').val(title);
        });

        $('#id_'+viaf_select_id).on('select2:unselect', function(e){
            $('#id_title').removeAttr("readonly");
            $('#id_title').val("");
        });
});

