import json
from django.shortcuts import render, redirect
from marketplace.models import Cart
from marketplace.context_processors import get_cart_total
from order.form import OrderForm
from order.models import Order
from .utils import generate_order_no

import simplejson as json

# Create your views here.
def place_order(request):
  cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
  cart_count = cart_items.count()
  if cart_count <= 0:
    return redirect('marketplace')

  subtotal = get_cart_total(request)['subtotal']
  total_tax = get_cart_total(request)['tax']
  grand_total = get_cart_total(request)['grand_total']
  tax_data = get_cart_total(request)['tax_dict']

  #cek jika request adalah post method
  if request.method == 'POST':
    form = OrderForm(request.POST)
    if form.is_valid():
      order = Order()
      order.first_name = form.cleaned_data['first_name']
      order.last_name = form.cleaned_data['last_name']
      order.phone = form.cleaned_data['phone']
      order.email = form.cleaned_data['email']
      order.address = form.cleaned_data['address']
      order.country = form.cleaned_data['country']
      order.state = form.cleaned_data['state']
      order.city = form.cleaned_data['city']
      order.pin_code = form.cleaned_data['pin_code']
      order.user = request.user
      order.total_tax = total_tax
      order.total = grand_total
      order.tax_data = json.dumps(tax_data)
      order.payment_method =request.POST['payment_method']
      order.save()
      order.order_no = generate_order_no(order.id)
      order.save()

      return redirect('place_order')

    else:
      print(form.errors)
  return render(request, 'order/place_order.html')
