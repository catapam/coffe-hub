from django.views.generic.edit import FormView
from django.shortcuts import redirect, reverse
from django.utils.html import format_html
from django.contrib import messages
from django.conf import settings
from .forms import OrderForm
from product.models import Product
from cart.utils import get_cart_data  # Import the utility function
from .models import OrderLineItem
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order

import stripe


class CheckoutView(LoginRequiredMixin, FormView):
    template_name = 'checkout/checkout.html'
    form_class = OrderForm

    def dispatch(self, request, *args, **kwargs):
        cart_items, total, adjustments = get_cart_data(self.request)
        stripe_public_key = settings.STRIPE_PUBLIC_KEY

        if not cart_items:
            messages.error(request, "There's nothing in your cart at the moment")
            return redirect(reverse('product'))

        if not stripe_public_key:
            messages.warning(request, 'Stripe public key is missing. \
                Did you forget to set it in your environment?')

        return super().dispatch(request, *args, **kwargs)

    def get_cart_and_stripe_context(self):
        """
        Helper method to get cart items, total, and Stripe context.
        Reuses an existing PaymentIntent if possible, or creates a new one
        if the cart total changes.
        """
        cart_items, total, adjustments = get_cart_data(self.request)

        stripe_total = round(total * 100)
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        stripe_secret_key = settings.STRIPE_SECRET_KEY
        stripe.api_key = stripe_secret_key

        # Check if there's already a PaymentIntent in the session
        intent_id = self.request.session.get('stripe_payment_intent_id')
        if intent_id:
            try:
                # Retrieve the existing PaymentIntent
                intent = stripe.PaymentIntent.retrieve(intent_id)

                # Check if the existing PaymentIntent amount matches the cart total
                if intent['amount'] != stripe_total:
                    # Amount changed, create a new PaymentIntent
                    intent = stripe.PaymentIntent.create(
                        amount=stripe_total,
                        currency=settings.STRIPE_CURRENCY,
                    )
                    self.request.session['stripe_payment_intent_id'] = intent['id']
            except stripe.error.InvalidRequestError:
                # If the PaymentIntent is invalid, create a new one
                intent = stripe.PaymentIntent.create(
                    amount=stripe_total,
                    currency=settings.STRIPE_CURRENCY,
                )
                self.request.session['stripe_payment_intent_id'] = intent['id']
        else:
            # Create a new PaymentIntent if not in session
            intent = stripe.PaymentIntent.create(
                amount=stripe_total,
                currency=settings.STRIPE_CURRENCY,
            )
            self.request.session['stripe_payment_intent_id'] = intent['id']

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
        return reverse('order_view', kwargs={'order_id': self.order.order_number})

    def form_valid(self, form):
        order = form.save(commit=False)  # Save the form but do not commit yet
        order.user = self.request.user  # Associate the order with the logged-in user, if applicable

        # Get the PaymentIntent ID from the session
        payment_intent_id = self.request.session.get('stripe_payment_intent_id')
        order.payment_intent_id = payment_intent_id  # Save the PaymentIntent ID to the order

        order.save()  # Save the form instance to the database
        cart_and_stripe_context = self.get_cart_and_stripe_context()

        for cart_item in cart_and_stripe_context['cart_items']:
            try:
                product = Product.objects.get(id=cart_item['id'])

                # Create an OrderLineItem instance
                order_line_item = OrderLineItem(
                    order=order,
                    product=product,
                    size=cart_item['size'], 
                    quantity=cart_item['quantity'],
                    price=cart_item['price'],
                    lineitem_total=cart_item['subtotal'],
                )
                
                # Save the order line item
                order_line_item.save()

            except Product.DoesNotExist:
                messages.error(request, (
                    "One of the products in your cart wasn't found in our database. "
                    "Please get in touch with us for assistance!")
                )
                order.delete()
                return redirect(reverse('cart'))

        # Clear the PaymentIntent ID from the session after successful order creation
        self.request.session.pop('stripe_payment_intent_id', None)

        messages.success(
            self.request,
            format_html(
                "<p>Payment completed successfully! Thank you for your purchase. You can check your order <a href='{}'>here</a>!</p>",
                reverse('order_view', kwargs={'order_id': order.order_number})
            )
        )

        return redirect(reverse('order_view', kwargs={'order_id': order.order_number}))

    def form_invalid(self, form):
        messages.error(request, 'There was an error with your form. \
                Please double check your information.')

        return super().form_invalid(form)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'checkout/order_detail.html'  # Define the template to use
    context_object_name = 'order'

    def get_object(self, queryset=None):
        """
        Customize object retrieval to use order_number from the URL.
        """
        order_number = self.kwargs.get('order_id')  # 'order_id' corresponds to order_number
        try:
            # Retrieve the order using the order_number
            order = Order.objects.get(order_number=order_number)
            # Ensure the order belongs to the current user
            if order.user != self.request.user:
                raise Http404("You do not have permission to view this order.")
        except Order.DoesNotExist:
            raise Http404("Order not found.")
        return order


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'checkout/order_list.html'  # Define the template to use
    context_object_name = 'orders'

    def get_queryset(self):
        """
        Filter orders by the logged-in user.
        """
        return Order.objects.filter(user=self.request.user).order_by('-date')

