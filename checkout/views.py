from django.views.generic.edit import FormView
from django.shortcuts import redirect, reverse
from django.contrib import messages
from .forms import OrderForm
from product.models import Product
from cart.utils import get_cart_data  # Import the utility function

class CheckoutView(FormView):
    template_name = 'checkout/checkout.html'
    form_class = OrderForm

    def dispatch(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "There's nothing in your cart at the moment")
            return redirect(reverse('product'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items, total, adjustments = get_cart_data(self.request)

        context['cart'] = {"items": cart_items, "total": total}
        context['order_form'] = self.get_form()
        context['stripe_public_key'] = 'pk_test_0SMREd7Vdweb1MGRi8S0EycR00JVzSAs5O'
        context['client_secret'] = 'test client secret'
        return context

    def form_valid(self, form):
        # Process the form here if needed
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
