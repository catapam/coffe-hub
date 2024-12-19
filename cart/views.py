import json
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from product.models import Product
from .models import CartEntry
from .utils import (
    get_cart_data,
    add_to_cart_logic,
    update_cart_logic,
    delete_cart_item_logic
)


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
