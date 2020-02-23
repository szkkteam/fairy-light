


var initPayment = function(stripe_key, client_secret, success_url, processing_url, failed_url) {
  // Init stripe with the key
  var stripe = Stripe(stripe_key);
  var elements = stripe.elements();
	
	var submitButton = $('#submit-btn');
	//const submitButtonText = $(submitButton).text;
	
	var validateEmail = function(sEmail) {
	  var reEmail = /^(?:[\w\!\#\$\%\&\'\*\+\-\/\=\?\^\`\{\|\}\~]+\.)*[\w\!\#\$\%\&\'\*\+\-\/\=\?\^\`\{\|\}\~]+@(?:(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-](?!\.)){0,61}[a-zA-Z0-9]?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9\-](?!$)){0,61}[a-zA-Z0-9]?)|(?:\[(?:(?:[01]?\d{1,2}|2[0-4]\d|25[0-5])\.){3}(?:[01]?\d{1,2}|2[0-4]\d|25[0-5])\]))$/;

	  if(!sEmail.match(reEmail)) {
		return false;
	  }

	  return true;

	}
	
	// Custom styling can be passed to options when creating an Element.
	// (Note that this demo uses a wider set of styles than the guide below.)
	var style = {
		base: {
		lineHeight: '1.429'
		},
		invalid: {
		color: '#fa755a',
		iconColor: '#fa755a'
		}
	};

	// Create an instance of the card Element.
	var card = elements.create('card', {
		style: style,
		hidePostalCode : true,
	});

	// Add an instance of the card Element into the `card-element` <div>.
	card.mount('#card-element');

	// Monitor change events on the Card Element to display any errors.
	card.on('change', ({error}) => {
		const cardErrors = $('#card-errors');
		if (error) {
			cardErrors.text(error.message);
			//cardErrors.addClass('visible');
		} else {
			cardErrors.text("");
			//cardErrors.removeClass('visible');
		}
		// Re-enable the Pay button.
		$(submitButton).prop('disabled', false);
	});
	
	$('input[name=email]').on('blur', function (e) {
		const valid = validateEmail($(this).val());
		if (valid) {
			$(this).next('.form-errors').text = "";
		} else {
			$(this).next('.form-errors').text = "Invalid email address";
		}
		
	});
	
	/**
	   * Handle the form submission.
	   *
	   * This uses Stripe.js to confirm the PaymentIntent using payment details collected
	   * with Elements.
	   *
	   * Please note this form is not submitted when the user chooses the "Pay" button
	   * or Apple Pay, Google Pay, and Microsoft Pay since they provide name and
	   * shipping information directly.
	   */
	console.log("Test");
	  // Listen to changes to the user-selected country.
	$('select[name=country]').on('change', function (e) {
		event.preventDefault();
	});
		  // TODO: What to do with country? Currently only 1 payment method will be available
		  //selectCountry(event.target.value);
			  
	$(submitButton).on('click', function(ev) {
		ev.preventDefault();
		
		/* Validate the form fields */


		const nameField = $('input[name=name]');
		const emailField = $('input[name=email]');
		const country = $('select[name=country] option:selected').val();
		const postalCodeField = $('input[name=zip]');
		const addressField = $('input[name=address]');
		const cityField = $('input[name=city]');
		const tcField = $('#terms-condition input[type=checkbox]');

		const name = $(nameField).val();
		const address = $(addressField).val();
		const city = $(cityField).val();
		const email = $(emailField).val();
		const postalCode = $(postalCodeField).val();
		const tc = $(tcField).is(':checked');

		var error = false

		if (name == "") {
			$(nameField).next('.form-errors').text("Name must be filled out.");
			error = true;
		} else {
			$(nameField).next('.form-errors').text("");
		}

		if (address == "") {
			$(addressField).next('.form-errors').text("Address must be filled out.");
			error = true;
		} else {
			$(addressField).next('.form-errors').text("");
		}

		if (city == "") {
			$(cityField).next('.form-errors').text("City must be filled out.");
			error = true;
		} else {
			$(cityField).next('.form-errors').text("");
		}

		if (email == "") {
			$(emailField).next('.form-errors').text("Email must be filled out.");
			error = true;
		} else {
			const valid = validateEmail(email);
			if (valid) {
				$(emailField).next('.form-errors').text("");
			} else {
				$(emailField).next('.form-errors').text("Invalid email address");
				error = true;
			}
			
		}

		if (postalCode == "") {
			$(postalCodeField).next('.form-errors').text("Postal Code must be filled out.");
			error = true;
		} else {
			$(postalCodeField).next('.form-errors').text("");
		}

		if (!tc) {
      var c = $(tcField).next('.form-errors');
			$(tcField).nextAll('.form-errors').text("You must aggree with the Terms & Conditions.")
			error = true;
		} else {
			$(tcField).nextAll('.form-errors').text("");
		}

		if (error) return;

		const shipping = {
			name,
			//email,
			address: {
				line1: address,
				city: city,
				state: "",
				// TODO: Maybe add line1
				// TODO: Maybe add city
				postal_code: postalCode,
				// TODO: Maybe add state
				country: country,
			}
		};
		
		// Disable the Pay button to prevent multiple click events.
		submitButton.prop('disabled', true);
		$('.pay-btn-idle').css('display', 'none');
		$('.pay-btn-processing').css('display', 'block');	

		// Currently only card payment is supported
		stripe.confirmCardPayment(client_secret, 
		{
			payment_method: {
				card: card,
				billing_details: {
					name: name,
					email: email,
				},
			},
			shipping,
			receipt_email: email
		}).then(function(result) {
			const cardErrors = $('#card-errors');
			if (result.error) {				
				cardErrors.text(result.error.message);
				
				console.log(result.error.message);
				// Re-enable the Pay button.
				//$(submitButton).prop('disabled', false);
			} else {
				cardErrors.text("");
				// The payment has been processed!
				console.log(result);
				if (result.paymentIntent.status === 'succeeded') {
					// Show a success message to your customer
					// There's a risk of the customer closing the window before callback
					// execution. Set up a webhook or plugin to listen for the
					// payment_intent.succeeded event that handles any business critical
					// post-payment actions.
					// Success! Payment is confirmed. Update the interface to display the confirmation screen.
					window.location.href = success_url;
					// TODO: Redirect user
				} else if (result.paymentIntent.status === 'processing') {
					// Success! Now waiting for payment confirmation. Update the interface to display the confirmation screen.
					window.location.href = processing_url;
				} else {
					// Success! Now waiting for payment confirmation. Update the interface to display the confirmation screen.
					window.location.href = failed_url;
				}
				
			}
		});
	});

};
