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
                    data: JSON.stringify({ 'id': cardId, 'type': cardType }),
                    contentType: 'application/json;charset=UTF-8',
                    success: function (data) {
                        /* Update the counter at the shopping cart. */
                        updateItemsCounter(data.shopItems);
                        /* Update the shopping cart details */
                        loadCartData();
                        console.log(data.shopItems)
                    },
                    error: function (data) {
                        console.log(data.responseJSON);
                    }
                });    
            });        
        });

                    
        $(document.body).on('click', '.shopping-cart-clear', function(e) {
            e.preventDefault();
            const cardId = $(this).parent().parent().attr('data-id');

            $.ajax({
                type: 'POST',
                url: $(this).attr('href'),
                data: JSON.stringify({ 'id': cardId }),
                contentType: 'application/json;charset=UTF-8',
                success: function (data) {
                    /* Update the counter at the shopping cart. */
                    updateItemsCounter(data.shopItems);
                    /* Update the shopping cart details */
                    loadCartData();
                    console.log(data.shopItems)
                },
                error: function (data) {
                    console.log(data.responseJSON);
                }
            });    
        });

        function updateItemsCounter(numOfItems) {
            $(opts.numOfItemsIndicatorFilter).html(numOfItems);
        };

        /* Register common shopping cart functionality */
        function loadCartData ( ) {
            $.ajax({
                type: 'GET',
                url: '/photos/cart',
                dataType: 'html',
                success: function (data) {
                    console.log(data);
                    $('.popover .popover-body').html(data);
                    //popover.$tip.addClass(popover.options.placement);
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

