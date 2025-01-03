import json
import time
import stripe

# Django imports
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

# Internal imports
from .models import Order, OrderLineItem
from product.models import Product, ProductVariant
from accounts.models import UserProfile
from cart.models import CartEntry
from django.contrib.auth.models import User


class StripeWH_Handler:
    '''
    Handle Stripe webhooks for payment processing and order management.
    '''

    def __init__(self, request):
        '''
        Initialize the webhook handler with the request object.

        Args:
            request (HttpRequest): The incoming request object.
        '''
        self.request = request

    def _send_confirmation_email(self, order):
        '''
        Send a confirmation email to the user after order creation.

        Args:
            order (Order): The order object for which the email is sent.
        '''
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order}
        )
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.EMAIL_HOST_USER}
        )

        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [cust_email],
            fail_silently=False,
        )

    def _clear_cart(self, username):
        '''
        Clear the user's cart entries from the database.

        Args:
            username (str): The username of the user whose cart is cleared.
        '''
        user = User.objects.get(username=username)
        cart_entries = CartEntry.objects.filter(user=user)
        if cart_entries.exists():
            cart_entries.delete()

    def _reduce_stock(self, cart):
        '''
        Reduce stock for purchased product variants.

        Args:
            cart (str): JSON string representing the cart items.
        '''
        cart_items = json.loads(cart)
        for cart_item in cart_items:
            variant = ProductVariant.objects.get(
                product_id=cart_item['id'],
                size=cart_item['size'],
            )
            variant.stock -= cart_item['quantity']
            if variant.stock < 0:
                variant.stock = 0
            variant.save()

    def handle_event(self, event):
        '''
        Handle a generic or unexpected webhook event.

        Args:
            event (dict): The Stripe event payload.

        Returns:
            HttpResponse: A response indicating the event was unhandled.
        '''
        return HttpResponse(
            content=f'Unhandled webhook received: {event['type']}',
            status=200
        )

    def handle_payment_intent_succeeded(self, event):
        '''
        Handle the payment_intent.succeeded webhook from Stripe.

        Args:
            event (dict): The Stripe event payload.

        Returns:
            HttpResponse: A response indicating success or failure.
        '''
        intent = event['data']['object']
        pid = intent['id']
        cart = intent['metadata']['cart']
        save_info = intent['metadata']['save_info']
        username = intent['metadata']['username']

        stripe_charge = stripe.Charge.retrieve(intent['latest_charge'])

        billing_details = stripe_charge['billing_details']
        shipping_details = intent['shipping']

        for field, value in shipping_details['address'].items():
            if value == '':
                shipping_details['address'][field] = None

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=(
                        shipping_details['name']
                    ),

                    email__iexact=(
                        billing_details['email']
                    ),

                    phone_number__iexact=(
                        shipping_details['phone']
                    ),

                    country__iexact=(
                        shipping_details['address']['country']
                    ),

                    postcode__iexact=(
                        shipping_details['address']['postal_code']
                    ),

                    town_or_city__iexact=(
                        shipping_details['address']['city']
                    ),

                    street_address1__iexact=(
                        shipping_details['address']['line1']
                    ),

                    street_address2__iexact=(
                        shipping_details['address']['line2']
                    ),

                    county__iexact=(
                        shipping_details['address']['state']
                    ),

                    stripe_pid=pid,
                    order_total=(intent['amount'] / 100),
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        if order_exists:
            self._reduce_stock(cart)
            self._clear_cart(username)
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: '
                        f'Verified order already in database',
                status=200
            )
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details['name'],
                    email=billing_details['email'],
                    phone_number=shipping_details['phone'],
                    country=shipping_details['address']['country'],
                    postcode=shipping_details['address']['postal_code'],
                    town_or_city=shipping_details['address']['city'],
                    street_address1=shipping_details['address']['line1'],
                    street_address2=shipping_details['address']['line2'],
                    county=shipping_details['address']['state'],
                    stripe_pid=pid,
                    order_total=(intent['amount'] / 100),
                )
                for cart_item in json.loads(cart):
                    product = Product.objects.get(id=cart_item['id'])
                    order_line_item = OrderLineItem(
                        order=order,
                        product=product,
                        size=cart_item['size'],
                        quantity=cart_item['quantity'],
                        price=cart_item['price'],
                        lineitem_total=cart_item['subtotal'],
                    )
                    order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500
                )

        self._reduce_stock(cart)
        self._clear_cart(username)
        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: '
                    f'Created order in webhook',
            status=200
        )

    def handle_payment_intent_payment_failed(self, event):
        '''
        Handle the payment_intent.payment_failed webhook from Stripe.

        Args:
            event (dict): The Stripe event payload.

        Returns:
            HttpResponse: A response indicating the event was handled.
        '''
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200
        )
