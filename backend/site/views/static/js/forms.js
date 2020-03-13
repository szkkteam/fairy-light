
/*
 * Common async form handler
*/
$('form.ajax-form').on('submit', function(e) {
    e.preventDefault(); // avoid to execute the actual submit of the form.
    var form = $(this);
    var submitBtn = $(this).find('button[type=submit]');
    /* Prepare form values */
    var formValues = $(this).serializeArray();
    var obj = {};
    for (var a = 0; a < formValues.length; a++) {
         obj[formValues[a].name] = formValues[a].value;
    }
    const jsonData = JSON.stringify(obj);

    /* Prepare ajax object */
    var send = $.ajax({
        type: $(this).attr('method'),
        url: $(this).attr('action'),
        data: jsonData ,
        dataType: 'json',
        contentType: 'application/json;charset=UTF-8',
    });

    /* Control the submit button */
    // Disable the Pay button to prevent multiple click events.
    submitBtn.prop('disabled', true);
    /* Active the processing element if exists */
    submitBtn.children('.submit-btn-idle').css('display', 'none');
    submitBtn.children('.submit-btn-processing').css('display', 'block');

    send.then( function(result) {
        // Re-enable the button
        submitBtn.prop('disabled', false);
        submitBtn.children('.submit-btn-processing').css('display', 'none');
        submitBtn.children('.submit-btn-idle').css('display', 'block');

        /* Process success message */
        /* Clear all from error html text */
        Object.keys(obj).forEach(function(key) {
            /* find the corresponding element */
            form.find('[name=' + key + ']').nextAll('.form-errors').text("");
            // ...
        });
        form.find('.form-success').text("Thanks for submitting!");
    })
    .fail( function(result) {
        // Re-enable the button
        submitBtn.prop('disabled', false);
        submitBtn.children('.submit-btn-processing').css('display', 'none');
        submitBtn.children('.submit-btn-idle').css('display', 'block');

        /* Process error message */
            /* Iterate over the errors */
            Object.keys(result.responseJSON.errors).forEach(function(key) {
                const error_msg = result.responseJSON.errors[key][0];
                /* find the corresponding element */
                form.find('[name=' + key + ']').nextAll('.form-errors').text(error_msg);
                // ...
            });
    });
});
