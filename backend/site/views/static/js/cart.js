/*
 * Shopping Cart init for index, portfolio, about and services pages.
 */
$('#shopping-cart').shoppingCart({
    delegates : {
        cartModal: '#shopping-cart-modal',
        cartContent: '#shopping-cart-content',
    },
    urls: {
        cartContent: "{{url_for('shop.cart_mini_refresh')}}",
    },
    callbacks: {
        onCounterUpdated: function(cnt) {
            if (cnt == 0) {
                this.hide();
            } else {
                this.show();
            }
        },
    }
});