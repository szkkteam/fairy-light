/*
 * Facebook SDK init
 */
if (facebookAppId) {
    window.fbAsyncInit = function() {
        FB.init({
        appId            : facebookAppId,
        autoLogAppEvents : true,
        xfbml            : true,
        version          : 'v6.0'
        });
    };
}


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
