/*
	Resources:
	- https://learn.jquery.com/plugins/basic-plugin-creation/
*/
(function ( $ ) {
	
	$.fn.shoppingCart = function ( options ) {
		options = options || {};
		
		/* Configure options */
        var opts = $.extend( {}, $.fn.shoppingCart.defaults, options );
        
        /* Store the cart content element */
        var cartContent = $(this);

        /* Register Buy buttons */
        if (opts.buyButton) {
            $(document.body).on('click', opts.buyButton, function(e) {
                /* Prevent default action if any */
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
        }
        /* Register Remove buttons */
        if (opts.removeButton) {
            $(document.body).on('click', opts.removeButton, function(e) {
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
        }
        if (opts.clearButton) {
            $(document.body).on('click', opts.clearButton, function(e) {
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
        }

        function updateItemsCounter(numOfItems) {
            if (opts.indicator) {
                $(opts.indicator).html(numOfItems);
            }
            
        };

        /* Register common shopping cart functionality */
        function loadCartData ( ) {
            if (opts.urlGetCartContent) {
                $.ajax({
                    type: 'GET',
                    url: opts.urlGetCartContent,
                    cache:false,
                    dataType: 'html',
                    success: function (data) {
                        $(cartContent).html(data)
                    },
                    error: function (data) {
                        console.log(data);
                    }
                }); 
            }
        };
	};	
	
	$.fn.shoppingCart.defaults = {
        buyButton: '.photos-add-btn',
        clearButton: '#shopping-cart-clear',
        removeButton: '.clear-item',
        indicator: '#shopping-cart-items',
        urlGetCartContent: '/shop/cart',
	};
	
}( jQuery ));

