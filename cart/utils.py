import json

# Django imports
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

# Internal imports
from product.models import Product, ProductVariant
from .models import CartEntry


def merge_session_cart_to_user(request, user):
    '''
    Merge the session cart with the database cart for a logged-in user.

    Args:
        request: The current request object.
        user: The authenticated user.
    '''
    session_cart = request.session.get('cart', {})

    if session_cart:
        for product_id, sizes in session_cart.items():
            for size, quantity in sizes.items():
                product = Product.objects.get(pk=product_id)
                cart_entry, created = CartEntry.objects.get_or_create(
                    user=user,
                    product=product,
                    size=size,
                    defaults={'quantity': quantity}
                )
                if not created:
                    cart_entry.quantity += quantity
                    cart_entry.save()
        del request.session['cart']
        request.session.modified = True


def get_cart_data(request):
    '''
    Retrieve cart data for the current user or session.

    Args:
        request: The current request object.

    Returns:
        tuple: A tuple containing cart items, total cost, and any adjustments.
    '''
    cart_items = []
    total = 0
    adjustments = []  # To store any quantity adjustments
    items_to_remove = []

    if request.user.is_authenticated:
        cart_entries = CartEntry.objects.filter(
            user=request.user
        ).select_related('product')
        for entry in cart_entries:
            try:
                product = entry.product
                variant = product.variants.get(size=entry.size)
                price = variant.price
                stock = variant.stock

                if entry.quantity > stock:
                    adjustments.append({
                        'product': product.name,
                        'size': entry.size,
                        'old_quantity': entry.quantity,
                        'new_quantity': stock,
                    })
                    entry.quantity = stock
                    entry.save()

                if entry.quantity <= 0:
                    entry.delete()
                    continue

                subtotal = price * entry.quantity
                total += subtotal
                cart_items.append({
                    'product': product,
                    'slug': product.slug,
                    'size': entry.size,
                    'price': price,
                    'quantity': entry.quantity,
                    'stock': stock,
                    'subtotal': subtotal,
                    'id': product.id,
                })
            except ObjectDoesNotExist:
                continue
    else:
        cart = request.session.get('cart', {})
        for product_id, sizes in cart.items():
            try:
                product = Product.objects.get(pk=product_id)
                for size, quantity in sizes.items():
                    variant = product.variants.get(size=size)
                    price = variant.price
                    stock = variant.stock

                    if quantity > stock:
                        adjustments.append({
                            'product': product.name,
                            'size': size,
                            'old_quantity': quantity,
                            'new_quantity': stock,
                        })
                        cart[product_id][size] = stock

                    if cart[product_id][size] <= 0:
                        items_to_remove.append((product_id, size))
                        continue

                    subtotal = price * cart[product_id][size]
                    total += subtotal
                    cart_items.append({
                        'product': product,
                        'slug': product.slug,
                        'size': size,
                        'price': price,
                        'quantity': cart[product_id][size],
                        'stock': stock,
                        'subtotal': subtotal,
                        'id': product_id,
                    })
            except ObjectDoesNotExist:
                continue

        for product_id, size in items_to_remove:
            del cart[product_id][size]
            if not cart[product_id]:
                del cart[product_id]

        request.session['cart'] = cart
        request.session.modified = True

    return cart_items, total, adjustments


def add_to_cart_logic(request, item_id, size, quantity):
    '''
    Logic for adding items to the cart.

    Args:
        request: The current request object.
        item_id: The product ID.
        size: The size of the product.
        quantity: The quantity to add.

    Returns:
        JsonResponse: The response indicating success or failure.
    '''
    product_variant = ProductVariant.objects.filter(
        product_id=item_id, size=size
    ).first()

    if not product_variant:
        return JsonResponse(
            {
                'success': False,
                'type': 'error',
                'error': 'Product variant not found.'
            },
            status=404
        )

    stock = product_variant.stock

    if quantity > stock:
        return JsonResponse(
            {
                'success': False,
                'type': 'error',
                'error': f'Invalid quantity. Only {stock} items are available.'
            },
            status=400
        )

    cart = request.session.get('cart', {})

    if not isinstance(cart, dict):
        cart = {}

    item_id_str = str(item_id)

    if item_id_str not in cart:
        cart[item_id_str] = {}

    if size not in cart[item_id_str]:
        cart[item_id_str][size] = 0

    cart[item_id_str][size] += quantity
    request.session['cart'] = cart
    request.session.modified = True

    if request.user.is_authenticated:
        product = Product.objects.get(pk=item_id)
        cart_entry, created = CartEntry.objects.get_or_create(
            user=request.user,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )
        if not created:
            new_quantity = cart_entry.quantity + quantity
            if new_quantity > stock:
                return JsonResponse(
                    {
                        'success': False,
                        'type': 'error',
                        'error': f'Adding {quantity} exceeds available stock'
                                 f' of {stock}.'
                    },
                    status=400
                )
            cart_entry.quantity = new_quantity
            cart_entry.save()

    return JsonResponse(
        {
            'success': True,
            'type': 'success',
            'message': 'Item added to cart successfully!'
        })


