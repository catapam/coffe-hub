from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
import json
from product.models import Product
from .models import CartEntry


from django.db.models import F

class CartView(View):
    def get(self, request):
        cart_items = []
        total = 0

        if request.user.is_authenticated:
            # Load cart from database for logged-in users
            cart_entries = CartEntry.objects.filter(user=request.user).select_related('product')
            for entry in cart_entries:
                try:
                    product = entry.product
                    variant = product.variants.get(size=entry.size)
                    price = variant.price
                    stock = variant.stock
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
                        subtotal = price * quantity
                        total += subtotal
                        cart_items.append({
                            "product": product,
                            "slug": product.slug,
                            "size": size,
                            "price": price,
                            "quantity": quantity,
                            "stock": stock,
                            "subtotal": subtotal,
                            "id": product_id,
                        })
                except ObjectDoesNotExist:
                    continue

        context = {
            "cart": {
                "items": cart_items,
                "total": total
            }
        }
        return render(request, 'cart/cart.html', context)

class AddToCartView(View):
    def post(self, request, item_id):
        try:
            data = json.loads(request.body)
            size = str(data.get('size'))
            quantity = int(data.get('quantity'))

            if not size or quantity <= 0:
                return JsonResponse({"success": False, "type": "error", "error": "Invalid size or quantity."}, status=400)

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

            if request.user.is_authenticated:
                product = Product.objects.get(pk=item_id)
                cart_entry, created = CartEntry.objects.get_or_create(
                    user=request.user,
                    product=product,
                    size=size,
                    defaults={'quantity': quantity}
                )
                if not created:
                    cart_entry.quantity += quantity
                    cart_entry.save()

            return JsonResponse({"success": True, "type": "success", "message": "Item added to cart successfully!"})
        except ValueError:
            return JsonResponse({"success": False, "type": "error", "error": "Invalid input: quantity must be a number."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "type": "error", "error": str(e)}, status=500)


class UpdateCartView(View):
    def post(self, request, item_id):
        try:
            data = json.loads(request.body)
            size = str(data.get('size'))
            quantity = int(data.get('quantity'))

            if not size or quantity < 0:
                return JsonResponse({"success": False, "type": "error", "error": "Invalid size or quantity."}, status=400)

            if request.user.is_authenticated:
                # Update database for logged-in users
                product = get_object_or_404(Product, pk=item_id)
                cart_entry = CartEntry.objects.filter(user=request.user, product=product, size=size).first()

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
                # Update session for anonymous users
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
            return JsonResponse({"success": False, "type": "error", "error": "Invalid input: quantity must be a number."}, status=400)
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
