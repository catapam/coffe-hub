/**
 * Core logic/payment flow for this comes from here:
 * https://stripe.com/docs/payments/accept-a-payment
 *
 * CSS from here:
 * https://stripe.com/docs/stripe-js
 */
let stripe, elements, card;

/**
 * Initialize Stripe and set up the payment form.
 * @param {string} stripePublicKey - The public key for Stripe.
 * @param {string} clientSecret - The client secret for payment.
 */
function setupStripe(stripePublicKey, clientSecret) {
    stripe = Stripe(stripePublicKey);

    // Define styling for the Stripe card element
    const style = {
        base: {
            color: 'white',
            fontFamily: '"Nunito", Arial, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': {
                color: 'rgba(255, 255, 255, 0.65)',
            },
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545',
        },
    };

    // Set up Stripe.js and Elements for the checkout form
    elements = stripe.elements();
    card = elements.create('card', { style: style });
    card.mount('#card-element');

    // Add event listener for real-time card validation errors
    setupCardValidation(card);

    // Add event listener for form submission
    setupFormSubmission(card, clientSecret);
}

/**
 * Handle real-time validation errors on the card element.
 * @param {object} card - Stripe card element.
 */
function setupCardValidation(card) {
    card.addEventListener('change', function (event) {
        const errorDiv = document.getElementById('card-errors');
        if (event.error) {
            const html = `
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
}

/**
 * Handle form submission and payment processing.
 * @param {object} card - Stripe card element.
 * @param {string} clientSecret - The client secret for payment.
 */
function setupFormSubmission(card, clientSecret) {
    const form = document.getElementById('payment-form');
    const submitButton = document.getElementById('submit-button');

    submitButton.addEventListener('click', function (ev) {
        ev.preventDefault(); // Prevent default form submission behavior

        // Disable button and card input during payment processing
        submitButton.classList.add('disabled');
        card.update({ disabled: true });

        const saveInfo = $('#id-save-info').prop('checked');
        const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

        const postData = {
            csrfmiddlewaretoken: csrfToken,
            client_secret: clientSecret,
            save_info: saveInfo,
        };

        const url = '/checkout/cache_checkout_data/';
        $.post(url, postData)
            .done(() => confirmCardPayment(stripe, card, clientSecret, form, submitButton))
            .fail(() => location.reload()); // Reload page if error occurs
    });
}

/**
 * Confirm card payment and handle success or failure.
 * @param {object} stripe - Stripe instance.
 * @param {object} card - Stripe card element.
 * @param {string} clientSecret - The client secret for payment.
 * @param {HTMLFormElement} form - The payment form.
 * @param {HTMLButtonElement} submitButton - The form submit button.
 */
function confirmCardPayment(stripe, card, clientSecret, form, submitButton) {
    stripe
        .confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: gatherBillingDetails(form),
            },
            shipping: gatherShippingDetails(form),
        })
        .then((result) => handlePaymentResult(result, card, submitButton, form));
}

/**
 * Gather billing details from the form.
 * @param {HTMLFormElement} form - The payment form.
 * @returns {object} Billing details.
 */
function gatherBillingDetails(form) {
    return {
        name: $.trim(form.full_name.value),
        phone: $.trim(form.phone_number.value),
        email: $.trim(form.email.value),
        address: {
            line1: $.trim(form.street_address1.value),
            line2: $.trim(form.street_address2.value),
            city: $.trim(form.town_or_city.value),
            country: $.trim(form.country.value),
            state: $.trim(form.county.value),
        },
    };
}

/**
 * Gather shipping details from the form.
 * @param {HTMLFormElement} form - The payment form.
 * @returns {object} Shipping details.
 */
function gatherShippingDetails(form) {
    return {
        name: $.trim(form.full_name.value),
        phone: $.trim(form.phone_number.value),
        address: {
            line1: $.trim(form.street_address1.value),
            line2: $.trim(form.street_address2.value),
            city: $.trim(form.town_or_city.value),
            country: $.trim(form.country.value),
            postal_code: $.trim(form.postcode.value),
            state: $.trim(form.county.value),
        },
    };
}

/**
 * Handle the payment result and update UI accordingly.
 * @param {object} result - The result of the payment confirmation.
 * @param {object} card - Stripe card element.
 * @param {HTMLButtonElement} submitButton - The form submit button.
 * @param {HTMLFormElement} form - The payment form.
 */
function handlePaymentResult(result, card, submitButton, form) {
    if (result.error) {
        displayPaymentError(result.error);
        card.update({ disabled: false });
        submitButton.classList.remove('disabled');
    } else if (result.paymentIntent.status === 'succeeded') {
        form.submit();
    }
}

/**
 * Display payment error in the UI.
 * @param {object} error - The error object from Stripe.
 */
function displayPaymentError(error) {
    const errorDiv = document.getElementById('card-errors');
    const html = `
        <span class="icon" role="alert">
            <i class="fas fa-times"></i>
        </span>
        <span>${error.message}</span>
    `;
    $(errorDiv).html(html);
}

document.addEventListener('DOMContentLoaded', function () {
    // Initialize after DOM is ready
    $(document).ready(function () {
        // Retrieve Stripe public key and client secret from the DOM
        (function defineStripeKeys() {
            const stripePublicKey = JSON.parse(document.getElementById('id_stripe_public_key').textContent.trim());
            const clientSecret = JSON.parse(document.getElementById('id_client_secret').textContent.trim());
            setupStripe(stripePublicKey, clientSecret);
        })();
    });
});