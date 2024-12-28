import json
import stripe

# Django imports
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, reverse
from django.utils.html import format_html
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import FormView
from django.views.decorators.http import require_POST

# Internal imports
from .forms import OrderForm
from .models import Order, OrderLineItem
from product.models import Product
from cart.utils import get_cart_data
from accounts.models import UserProfile
from allauth.account.models import EmailAddress
from accounts.forms import UserProfileForm


class CheckoutView(LoginRequiredMixin, FormView):
    '''
    Handles the checkout process, including rendering the checkout form,
    creating orders, and managing PaymentIntents via Stripe.
    '''
    template_name = 'checkout/checkout.html'
    form_class = OrderForm

    def dispatch(self, request, *args, **kwargs):
        '''
        Prepare the checkout form and validate cart contents.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            HttpResponse: The appropriate response for the request.
        '''
        cart_items, total, adjustments = get_cart_data(self.request)
        stripe_public_key = settings.STRIPE_PUBLIC_KEY

        if not cart_items:
            messages.error(
                request, "There's nothing in your cart at the moment"
            )
            return redirect(reverse('product'))

        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                primary_email = EmailAddress.objects.filter(
                    user=request.user, primary=True
                ).first()
                emails = EmailAddress.objects.filter(
                    user=request.user
                ).values_list('email', flat=True)

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
                self.order_form = OrderForm(initial=initial_data)
                self.order_form.fields['email'].widget = forms.Select(
                    choices=[(email, email) for email in emails]
                )
            except UserProfile.DoesNotExist:
                self.order_form = OrderForm()
        else:
            self.order_form = OrderForm()

        if not stripe_public_key:
            messages.warning(
                request,
                'Stripe public key is missing. Did you forget to set it?'
            )

        return super().dispatch(request, *args, **kwargs)

    def get_cart_and_stripe_context(self):
        '''
        Retrieve cart details and manage Stripe PaymentIntent.

        Returns:
            dict: A dictionary containing cart and Stripe details.
        '''
        cart_items, total, adjustments = get_cart_data(self.request)

        stripe_total = round(total * 100)
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        stripe_secret_key = settings.STRIPE_SECRET_KEY
        stripe.api_key = stripe_secret_key

        stripe_pid = self.request.session.get('stripe_pid')
        if stripe_pid:
            try:
                intent = stripe.PaymentIntent.retrieve(stripe_pid)
                if intent['amount'] != stripe_total:
                    intent = stripe.PaymentIntent.create(
                        amount=stripe_total,
                        currency=settings.STRIPE_CURRENCY,
                    )
                    self.request.session['stripe_pid'] = intent['id']
            except stripe.error.InvalidRequestError:
                intent = stripe.PaymentIntent.create(
                    amount=stripe_total,
                    currency=settings.STRIPE_CURRENCY,
                )
                self.request.session['stripe_pid'] = intent['id']
        else:
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
        '''
        Handle POST requests to process the checkout form.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            HttpResponse: Redirect to success or failure page.
        '''
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
        '''
        Add cart and Stripe context to the template context.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: Context data for the template.
        '''
        context = super().get_context_data(**kwargs)
        cart_and_stripe_context = self.get_cart_and_stripe_context()

        context.update({
            'cart': {
                'items': cart_and_stripe_context['cart_items'],
                'total': cart_and_stripe_context['total'],
            },
            'order_form': self.order_form,
            'stripe_public_key': cart_and_stripe_context['stripe_public_key'],
            'client_secret': cart_and_stripe_context['client_secret'],
        })
        return context

    def get_success_url(self):
        '''
        Determine the URL to redirect to after successful checkout.

        Returns:
            str: The success URL.
        '''
        return reverse(
            'order_view',
            kwargs={'order_id': self.order.order_number}
        )

    def form_valid(self, form):
        '''
        Handle valid form submissions and create the order.

        Args:
            form: The valid order form instance.

        Returns:
            HttpResponse: Redirect to the order detail page.
        '''
        order = form.save(commit=False)
        order.user = self.request.user

        stripe_pid = self.request.session.get('stripe_pid')
        order.stripe_pid = stripe_pid

        existing_order = Order.objects.filter(stripe_pid=stripe_pid).first()
        if existing_order:
            return redirect(
                reverse('order_view',
                        kwargs={'order_id': existing_order.order_number})
            )

        order.save()
        cart_and_stripe_context = self.get_cart_and_stripe_context()

        for cart_item in cart_and_stripe_context['cart_items']:
            try:
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
            except Product.DoesNotExist:
                messages.error(self.request, (
                    "One of the products in your cart wasn't found. "
                    'Please get in touch with us for assistance!'
                ))
                order.delete()
                return redirect(reverse('cart'))

        self.request.session.pop('stripe_pid', None)
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
                messages.error(
                    self.request,
                    'Could not update your profile. Please contact support.'
                )

            messages.success(
                self.request,
                'Profile details updated during checkout process'
            )

        messages.success(
            self.request,
            format_html(
                '<p>Payment completed successfully! '
                'Thank you for your purchase. You can check your order '
                "<a href='{}'>here</a>!</p>",
                reverse('order_view', kwargs={'order_id': order.order_number})
            )
        )
        return redirect(
            reverse('order_view', kwargs={'order_id': order.order_number})
        )

    def form_invalid(self, form):
        '''
        Handle invalid form submissions.

        Args:
            form: The invalid order form instance.

        Returns:
            HttpResponse: Redirect to the form with errors.
        '''
        messages.error(self.request, 'There was an error with your form. '
                       'Please double-check your information.')

        return super().form_invalid(form)


class CacheCheckoutDataView(View):
    '''
    View to handle caching of checkout metadata.
    '''
    def post(self, request, *args, **kwargs):
        '''
        Cache cart and user metadata into the Stripe PaymentIntent.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            JsonResponse: A response indicating success or failure.
        '''
        try:
            pid = request.POST.get('client_secret').split('_secret')[0]
            stripe.api_key = settings.STRIPE_SECRET_KEY

            cart_items, _, _ = get_cart_data(request)
            serialized_cart_items = []

            for cart_item in cart_items:
                serialized_cart_items.append(
                    {
                        'id': cart_item['id'],
                        'size': cart_item['size'],
                        'price': float(cart_item['price']),
                        'quantity': cart_item['quantity'],
                        'lineitem_total': float(cart_item['subtotal']),
                    }
                )

            request.session['save_info'] = (
                request.POST.get('save_info') == 'true'
            )

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
    '''
    View to display details of a specific order.

    Ensures that only the owner of the order can view its details.
    '''
    model = Order
    template_name = 'checkout/order_detail.html'
    context_object_name = 'order'

    def get_object(self, queryset=None):
        '''
        Retrieve the order using the order_number from the URL.

        Returns:
            Order: The order object if found and authorized.

        Raises:
            Http404: If the order does not exist or is unauthorized.
        '''
        order_number = self.kwargs.get('order_id')
        try:
            order = Order.objects.get(order_number=order_number)
            if order.user != self.request.user:
                raise Http404('You do not have permission to view this order.')
        except Order.DoesNotExist:
            raise Http404('Order not found.')
        return order


class OrderListView(LoginRequiredMixin, ListView):
    '''
    View to display a list of all orders for the logged-in user.

    Orders are filtered by the currently logged-in user and ordered
    by date in descending order.
    '''
    model = Order
    template_name = 'checkout/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        '''
        Filter the queryset to include only orders for the logged-in user.

        Returns:
            QuerySet: A queryset of orders belonging to the logged-in user.
        '''
        return Order.objects.filter(
            user=self.request.user
        ).order_by('-date')
