/*
 * Cart detail update event handler
 */
$('#checkout-modal-btn').click(function(e) {
    //e.preventDefault();
    var targetId = $(this).attr('data-target');
    var url = $(this).attr('href')
    var targetDOM = $(targetId + ' .modal-content')
    targetDOM.html('<button class="btn btn-primary"><span class="spinner-border spinner-border-sm"></span>Loading..</button>');
    $.ajax({
        type: 'GET',
        url: url,
        dataType: 'html',
        success: function (data) {
            targetDOM.html(data);
        },
        error: function (data) {
            console.log(data.responseJSON);
        }
    });
});

//Fixing jQuery Click Events for the iPad
var ua = navigator.userAgent, event = (ua.match(/iPad/i)) ? "touchstart" : "click";
var e = $('#cart tr.cart-table-album');
$(document.body).on(event, '#cart tr.cart-table-album', function() {
    $(this).toggleClass("active", "").nextUntil('.cart-table-album, .cart-table-total').css('display', function(i, v){
        return this.style.display == 'table-row'? 'none' : 'table-row';
    });
    $(this).find('td span.cart-toggle-element').css('visibility', function(i, v) {
        return this.style.visibility == 'visible'? 'hidden' : 'visible';
    });
});

/*
 * Shopping cart init and event handler
 */
$('#shopping-cart').shoppingCart({
delegates : {
    cartModal: '',
    cartContent: '#cart-details',
    buyButton: '',
    removeButton: '.clear-item',
},
urls: {
    cartContent: "{{url_for('shop.cart_detail_refresh')}}",
},
callbacks: {
    onCounterUpdated: function(cnt) {
        // Make sure the floating cart is hidden
        this.hide();
        if (cnt == 0) {
            $('#checkout-modal-btn').addClass('disabled').attr('aria-disabled', true);
        } else {
            $('#checkout-modal-btn').removeClass('disabled').attr('aria-disabled', false);
        }
    },
}
});