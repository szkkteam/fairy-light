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
				updateNumOfItems(e, resp.numOfItems);
			});
		};
		
		var updateNumOfItems = function(e, itemCnt) {
			// Call the registered callback function
			opts.callbacks.onCounterUpdated.call(e, itemCnt);
			// Store the fetched value
			e.numOfItems = itemCnt;
			// Update DOM element
			cartContent.find('[data-count]').attr('data-count', itemCnt);
		};
		
		var getCartContent = function(e) {
			// Update the placeholder text
			$(opts.delegates.cartContent).html(opts.messages.cartLoading);

			htmlRequest(opts.urls.cartContent || cartContent.find('a').attr('href'), 'GET').then( function(resp) {
				// Call the registered callback function
				opts.callbacks.onCartUpdated.call(e, resp);
				// Update DOM element
				$(opts.delegates.cartContent).html(resp);
			});
		}
		
		var add = function(e) {
			jsonRequest(cartContent.find('a').attr('href'), 'POST').then( function(resp) {
				if (that.opts.callbacks.onAdd.call(e, resp)) {
					updateNumOfItems(resp.shopItems);
				} else {
					// Store the fetched value
					e.numOfItems = resp.shopItems;
				}
			});
		};
		
		var remove = function(e) {
			jsonRequest(cartContent.find('a').attr('href'), 'DELETE').then( function(resp) {
				if (opts.callbacks.onClear.call(e, resp)) {
					updateNumOfItems(resp.shopItems);
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

		this.initialize = function() {
				// Update the cart counter indicator
				getNumOfItems(this);
				// Register Open cart event
				$(cartContent).on('click', function(e) {
					e.preventDefault();
					getCartContent(this);
				});
				// Register Add to cart event
				if (opts.delegates.buyButton) {
					$(opts.delegates.buyButton).on('click', function(e) {
						e.preventDefault();
						add(this);					
					});
				}
				// Register Remove events
				if (opts.delegates.removeButton) {
					$(document.body).on('click', opts.delegates.removeButton, function(e) {
						e.preventDefault();
						remove(this);
					});
				}
				// Register Remove events
				if (opts.delegates.clearButton) {
					$(document.body).on('click', opts.delegates.clearButton, function(e) {
						e.preventDefault();
						remove(this);
					});

				}
				
				return this;

		};

		
		return this.initialize();		     
	};	
	
	$.fn.shoppingCart.defaults = {
		delegates : {
			cartContent: '',
			buyButton: '.photos-add-btn',	
			clearButton: '#shopping-cart-clear',
			removeButton: '.clear-item',
		},
		callbacks: {
			onCounterUpdated: function(e) { },
			onCartUpdated: function(e) { },			
			onAdd: function(e) { return true; },
			onClear: function(e) { return true; },
		},
		urls: {
			numberOfItems: '/shop/cart',
			cartContent: '/shop/cart',	
		},
		messages: {
			cartLoading: '<button class="btn btn-primary"><span class="spinner-border spinner-border-sm"></span>Loading..</button>',
		}

	};
	
}( jQuery ));

