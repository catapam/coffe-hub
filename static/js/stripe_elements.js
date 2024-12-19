/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/
var stripe_public_key = JSON.parse(document.getElementById('id_stripe_public_key').textContent.trim());
var client_secret = JSON.parse(document.getElementById('id_client_secret').textContent.trim());
var stripe = Stripe(stripe_public_key);
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