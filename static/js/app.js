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

