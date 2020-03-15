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
                // Get alert element if any
                const alertElement = e.nextAll('.alert');
                if (alertElement.length) {
                    alertElement.css('visibility', 'visible');
                }
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
/*
 * Init venobox
 */
$('.venobox').venobox({
    overlayColor: 'rgba(0,0,0,0.6)',
    bgcolor: '#000',
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