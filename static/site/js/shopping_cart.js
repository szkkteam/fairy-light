/*
	Resources:
	- https://learn.jquery.com/plugins/basic-plugin-creation/
*/
(function ( $ ) {
	
	$.fn.shoppingCart = function ( options ) {
		options = options || {};
		
		/* Configure options */
        var opts = $.extend( {}, $.fn.shoppingCart.defaults, options );
        
        /* Register each card shopping cart functionality */
        $(this).each( function() {

            const cardId = $(this).attr('data-id');
            const cardType = $(this).attr('data-type');

            /* Add item to shopping cart */
            $(this).find(opts.addToCartFilter).on('click', function(e) {
                e.preventDefault();

                $.ajax({
                    type: 'POST',
                    url: $(this).attr('href'),
                    contentType: 'application/json;charset=UTF-8',
                    success: function (data) {
                        /* Update the counter at the shopping cart. */
                        updateItemsCounter(data.shopItems);
                        /* Update the shopping cart details */
                        loadCartData();
                    },
                    error: function (data) {
                        console.log(data.responseJSON);
                    }
                });    
            });        
        });

        /* Remove element from cart */
        $(document.body).on('click', '.clear-item', function(e) {
            e.preventDefault();

            $.ajax({
                type: 'DELETE',
                url: $(this).attr('href'),
                contentType: 'application/json;charset=UTF-8',
                success: function (data) {
                    /* Update the counter at the shopping cart. */
                    updateItemsCounter(data.shopItems);
                    /* Update the shopping cart details */
                    loadCartData();
                },
                error: function (data) {
                    console.log(data.responseJSON);
                }
            });    
        });

        $(document.body).on('click', '#shopping-cart-clear', function(e) {
            e.preventDefault();

            $.ajax({
                type: 'DELETE',
                url: $(this).attr('href'),
                contentType: 'application/json;charset=UTF-8',
                success: function (data) {
                    /* Update the counter at the shopping cart. */
                    updateItemsCounter(data.shopItems);
                    /* Update the shopping cart details */
                    loadCartData();
                },
                error: function (data) {
                    console.log(data.responseJSON);
                }
            });    
        })

        function updateItemsCounter(numOfItems) {
            $(opts.numOfItemsIndicatorFilter).html(numOfItems);
        };

        /* Register common shopping cart functionality */
        function loadCartData ( ) {
            $.ajax({
                type: 'GET',
                url: '/shop/cart',
                dataType: 'html',
                success: function (data) {
                    $('.popover .popover-body').html(data);
                },
                error: function (data) {
                    console.log(data.responseJSON);
                }
            }); 
        };
				
		return this;
	};	
	
	$.fn.shoppingCart.defaults = {
		addToCartFilter : '.photos-add-btn',
        numOfItemsIndicatorFilter : '#shopping-cart-items',
        openShoppingCartFilter: '#shopping-cart',
		shoppingCartDetailsFilter : '#shopping-cart-wrapper',
		onFailedOperation : function () {},
		imgPreviewElement : null,
		inputElements : null,
		/* buildPreview = function (src, filename ) { return buildPreviewHtml(src, filename) },*/
		/*
		foreground: "red",
		background: "yellow"
		*/
	};
	
}( jQuery ));

