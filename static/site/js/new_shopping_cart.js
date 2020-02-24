/*
	Resources:
	- https://learn.jquery.com/plugins/basic-plugin-creation/
*/
(function ( $ ) {
	
	$.fn.shoppingCart = function ( options ) {
		options = options || {};
		
		/*
		 * Private variables
		*/
		/* Configure options */
		var opts = $.extend( true, $.fn.shoppingCart.defaults, options );		
		var cartContent = $(this);
        /*
		 * Public variables
		*/
		/* Store the cart content element. It should be the shopping cart icon */
		
		this.numOfItems = parseInt(cartContent.find('[data-count]').attr('data-count')); //TODO: Or initialize it with 0

        /*
		 * Private Methods
		*/
		var jsonRequest = function(url, type, data = null) {
			return $.ajax({
                    type: type,
                    url: url,
                    contentType: 'application/json;charset=UTF-8',
					dataType: 'json',
					data: data
                });  			
		};
		
		var htmlRequest = function(url, type) {
			return $.ajax({
				type: type,
				url: url,
				contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
				dataType: 'html'
			});
		}
		
		var getNumOfItems = function(e) {
			const url1 = opts.urls.numberOfItems;
			const url2 =  cartContent.find('a').attr('href');
			jsonRequest(url1 || url2, 'GET').then( function(resp) {
				e.updateNumOfItems(resp.numOfItems);
			});
		};
				
		var getCartContent = function(e, usePlaceholder=true) {
			// Update the placeholder text
			if (usePlaceholder) {
				$(opts.delegates.cartContent).html(opts.messages.cartLoading);
			}

			htmlRequest(opts.urls.cartContent || cartContent.find('a').attr('href'), 'GET').then( function(resp) {
				// Update DOM element
				$(opts.delegates.cartContent).html(resp);
				// Call the registered callback function
				opts.callbacks.onCartUpdated.call(e, resp);
			});
		}
		
		var add = function(t, e) {
			jsonRequest(e.attr('href'), 'POST').then( function(resp) {
				if (opts.callbacks.onAdd.call(t, e, resp)) {
					t.updateNumOfItems(resp.shopItems);
				} else {
					// Store the fetched value
					t.numOfItems = resp.shopItems;
				}
			});
		};
		
		var remove = function(t, e) {
			jsonRequest(e.attr('href'), 'DELETE').then( function(resp) {
				if (opts.callbacks.onClear.call(t, e, resp)) {
					// Delete Element. Not working. Total is not refreshed. Maybe fetch total?
					//e.parent().parent().remove();
					getCartContent(t, false);
					t.updateNumOfItems(resp.shopItems);
				} else {
					// Store the fetched value
					this.numOfItems = resp.shopItems;
				}				
			});
		};
		
        /*
		 * Public Methods
		*/
		this.hide = function() {
			cartContent.hide();
		};
		this.show = function() {
			cartContent.show();
		};

		this.updateNumOfItems = function(itemCnt) {
			// Call the registered callback function
			opts.callbacks.onCounterUpdated.call(this, itemCnt);
			// Store the fetched value
			this.numOfItems = itemCnt;
			// Update DOM element
			cartContent.find('[data-count]').attr('data-count', itemCnt);
		};

		this.initialize = function() {
				var _that = this;
				// Update the cart counter indicator
				getNumOfItems(this);
				// Register Open cart event
				$(cartContent).on('click', function(e) {
					//e.preventDefault();
					getCartContent(_that);
				});
				// Register Add to cart event
				if (opts.delegates.buyButton) {
					$(document.body).on('click', opts.delegates.buyButton, function(e) {
						e.preventDefault();
						add(_that, $(e.currentTarget));					
					});
				}
				// Register Remove events
				if (opts.delegates.removeButton) {
					$(document.body).on('click', opts.delegates.removeButton, function(e) {
						e.preventDefault();
						remove(_that, $(e.currentTarget));
					});
				}
				// Register Remove events
				if (opts.delegates.clearButton) {
					$(document.body).on('click', opts.delegates.clearButton, function(e) {
						e.preventDefault();
						remove(_that, $(e.currentTarget));
					});

				}
				
				return this;

		};

		
		return this.initialize();		     
	};	
	
	$.fn.shoppingCart.defaults = {
		delegates : {
			cartModal: '#shopping-cart-modal',
			cartContent: '',
			buyButton: '.cart-add',	
			clearButton: '#shopping-cart-clear',
			removeButton: '.cart-remove',
		},
		callbacks: {
			onCounterUpdated: function(e) { },
			onCartUpdated: function(e) { },			
			onAdd: function(e, resp) { return true; },
			onClear: function(e, resp) { return true; },
		},
		urls: {
			numberOfItems: '/shop/cart',
			cartContent: '/shop/cart/mini',
		},
		messages: {
			cartLoading: '<div class="d-flex justify-content-center"><div class="spinner-border" role="status"><span class="sr-only">Loading...</span></div></div>',
		}

	};
	
}( jQuery ));

