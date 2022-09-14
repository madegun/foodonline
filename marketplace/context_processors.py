from .models import Cart
from menu.models import FoodItem


def get_cart_counter(request):
  cart_counter = 0

  if request.user.is_authenticated:
    try:
      cart_items = Cart.objects.filter(user=request.user)
      if cart_items:
        for cart_item in cart_items:
          cart_counter += cart_item.quantity
      else:
        cart_counter = 0
    except:
      cart_counter = 0

  return dict(cart_counter = cart_counter)
