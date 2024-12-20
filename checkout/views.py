from django.views.generic.edit import FormView
from django.shortcuts import redirect, reverse
from django.utils.html import format_html
from django.contrib import messages
from django.conf import settings
from .forms import OrderForm
from product.models import Product
from cart.utils import get_cart_data  # Import the utility function
from .models import OrderLineItem

import stripe

class CheckoutView(FormView):
    template_name = 'checkout/checkout.html'
    form_class = OrderForm

    def dispatch(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        stripe_public_key = settings.STRIPE_PUBLIC_KEY

        if not cart:
            messages.error(request, "There's nothing in your cart at the moment")
            return redirect(reverse('product'))

        if not stripe_public_key:
            messages.warning(request, 'Stripe public key is missing. \
                Did you forget to set it in your environment?')

        return super().dispatch(request, *args, **kwargs)

    def get_cart_and_stripe_context(self):
        """
        Helper method to get cart items, total, and Stripe context.
        """
        cart_items, total, adjustments = get_cart_data(self.request)

        # Stripe
        stripe_total = round(total * 100)
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        stripe_secret_key = settings.STRIPE_SECRET_KEY
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        return {
            'cart_items': cart_items,
            'total': total,
            'adjustments': adjustments,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
        }

    def post(self, request, *args, **kwargs):
        # Reuse get_cart_and_stripe_context
        context = self.get_cart_and_stripe_context()

        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)

        if order_form.is_valid():
            return self.form_valid(order_form)
        else:
            return self.form_invalid(order_form)

    def get_context_data(self, **kwargs):
        # Reuse get_cart_and_stripe_context
        context = super().get_context_data(**kwargs)
        cart_and_stripe_context = self.get_cart_and_stripe_context()

        context.update({
            'cart': {
                "items": cart_and_stripe_context['cart_items'],
                "total": cart_and_stripe_context['total'],
            },
            'order_form': self.get_form(),
            'stripe_public_key': cart_and_stripe_context['stripe_public_key'],
            'client_secret': cart_and_stripe_context['client_secret'],
        })
        return context

    def get_success_url(self):
        return reverse('product')

    def form_valid(self, form):
        order = OrderForm.save()
        cart_and_stripe_context = self.get_cart_and_stripe_context()

        for cart_item in cart_and_stripe_context['cart_items']:
            try:
                product = Product.objects.get(id=cart_item.product)
                if isinstance(cart_item, int):
                    order_line_item = OrderLineItem(
                        order=order,
                        product=product,
                        quantity=cart_item.product,
                    )
                    order_line_item.save()
                else:
                    # Create an OrderLineItem instance
                    order_line_item = OrderLineItem(
                        order=order,
                        product=product,
                        size=cart_item['size'],  # Assuming OrderLineItem has a 'size' field
                        quantity=cart_item['quantity'],
                        price=cart_item['price'],  # Include price if your model has this field
                        subtotal=cart_item['subtotal'],  # Optional: Include subtotal if relevant
                    )
                    
                    # Save the order line item
                    order_line_item.save()

            except Product.DoesNotExist:
                messages.error(request, (
                    "One of the products in your bag wasn't found in our database. "
                    "Please get in touch with us for assistance!")
                )
                order.delete()
                return redirect(reverse('view_bag'))

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('account_orders', args=[order.order_number]))

        messages.success(
            self.request,
            format_html(
                "Payment completed successfully! Thank you for your purchase. You can check your order<a href='{}'>here</a>.",
                reverse('order_view', kwargs={'order_id': order.order_number})
            )
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(request, 'There was an error with your form. \
                Please double check your information.')

        return super().form_invalid(form)
