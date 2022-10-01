from .models import Cart, Tax
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


#context processor untuk menangani subtotal, tax, dan grand total
def get_cart_total(request):
  subtotal = 0
  tax = 0
  grand_total = 0
  tax_dict = {}

  if request.user.is_authenticated:
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
      fooditem = FoodItem.objects.get(pk=item.fooditem.id)
      subtotal += (fooditem.price * item.quantity)

      get_tax = Tax.objects.filter(is_active=True)
      for i in get_tax:
        tax_type = i.tax_type
        tax_percentage = i.tax_percentage
        tax_total = round((tax_percentage * subtotal)/100, 2)
        tax_dict.update({tax_type: {str(tax_percentage):tax_total}})

        tax = 0
        # for key in tax_dict.values():
        #   for x in key.values():
        #     tax = tax + x
        tax = sum(x for key in tax_dict.values() for x in key.values())

      grand_total = (subtotal + tax)

  return dict(subtotal=subtotal, tax=tax, grand_total=grand_total, tax_dict=tax_dict)
