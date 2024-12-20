/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/
var stripePublicKey = JSON.parse(document.getElementById('id_stripe_public_key').textContent.trim());
var clientSecret = JSON.parse(document.getElementById('id_client_secret').textContent.trim());
var stripe = Stripe(stripePublicKey);
var style = {
    base: {
        color: 'white',
        fontFamily: '"Nunito", Arial, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '1.2rem',
        '::placeholder': {
            color: 'rgba(255, 255, 255, 0.65)',
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};

// Set up Stripe.js and Elements to use in checkout form, passing the client secret obtained in a previous step
const elements = stripe.elements();

// Create and mount the Payment Element
var card = elements.create('card', {style: style});
card.mount('#card-element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
var submitButton = document.getElementById('submit-button');

submitButton.addEventListener('click', function(ev) {
    ev.preventDefault(); // Prevent default anchor behavior (e.g., navigation)
    submitButton.classList.add('disabled'); // Add disabled styling
    card.update({ 'disabled': true });
    
    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
        }
    }).then(function(result) {
        if (result.error) {
            // Show error message
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html);

            // Re-enable button and card element
            card.update({ 'disabled': false });
            submitButton.classList.remove('disabled');
        } else {
            // Payment succeeded, submit the form
            if (result.paymentIntent.status === 'succeeded') {
                document.getElementById('payment-form').submit();
            }
        }
    });
});
