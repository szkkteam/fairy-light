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
        /* Store the cart content element. It should be the shopping cart icon */
        var cartContent = $(this);
        /*
		 * Public variables
		*/
		this.numOfItems = cartContent.attr('data-count'); //TODO: Or initialize it with 0

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
		
		var getNumOfItems = function() {
			jsonRequest(this.opts.urls.numOfItems || cartContent.attr('href'), 'GET').then( function(resp) {
				updateNumOfItems(resp.numOfItems);
			});
		};
		
		var updateNumOfItems = function(itemCnt) {
			// Call the registered callback function
			this.opts.callbacks.onCounterUpdated.apply(this, itemCnt);
			// Store the fetched value
			this.numOfItems = itemCnt;
			// Update DOM element
			cartContent.find('[data-count]').attr('data-count', itemCnt);
		};
		
		var getCartContent = function(e) {
			var that = this;
			// Update the placeholder text
			$(that.opts.delegates.cartContent).html(this.opts.messages.cartLoading);

			htmlRequest(this.opts.urls.cartContent || e.attr('href'), 'GET').then( function(resp) {
				// Call the registered callback function
				this.opts.callbacks.onCartUpdated.apply(that, resp);
				// Update DOM element
				$(that.opts.delegates.cartContent).html(resp);
			});
		}
		
		var add = function(e) {
			var that = this;
			jsonRequest($(e).attr('href'), 'POST').then( function(resp) {
				if (that.opts.callbacks.onAdd(that, resp) {
					updateNumOfItems(resp.shopItems);
				} else {
					// Store the fetched value
					this.numOfItems = resp.shopItems;
				}
			});
		};
		
		var remove = function(e) {
			var that = this;
			jsonRequest($(e).attr('href'), 'DELETE').then( function(resp) {
				if (that.opts.callbacks.onClear(that, resp) {
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
		this.initialize = function() {
			// Update the cart counter indicator
			getNumOfItems();
			// Register Open cart event
			$(cartContent).on('click', function(e) {
				e.preventDefault();
				getCartContent(this);
			});
			// Register Add to cart event
			if (this.opts.delegates.buyButton) {
				$(this.opts.delegates.buyButton).on('click', function(e) {
					e.preventDefault();
					add(this);					
				});
			}
			// Register Remove events
			if (this.opts.delegates.removeButton) {
				$(document.body).on('click', this.opts.delegates.removeButton, function(e) {
					e.preventDefault();
					remove(this);
				});
			}
			// Register Remove events
			if (this.opts.delegates.clearButton) {
				$(document.body).on('click', this.opts.delegates.clearButton, function(e) {
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
			onCounterUpdated: function(t, e) { },
			onCartUpdated: function(t, e) { },			
			onAdd: function(t, e) { return true; },
			onClear: function(t, e) { return true; },
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

