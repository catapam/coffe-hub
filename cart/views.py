import json
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from product.models import Product
from .models import CartEntry
from .utils import (
    get_cart_data,
    add_to_cart_logic,
    update_cart_logic,
    delete_cart_item_logic,
    merge_session_cart_to_user
)
from django.contrib import messages


class CartChoiceView(View):
    def get(self, request):
        """
        Display the cart choice options to the user.
        """
        # Fetch session cart
        session_cart = request.session.get('cart', {})
        session_cart_items = []
        session_cart_total = 0

        for product_id, sizes in session_cart.items():
            for size, quantity in sizes.items():
                try:
                    product = Product.objects.get(pk=product_id)
                    variant = product.variants.get(size=size)
                    price = variant.price
                    subtotal = price * quantity

                    session_cart_items.append({
                        'product': product,
                        'size': size,
                        'quantity': quantity,
                        'price': price,
                        'subtotal': subtotal,
                    })
                    session_cart_total += subtotal
                except Product.DoesNotExist:
                    continue
                except ProductVariant.DoesNotExist:
                    continue

        # Fetch database cart
        database_cart_items, database_cart_total, _ = get_cart_data(request)

        return render(request, 'cart/cart_choice.html', {
            'database_cart': {'items': database_cart_items, 'total': database_cart_total},
            'session_cart': {'items': session_cart_items, 'total': session_cart_total},
            'merge_total': session_cart_total + database_cart_total,
        })

    def post(self, request):
        """
        Handle the user's choice to manage the cart.
        """
        choice = request.POST.get('cart_choice')

        if not choice:
            messages.error(request, "Invalid choice. Please try again.")
            return redirect('cart_choice')

        if choice == 'merge':
            merge_session_cart_to_user(request, request.user)
            messages.success(request, "Your carts have been merged.")
        elif choice == 'keep_database':
            if 'cart' in request.session:
                del request.session['cart']
                request.session.modified = True
            messages.success(request, "Kept only the database cart.")
        elif choice == 'keep_session':
            CartEntry.objects.filter(user=request.user).delete()

            session_cart = request.session.get('cart', {})
            for product_id, sizes in session_cart.items():
                for size, quantity in sizes.items():
                    product = Product.objects.get(pk=product_id)
                    CartEntry.objects.create(
                        user=request.user,
                        product=product,
                        size=size,
                        quantity=quantity
                    )
            del request.session['cart']
            request.session.modified = True
            messages.success(request, "Kept only the session cart.")

        return redirect('cart')  # Redirect to cart page


class CartView(View):
    def get(self, request):
        cart_items, total, adjustments = get_cart_data(request)
        
        context = {
            "cart": {
                "items": cart_items,
                "total": total
            }
        }

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

            return add_to_cart_logic(request, item_id, size, quantity)

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

            return update_cart_logic(request, item_id, size, quantity)

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

            return delete_cart_item_logic(request, item_id, size)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "type": "error", "error": "Invalid JSON payload."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "type": "error", "error": str(e)}, status=500)
