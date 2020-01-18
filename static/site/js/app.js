
function getCSRFToken() {
    return getCookie('csrf_token');
}

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


$(document).ready( function(){

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
});