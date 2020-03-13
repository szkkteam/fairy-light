/*
 * Helper function to get the CSRF Token from the cookies
 */
function getCSRFToken() {
    return getCookie('csrf_token');
}

/*
 * Helper function to get value from cookies
 */
function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
        c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
        }
    }
    return "";
}

/*
 * AJAX Call setup to include the CSRF token in the header
 * CSRF Token is set in the HTML before the package is included.
 */
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrf_token);  // insert custom header
        }
    }
});

/*
 * Navigation bar and Cart icon scrolltofix init.
 */
$('#navbar').scrollToFixed();
$('#shopping-cart').scrollToFixed({
//		marginTop : $('#navbar').outerHeight(true) + 20,
    marginTop : 75,
    zIndex : 500,
    /*spacerClass: $('#spacer'),*/
});

// Workaround: window on load event used to make sure all media is loaded on the page then trigger a resize
// event to force the scollToFixed plugin to recalulate every parameter.
$(window).on('load', function() {
    $(window).resize();
});


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