def update_cart_logic(request, item_id, size, quantity):
    '''
    Logic for updating items in the cart.

    Args:
        request: The current request object.
        item_id: The product ID.
        size: The size of the product.
        quantity: The new quantity.

    Returns:
        JsonResponse: The response indicating success or failure.
    '''
    product_variant = ProductVariant.objects.filter(
        product_id=item_id, size=size
    ).first()

    if not product_variant:
        return JsonResponse(
            {
                'success': False,
                'type': 'error',
                'error': 'Product variant not found.'
            },
            status=404
        )

    stock = product_variant.stock

    if quantity > stock:
        return JsonResponse(
            {
                'success': False,
                'type': 'error',
                'error': f'Invalid quantity. Only {stock} items are available.'
            },
            status=400
        )

    if request.user.is_authenticated:
        cart_entry = CartEntry.objects.filter(
            user=request.user, product_id=item_id, size=size
        ).first()

        if cart_entry:
            if quantity == 0:
                cart_entry.delete()
            else:
                cart_entry.quantity = quantity
                cart_entry.save()
            return JsonResponse(
                {
                    'success': True,
                    'type': 'success',
                    'message': 'Cart updated successfully.'
                }
            )
        else:
            return JsonResponse(
                {
                    'success': False,
                    'type': 'error',
                    'error': 'Item not found in cart.'
                },
                status=404
            )
    else:
        cart = request.session.get('cart', {})
        item_id_str = str(item_id)

        if item_id_str in cart and size in cart[item_id_str]:
            if quantity == 0:
                del cart[item_id_str][size]
            else:
                cart[item_id_str][size] = quantity

            if not cart[item_id_str]:
                del cart[item_id_str]

            request.session['cart'] = cart
            request.session.modified = True

            return JsonResponse(
                {
                    'success': True,
                    'type': 'success',
                    'message': 'Cart updated successfully.'
                }
            )

        return JsonResponse(
            {
                'success': False,
                'type': 'error',
                'error': 'Item not found in cart.'
            },
            status=404
        )


def delete_cart_item_logic(request, item_id, size):
    '''
    Logic for deleting items from the cart.

    Args:
        request: The current request object.
        item_id: The product ID.
        size: The size of the product.

    Returns:
        JsonResponse: The response indicating success or failure.
    '''
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=item_id)
        cart_entry = CartEntry.objects.filter(
            user=request.user, product=product, size=size
        ).first()

        if cart_entry:
            cart_entry.delete()
            return JsonResponse(
                {
                    'success': True,
                    'type': 'success',
                    'message': 'Item removed from cart successfully.'
                }
            )
        else:
            return JsonResponse(
                {
                    'success': False,
                    'type': 'error',
                    'error': 'Item not found in cart.'
                },
                status=404
            )
    else:
        cart = request.session.get('cart', {})
        item_id_str = str(item_id)

        if item_id_str in cart and size in cart[item_id_str]:
            del cart[item_id_str][size]

            if not cart[item_id_str]:
                del cart[item_id_str]

            request.session['cart'] = cart
            request.session.modified = True

            return JsonResponse(
                {
                    'success': True,
                    'type': 'success',
                    'message': 'Item removed from cart successfully.'
                }
            )

        return JsonResponse(
            {
                'success': False,
                'type': 'error',
                'error': 'Item not found in cart.'
            },
            status=404
        )
