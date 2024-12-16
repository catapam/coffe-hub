from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
import json
from product.models import Product, ProductVariant
from .models import CartEntry
from django.db.models import F


class CartView(View):
    def get(self, request):
        cart_items = []
        total = 0
        adjustments = []  # To store any quantity adjustments

        if request.user.is_authenticated:
            # Load cart from database for logged-in users
            cart_entries = CartEntry.objects.filter(user=request.user).select_related('product')
            for entry in cart_entries:
                try:
                    product = entry.product
                    variant = product.variants.get(size=entry.size)
                    price = variant.price
                    stock = variant.stock

                    # Check and adjust quantity if it exceeds stock
                    if entry.quantity > stock:
                        adjustments.append({
                            "product": product.name,
                            "size": entry.size,
                            "old_quantity": entry.quantity,
                            "new_quantity": stock,
                        })
                        entry.quantity = stock
                        entry.save()

                    subtotal = price * entry.quantity
                    total += subtotal
                    cart_items.append({
                        "product": product,
                        "slug": product.slug,
                        "size": entry.size,
                        "price": price,
                        "quantity": entry.quantity,
                        "stock": stock,
                        "subtotal": subtotal,
                        "id": product.id,
                    })
                except ObjectDoesNotExist:
                    continue
        else:
            # Load cart from session for anonymous users
            cart = request.session.get('cart', {})
            for product_id, sizes in cart.items():
                try:
                    product = Product.objects.get(pk=product_id)
                    for size, quantity in sizes.items():
                        variant = product.variants.get(size=size)
                        price = variant.price
                        stock = variant.stock

                        # Check and adjust quantity if it exceeds stock
                        if quantity > stock:
                            adjustments.append({
                                "product": product.name,
                                "size": size,
                                "old_quantity": quantity,
                                "new_quantity": stock,
                            })
                            cart[product_id][size] = stock

                        subtotal = price * cart[product_id][size]
                        total += subtotal
                        cart_items.append({
                            "product": product,
                            "slug": product.slug,
                            "size": size,
                            "price": price,
                            "quantity": cart[product_id][size],
                            "stock": stock,
                            "subtotal": subtotal,
                            "id": product_id,
                        })
                except ObjectDoesNotExist:
                    continue

            # Save updated session cart
            request.session['cart'] = cart
            request.session.modified = True

        # Prepare the context for rendering
        context = {
            "cart": {
                "items": cart_items,
                "total": total
            }
        }

        # If any adjustments were made, return a JSON response with details
        if adjustments:
            return JsonResponse({
                "success": True,
                "message": "Some items in your cart had quantities exceeding available stock. Adjustments have been made.",
                "adjustments": adjustments,
            }, status=200)

        return render(request, 'cart/cart.html', context)


class AddToCartView(View):
    def post(self, request, item_id):
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            size = str(data.get('size'))
            quantity = int(data.get('quantity'))

            # Validate the incoming data
            if not size or quantity < 0:
                return JsonResponse(
                    {"success": False, "type": "error", "error": "Invalid size or quantity."},
                    status=400
                )

            # Fetch the product variant to get the stock
            product_variant = ProductVariant.objects.filter(product_id=item_id, size=size).first()

            if not product_variant:
                return JsonResponse(
                    {"success": False, "type": "error", "error": "Product variant not found."},
                    status=404
                )

            stock = product_variant.stock

            # Validate quantity against the available stock
            if quantity > stock:
                return JsonResponse(
                    {
                        "success": False,
                        "type": "error",
                        "error": f"Invalid quantity. Only {stock} items are available in stock.",
                    },
                    status=400
                )

            # Handle the cart for anonymous users
            cart = request.session.get('cart', {})

            if not isinstance(cart, dict):
                cart = {}

            item_id = str(item_id)

            if item_id not in cart:
                cart[item_id] = {}

            if size not in cart[item_id]:
                cart[item_id][size] = 0

            cart[item_id][size] += quantity
            request.session['cart'] = cart
            request.session.modified = True

            # Handle the cart for authenticated users
            if request.user.is_authenticated:
                product = Product.objects.get(pk=item_id)
                cart_entry, created = CartEntry.objects.get_or_create(
                    user=request.user,
                    product=product,
                    size=size,
                    defaults={'quantity': quantity}
                )
                if not created:
                    # Ensure quantity does not exceed stock
                    new_quantity = cart_entry.quantity + quantity
                    if new_quantity > stock:
                        return JsonResponse(
                            {
                                "success": False,
                                "type": "error",
                                "error": f"Adding {quantity} exceeds available stock of {stock}.",
                            },
                            status=400
                        )
                    cart_entry.quantity = new_quantity
                    cart_entry.save()

            return JsonResponse({"success": True, "type": "success", "message": "Item added to cart successfully!"})
        except ValueError:
            return JsonResponse(
                {"success": False, "type": "error", "error": "Invalid input: quantity must be a number."},
                status=400
            )
        except Exception as e:
            return JsonResponse({"success": False, "type": "error", "error": str(e)}, status=500)


