# Django imports
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

# Internal imports
from .utils import get_cart_data
from .models import CartEntry
from product.models import Product


@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    '''
    Signal handler to check if a user logs in with items in either the
    session or database cart.

    Transfers session cart items to the database cart if necessary
    and redirects the user to resolve conflicts if both carts have items.

    Args:
        sender (class): The sender of the signal.
        request (HttpRequest): The HTTP request object.
        user (User): The user logging in.
        **kwargs: Additional keyword arguments.
    '''
    # Check session cart
    has_session_cart = (
        'cart' in request.session and
        request.session['cart']
    )

    # Check database cart (simulate logged-in user)
    database_cart_items, _, _ = get_cart_data(request)
    has_database_cart = bool(database_cart_items)

    # Write session cart to database if database cart is empty
    if has_session_cart and not has_database_cart:
        for product_id, sizes in has_session_cart.items():
            for size, quantity in sizes.items():
                try:
                    product = Product.objects.get(pk=product_id)
                    CartEntry.objects.create(
                        user=user,
                        product=product,
                        size=size,
                        quantity=quantity
                    )
                except Product.DoesNotExist:
                    continue

        # Clear session cart after transferring
        del request.session['cart']
        request.session.modified = True

    # Redirect if either cart has items
    if has_session_cart and has_database_cart:
        request.session['post_login_redirect'] = 'cart_choice'
