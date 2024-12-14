from django.shortcuts import render, redirect
import json

# Create your views here.

def view_cart(request):
    """ A view that renders the cart contents page """

    return render(request, 'cart/cart.html')


from django.http import JsonResponse

def add_to_cart(request, item_id): 
    """Add a quantity of the specified product to the shopping cart via AJAX."""
    
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."}, status=400)
    
    try:
        data = json.loads(request.body)
        size = str(data.get('size'))
        quantity = int(data.get('quantity'))
        
        # Validate size and quantity
        if not size or quantity <= 0:
            return JsonResponse({"success": False, "error": "Invalid size or quantity."}, status=400)
        
        # Get cart or initialize if it doesn't exist
        cart = request.session.get('cart', {})
        
        # Ensure cart is a dictionary
        if not isinstance(cart, dict):
            cart = {}
        
        # Convert item_id to string to ensure consistent key type
        item_id = str(item_id)
        
        # If the product is not in the cart, create a new entry
        if item_id not in cart:
            cart[item_id] = {}
        
        # If the size doesn't exist for this product, initialize it
        if size not in cart[item_id]:
            cart[item_id][size] = 0
        
        # Add the quantity
        cart[item_id][size] += quantity 
        
        # Save the cart back to the session
        request.session['cart'] = cart
        request.session.modified = True  # Ensure session is saved

        # Log the cart for debugging
        print(request.session['cart']) 

        # Respond with a success message
        return JsonResponse({"success": True, "message": "Item added to cart successfully!"})
    
    except ValueError as e:
        return JsonResponse({"success": False, "error": "Invalid input: quantity must be a number."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

