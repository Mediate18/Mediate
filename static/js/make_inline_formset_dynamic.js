/*
  This script make an inline formset dynamically create new forms
  in concordance with the inline_formset_table.html template.
*/
function make_inline_formset_dynamic(formset_name, formset_prefix) {
    // Dynamically add a form to the form set
    $('#add_more_'+formset_name).click(function() {
        var form_idx = $('#id_'+formset_prefix+'-TOTAL_FORMS').val();
        $('#form_set_'+formset_name).append($('#empty_form_'+formset_name).html()
            .replace(/__prefix__/g, form_idx)
            .replace(/__prefixplusone__/g, parseInt(form_idx) + 1));
        $('#form_set_'+formset_name).find('select').djangoSelect2();

        // Workaround for the fact that djangoSelect2() as used above duplicates the selects.
        $('#form_set_'+formset_name).find('select ~ span:nth-of-type(2)').hide();

        $('#id_'+formset_prefix+'-TOTAL_FORMS').val(parseInt(form_idx) + 1);
    });
}