from django.shortcuts import render, redirect

# Create your views here.

def view_cart(request):
    """ A view that renders the cart contents page """

    return render(request, 'cart/cart.html')


def add_to_cart(request, item_id): 
    """ Add a quantity of the specified product to the shopping cart """ 
 
    size = str(request.POST.get('size')) 
    quantity = int(request.POST.get('quantity')) 
    redirect_url = request.POST.get('redirect_url') 
    
    # Get cart or initialize if not exists
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
 
    request.session['cart'] = cart 
    request.session.modified = True  # Ensure session is saved
    print(request.session['cart']) 
    return redirect(redirect_url)