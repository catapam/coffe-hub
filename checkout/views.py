from django.views.generic.edit import FormView
from django.shortcuts import redirect, reverse
from django.utils.html import format_html
from django.contrib import messages
from django.conf import settings
from .forms import OrderForm
from product.models import Product
from cart.utils import get_cart_data  # Import the utility function

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

        # Contexts
        context.update({
            'cart': {"items": cart_items, "total": total},
            'order_form': self.get_form(),
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret
        })
        return context

    def get_success_url(self):
        return reverse('product')

    def form_valid(self, form):
        messages.success(
            self.request,
            format_html(
                "Payment completed successfully! Thank you for your purchase. You can check your order<a href='{}'>here</a>.",
                reverse('account_orders')
            )
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
