/*
 * Facebook SDK init
 */
window.fbAsyncInit = function() {
    FB.init({
    appId            : '{{facebook_app_id}}',
    autoLogAppEvents : true,
    xfbml            : true,
    version          : 'v6.0'
    });
};


/*
 * Share on facebook button event handler
 */
$('.share-facebook').click(function(e) {
    e.preventDefault();
    FB.ui({
        method: 'share',
        href: $(this).attr('href'),
    }, function(response){});
});
