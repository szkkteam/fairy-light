/*
 * Shopping Cart init and event handlers
 */
$('#shopping-cart').shoppingCart({
    delegates : {
        cartModal: '#shopping-cart-modal',
        cartContent: '#shopping-cart-content',
        buyButton: '.cart-add',
        removeButton: '.cart-remove',
    },
    urls: {
        cartContent: cartContentUrl,
    },
    callbacks: {
        onCounterUpdated: function(cnt) {
            var element = $(this).find('a');
            element.addClass('grow');
            setTimeout(function() {
                element.removeClass('grow');
            }, 200);
            this.show();
        },
        onCartUpdated: function(e) {
            $('#shopping-cart-modal').modal('handleUpdate');
        },
        onAdd: function(e, resp) {
            var _that = this;
            // If item not present in the cart
            if (this.numOfItems != resp.shopItems) {
                // Get the defined animation if any
                const animationClass = e.attr('data-animation');
                // If animation defined
                if (animationClass) {
                    // Find card image
                    var item = e.parent().parent().parent();
                    img = item.find('img');

                    // Get cart offset
                    const offset = $(this).offset();
                    cartTopOffset = offset.top - item.offset().top,
                    cartLeftOffset = offset.left - item.offset().left;

                    var flyingImg = $('<img class="' +  animationClass + '">');
                    flyingImg.attr('src', img.attr('src'));
                    flyingImg.css('width', '200').css('height', '200');
                    flyingImg.animate({
                        top: cartTopOffset,
                        left: cartLeftOffset,
                        width: 50,
                        height: 50,
                        opacity: 0.1
                    }, 800, function () {
                        flyingImg.remove();
                        /* Update the counter at the shopping cart. */
                        _that.updateNumOfItems(resp.shopItems);
                    });
                    item.append(flyingImg);
                    return false;
                } else {
                    return true;
                }
            } else {
                return true;
            }
        },
    }
});
/*
 * Photo viewwer popup init and event handler
 */
$('.popup-parent').magnificPopup({
    delegate: 'a.popup-item',
    type:'ajax',
    ajax: {
        settings: null, // Ajax settings object that will extend default one - http://api.jquery.com/jQuery.ajax/#jQuery-ajax-settings
        // For example:
        // settings: {cache:false, async:false}

        cursor: 'mfp-ajax-cur', // CSS class that will be added to body during the loading (adds "progress" cursor)
        tError: '<a href="%url%">The content</a> could not be loaded.' //  Error message, can contain %curr% and %total% tags if gallery is enabled
    },
    gallery: {
        enabled: true, // set to true to enable gallery

        preload: [1,1], // read about this option in next Lazy-loading section

        navigateByImgClick: true,

        arrowMarkup: '<button title="%title%" type="button" class="mfp-arrow mfp-arrow-%dir%"></button>', // markup of an arrow button

        tPrev: 'Previous (Left arrow key)', // title for left button
        tNext: 'Next (Right arrow key)', // title for right button
        tCounter: '<span class="mfp-counter">%curr% of %total%</span>' // markup of counter
    },
    callbacks: {
        lazyLoad: function(item) {
            //console.log(item); // Magnific Popup data object that should be loaded
        },
        open: function() {
            var mfp = jQuery.magnificPopup.instance;

            // hide image nav when first/last
            if(mfp.index >= mfp.items.length - 1) {
                $(".mfp-container").addClass("mfp-last");
            } else {;
                $(".mfp-last").removeClass("mfp-last");
            }
            if(mfp.index == 0) {
                $(".mfp-container").addClass("mfp-first");
            } else {;
                $(".mfp-first").removeClass("mfp-first");
            }
        },
        change: function(){
            var mfp = jQuery.magnificPopup.instance;

            // hide image nav when first/last
            if(mfp.index >= mfp.items.length - 1) {
                $(".mfp-container").addClass("mfp-last");
            } else {;
                $(".mfp-last").removeClass("mfp-last");
            }
            if(mfp.index == 0) {
                $(".mfp-container").addClass("mfp-first");
            } else {;
                $(".mfp-first").removeClass("mfp-first");
            }
        }, //change
    },
});
/*
 * Open Album detail event handler
 */
$('.album-detail').click(function(e) {
    //e.preventDefault();
    var targetId = $(this).attr('data-target');
    var url = $(this).attr('href')
    $.ajax({
        type: 'GET',
        url: url,
        dataType: 'html',
        success: function (data) {
            $(targetId + ' .modal-content').html(data);
        },
        error: function (data) {
            console.log(data.responseJSON);
        }
    });
});