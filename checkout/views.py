from django.views.generic.edit import FormView
from django.shortcuts import redirect, reverse
from django.utils.html import format_html
from django.contrib import messages
from django.conf import settings
from .forms import OrderForm
from product.models import Product
from cart.utils import get_cart_data  # Import the utility function
from .models import OrderLineItem
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order
from django.views.decorators.http import require_POST
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from accounts.models import UserProfile
from allauth.account.models import EmailAddress
from accounts.forms import UserProfileForm
from django import forms

import stripe
import json


class CheckoutView(LoginRequiredMixin, FormView):
    template_name = 'checkout/checkout.html'
    form_class = OrderForm

    def dispatch(self, request, *args, **kwargs):
        cart_items, total, adjustments = get_cart_data(self.request)
        stripe_public_key = settings.STRIPE_PUBLIC_KEY

        if not cart_items:
            messages.error(request, "There's nothing in your cart at the moment")
            return redirect(reverse('product'))

        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                primary_email = EmailAddress.objects.filter(user=request.user, primary=True).first()
                emails = EmailAddress.objects.filter(user=request.user).values_list('email', flat=True)

                # Define initial data for the form
                initial_data = {
                    'full_name': profile.default_full_name,
                    'email': primary_email.email if primary_email else None,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                }

                # Initialize the OrderForm with initial data
                self.order_form = OrderForm(initial=initial_data)
                self.order_form.fields['email'].widget = forms.Select(choices=[(email, email) for email in emails])
            except UserProfile.DoesNotExist:
                self.order_form = OrderForm()
        else:
            self.order_form = OrderForm()

        if not stripe_public_key:
            messages.warning(request, 'Stripe public key is missing. Did you forget to set it in your environment?')

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
        stripe_pid = self.request.session.get('stripe_pid')
        if stripe_pid:
            try:
                # Retrieve the existing PaymentIntent
                intent = stripe.PaymentIntent.retrieve(stripe_pid)

                # Check if the existing PaymentIntent amount matches the cart total
                if intent['amount'] != stripe_total:
                    # Amount changed, create a new PaymentIntent
                    intent = stripe.PaymentIntent.create(
                        amount=stripe_total,
                        currency=settings.STRIPE_CURRENCY,
                    )
                    self.request.session['stripe_pid'] = intent['id']
            except stripe.error.InvalidRequestError:
                # If the PaymentIntent is invalid, create a new one
                intent = stripe.PaymentIntent.create(
                    amount=stripe_total,
                    currency=settings.STRIPE_CURRENCY,
                )
                self.request.session['stripe_pid'] = intent['id']
        else:
            # Create a new PaymentIntent if not in session
            intent = stripe.PaymentIntent.create(
                amount=stripe_total,
                currency=settings.STRIPE_CURRENCY,
            )
            self.request.session['stripe_pid'] = intent['id']

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
            'order_form': self.order_form,
            'stripe_public_key': cart_and_stripe_context['stripe_public_key'],
            'client_secret': cart_and_stripe_context['client_secret'],
        })
        return context

    def get_success_url(self):
        return reverse('order_view', kwargs={'order_id': self.order.order_number})

    def form_valid(self, form):
        order = form.save(commit=False)  # Save the form but do not commit yet
        order.user = self.request.user  # Associate the order with the logged-in user

        # Get the PaymentIntent ID from the session
        stripe_pid = self.request.session.get('stripe_pid')
        order.stripe_pid = stripe_pid  # Save the PaymentIntent ID to the order

        # Check for existing order with the same PaymentIntent
        existing_order = Order.objects.filter(stripe_pid=stripe_pid).first()
        if existing_order:
            return redirect(reverse('order_view', kwargs={'order_id': existing_order.order_number}))

        # Save the order
        order.save()
        cart_and_stripe_context = self.get_cart_and_stripe_context()

        # Save line items
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
                messages.error(self.request, (
                    "One of the products in your cart wasn't found in our database. "
                    "Please get in touch with us for assistance!"
                ))
                order.delete()
                return redirect(reverse('cart'))

        # Clear the PaymentIntent ID from the session after successful order creation
        self.request.session.pop('stripe_pid', None)

        # Update user profile if save_info is checked
        save_info = self.request.session.get('save_info', False)

        if save_info and self.request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=self.request.user)
                profile.default_full_name = order.full_name
                profile.default_phone_number = order.phone_number
                profile.default_country = order.country
                profile.default_postcode = order.postcode
                profile.default_town_or_city = order.town_or_city
                profile.default_street_address1 = order.street_address1
                profile.default_street_address2 = order.street_address2
                profile.default_county = order.county
                profile.save()
            except UserProfile.DoesNotExist:
                messages.error(self.request, "Could not update your profile. Please contact support.")
            
            messages.success(self.request, "Profile details updated during checkout process")

        # Success message and redirect
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
    

class CacheCheckoutDataView(View):
    """
    View to handle caching of checkout metadata.
    """

    def post(self, request, *args, **kwargs):
        try:
            pid = request.POST.get('client_secret').split('_secret')[0]
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Retrieve dynamic cart data
            cart_items, _, _ = get_cart_data(request)

            # Serialize cart items for JSON
            for cart_item in cart_items:
                serialized_cart_items = [
                    {
                        "id": cart_item["id"],
                        "size": cart_item["size"],
                        "price": float(cart_item["price"]),
                        "quantity": cart_item["quantity"],
                        "lineitem_total": float(cart_item["subtotal"]),
                    }
                ]

            # Update metadata in the PaymentIntent
            request.session['save_info'] = request.POST.get('save_info') == "true"

            stripe.PaymentIntent.modify(pid, metadata={
                'cart': json.dumps(serialized_cart_items),
                'save_info': request.session['save_info'],
                'username': request.user.username,
                'stripe_pid': pid,
            })
            return JsonResponse({'success': True}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


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

