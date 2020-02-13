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
                var aElement = $(this);
                const prevItemCount = Number($(opts.indicator).attr('data-val'));

                e.preventDefault();
                $.ajax({
                    type: 'POST',
                    url: $(this).attr('href'),
                    contentType: 'application/json;charset=UTF-8',
                    success: function (data) {
                        const itemCount = data.shopItems;

                        if (itemCount != prevItemCount) {
                            /* If animate is defined */
                            if (aElement.attr('data-animate') == 'true') {
                                var el = aElement;
                                var item = el.parent().parent().parent();
                                img = item.find('img');
                                
                                const offset = $(opts.indicator).offset();                            
                                cartTopOffset = offset.top - item.offset().top,
                                cartLeftOffset = offset.left - item.offset().left;

                                var flyingImg = $('<img class="b-flying-img">');
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
                                    updateItemsCounter(data.shopItems);
                                });                             
                                item.append(flyingImg);
                            } else if (aElement.next('.alert').length > 0) {
                                aElement.next('.alert').css('visibility', 'visible');    
                                updateItemsCounter(data.shopItems);
                            } else {
                                if (itemCount != prevItemCount) {
                                    /* Update the counter at the shopping cart. */
                                    updateItemsCounter(data.shopItems);
                                }
                            }                                                                  
                            /* Update the shopping cart details */
                            loadCartData();
                        }                        
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


                var el = $(opts.indicator);
                el.animate({
                    backgroundColor: "rgba(255,0,0,1)",
                  }, 200, function () {
                    $(opts.indicator).html(numOfItems);
                    $(opts.indicator).attr('data-val', numOfItems);
                  }).animate({
                    backgroundColor: "rgba(255,0,0,0)",
                  }, 400);                             
                  
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

