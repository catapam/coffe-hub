import stripe

# Django imports
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Internal imports
from checkout.webhook_handler import StripeWH_Handler


@require_POST
@csrf_exempt
def webhook(request):
    '''
    Listen for webhooks from Stripe and process them accordingly.

    Args:
        request (HttpRequest): The incoming request object.

    Returns:
        HttpResponse: A response indicating the result of webhook processing.
    '''
    # Setup Stripe API key and webhook secret
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

    # Set up a webhook handler instance
    handler = StripeWH_Handler(request)

    # Map webhook events to relevant handler functions
    event_map = {
        'payment_intent.succeeded': (
            handler.handle_payment_intent_succeeded
        ),
        'payment_intent.payment_failed': (
            handler.handle_payment_intent_payment_failed
        ),
    }

    # Get the webhook type from Stripe
    event_type = event['type']

    # Determine the appropriate handler or use the generic one
    event_handler = event_map.get(
        event_type, handler.handle_event
    )

    # Call the event handler with the event
    response = event_handler(event)
    return response
