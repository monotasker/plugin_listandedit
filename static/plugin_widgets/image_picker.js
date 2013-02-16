
$('.plugin_widgets_jqmodal').live('click', function(event){
//open modal dialog (using jquery-ui dialog) for image selection form
    var d_class = 'plugin_widgets_image_picker_dialog';
    // use existing dialog window if present
    var $old_dialog = $(d_class);
    if($old_dialog.length)
    {
        $old_dialog.html('').dialog('open');
    }
    else
    {
        var new_dialog = $('<div class="' + d_class + '"></div>');
        new_dialog.dialog({
            autoOpen:false,
            closeOnEscape:false,
            height:600,
            width:700,
            title:'Select an image',
        });
        $('.' + d_class).dialog('open');
    }
});
