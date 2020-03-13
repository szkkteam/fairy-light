
/* Query all the subscribe forms */
$('#subscribe-form').on('submit', function(e) {
    e.preventDefault(); // avoid to execute the actual submit of the form.

    var responseDiv = $(this).find('#feedback');
    responseDiv.removeClass('valid-feedback').removeClass('invalid-feedback').hide();

    $.ajax({
        type: $(this).attr('method'),
        url: $(this).attr('action'),

        data: JSON.stringify({ 'email': $(this).find('input[type="email"]').val() }),
        contentType: 'application/json;charset=UTF-8',
        success: function (data) {
            responseDiv.addClass('valid-feedback').show();
            responseDiv.html('You are successfully subscribed to our mailing list!')
        },
        error: function (data) {
            responseDiv.addClass('invalid-feedback').show();
            responseDiv.html(data.responseJSON.errors.email[0]);
        }
    });
});

/*
 * Common async form handler
*/
$('form.ajax-form').on('submit', function(e) {
    var from = $(this);
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
    submitBtn.children('submit-btn-idle').css('display', 'none');
    submitBtn.children('submit-btn-processing').css('display', 'block');

    send.then( function(result) {
        // Re-enable the button
        submitBtn.prop('disabled', false);
        submitBtn.children('submit-btn-idle').css('display', 'block');
        submitBtn.children('submit-btn-processing').css('display', 'none');
        if (result.error) {
            /* Process error message */
            /* Iterate over the errors */
            Object.keys(result.error.message.errors).forEach(function(key) {
                const error_msg = result.error.message.errors[key][0];
                /* find the corresponding element */
                form.find('input[name=' + key + ']').nextAll('.form-errors').text(error_msg);
                // ...
            });
        } else {
            /* Process success message */
            /* Clear all from error html text */
            Object.keys(obj).forEach(function(key) {
                /* find the corresponding element */
                form.find('input[name=' + key + ']').nextAll('.form-errors').text("");
                // ...
            });
            form.find('.form-success').text(result.message);
        }
    });
});

/* Query all the contact forms */
$('#contact-form').on('submit', function(e) {
    e.preventDefault(); // avoid to execute the actual submit of the form.

    var formDiv = this;

    var responseDiv = $(this).find('.validation');
    responseDiv.removeClass('valid-feedback').removeClass('invalid-feedback').hide();

    var feedbackDiv = $(this).find('#feedback');
    feedbackDiv.removeClass('valid-feedback').removeClass('invalid-feedback').hide();

    var name = $(this).find('input[name="name"]').val();
    var email = $(this).find('input[name="email"]').val();
    var message = $(this).find('textarea[name="message"]').val();

    $.ajax({
        type: $(this).attr('method'),
        url: $(this).attr('action'),

        data: JSON.stringify({ 'name': name, 'email': email, 'message': message }),
        contentType: 'application/json;charset=UTF-8',
        success: function (data) {
            feedbackDiv.addClass('valid-feedback').show();
            feedbackDiv.html('Your question has been sent.')
        },
        error: function (data) {
            console.log(data.responseJSON.errors);
            const errorKey = Object.keys(data.responseJSON.errors)[0];
            var errorDiv = $(formDiv).find('#' + errorKey);

            errorDiv.addClass('invalid-feedback').show();
            errorDiv.html(data.responseJSON.errors[errorKey]);
        }
    });
});