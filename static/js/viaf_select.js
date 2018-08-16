function prepare_select_widget(viaf_select_id) {
        console.log("viaf_select_id: " + viaf_select_id);
        $('#id_'+viaf_select_id).change(function() {
            // ... show a link when a selection is made;
            if($(this).select2('data').length > 0) {
                var link = $(this).select2('data')[0].external_url;
                var html = $(this).select2('data')[0].clean_text + " (" + $(this).select2('data')[0].url_type + ")"
                if(link != "") {
                    $('#'+viaf_select_id+'_uri').attr('href', link);
                    $('#'+viaf_select_id+'_uri').html(html);
                }

                // ... copy the title to the Title field;
                var result_class_name = $(this).select2('data')[0].class_name;
                console.log("Class_name: " + result_class_name);
                if(result_class_name == "local_work") {
                    $('#id_title').attr('readonly', true);
                } else {
                    $('#id_title').removeAttr("readonly");
                }
                var title = $(this).select2('data')[0].clean_text;
                title = $('<div/>').html(title).text();  // html decode
                $('#id_title').val(title);
            } else {
                $('#'+viaf_select_id+'_uri').attr('href', "");
                $('#'+viaf_select_id+'_uri').html("");
            }
        });

        $('#id_'+viaf_select_id).on('select2:unselect', function(e){
            $('#id_title').removeAttr("readonly");
            $('#id_title').val("");
        });
}

$(document).ready(function(){
        // For VIAF search box, ...
        var viaf_select_id = 'viaf_id';
        if('js_variables' in window && 'viaf_select_id' in js_variables) {
            viaf_select_id = js_variables['viaf_select_id'];
        }
        if(typeof viaf_select_id == "string") {
            prepare_select_widget(viaf_select_id);
        } else {
            viaf_select_id.forEach(function(currentValue, index, arr){
                prepare_select_widget(currentValue);
            });
        }
});