class UpdateCartView(View):
    def post(self, request, item_id):
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            size = str(data.get('size'))
            quantity = int(data.get('quantity'))

            # Validate the incoming data
            if not size or quantity < 0:
                return JsonResponse(
                    {"success": False, "type": "error", "error": "Invalid size or quantity."},
                    status=400
                )

            # Fetch the product variant to get the stock
            product_variant = ProductVariant.objects.filter(product_id=item_id, size=size).first()

            if not product_variant:
                return JsonResponse(
                    {"success": False, "type": "error", "error": "Product variant not found."},
                    status=404
                )

            stock = product_variant.stock

            # Validate quantity against the available stock
            if quantity > stock:
                return JsonResponse(
                    {
                        "success": False,
                        "type": "error",
                        "error": f"Invalid quantity. Only {stock} items are available in stock.",
                    },
                    status=400
                )

            # Proceed to update the cart
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
                    return JsonResponse({"success": True, "type": "success", "message": "Cart updated successfully."})
                else:
                    return JsonResponse({"success": False, "type": "error", "error": "Item not found in cart."}, status=404)
            else:
                # Handle for anonymous users
                cart = request.session.get('cart', {})
                item_id = str(item_id)

                if item_id in cart and size in cart[item_id]:
                    if quantity == 0:
                        del cart[item_id][size]
                    else:
                        cart[item_id][size] = quantity

                    if not cart[item_id]:
                        del cart[item_id]

                    request.session['cart'] = cart
                    request.session.modified = True

                    return JsonResponse({"success": True, "type": "success", "message": "Cart updated successfully."})

                return JsonResponse({"success": False, "type": "error", "error": "Item not found in cart."}, status=404)

        except ValueError:
            return JsonResponse(
                {"success": False, "type": "error", "error": "Invalid input: quantity must be a number."},
                status=400
            )
        except Exception as e:
            return JsonResponse({"success": False, "type": "error", "error": str(e)}, status=500)


class DeleteCartView(View):
    def post(self, request, item_id):
        try:
            # Retrieve size from the POST body
            data = json.loads(request.body)
            size = data.get('size')

            if not size:
                return JsonResponse({"success": False, "type": "error", "error": "Size is required."}, status=400)

            if request.user.is_authenticated:
                # Delete from database for logged-in users
                product = get_object_or_404(Product, pk=item_id)
                cart_entry = CartEntry.objects.filter(user=request.user, product=product, size=size).first()

                if cart_entry:
                    cart_entry.delete()
                    return JsonResponse({"success": True, "type": "success", "message": "Item removed from cart successfully."})
                else:
                    return JsonResponse({"success": False, "type": "error", "error": "Item not found in cart."}, status=404)
            else:
                # Delete from session for anonymous users
                cart = request.session.get('cart', {})
                item_id = str(item_id)

                if item_id in cart and size in cart[item_id]:
                    del cart[item_id][size]

                    if not cart[item_id]:
                        del cart[item_id]

                    request.session['cart'] = cart
                    request.session.modified = True

                    return JsonResponse({"success": True, "type": "success", "message": "Item removed from cart successfully."})

                return JsonResponse({"success": False, "type": "error", "error": "Item not found in cart."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "type": "error", "error": "Invalid JSON payload."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "type": "error", "error": str(e)}, status=500)
