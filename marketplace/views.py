from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from .context_processors import get_cart_counter
from marketplace.models import Cart
from vendor.models import Vendor
from menu.models import Category, FoodItem

from django.db.models import Prefetch



# Create your views here.
def marketplace(request):
  vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
  vendors_count = vendors.count()
  context = {
    'vendors': vendors,
    'vendors_count': vendors_count,
  }
  return render(request, 'marketplace/listing.html', context)


def vendor_detail(request, vendor_slug):
  vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

  #cara reverse related category in fooditem model
  categories = Category.objects.filter(vendor=vendor).prefetch_related(
    Prefetch(
      'fooditems',
      queryset = FoodItem.objects.filter(is_available=True)
    )
  )

  if request.user.is_authenticated:
    cart_items = Cart.objects.filter(user=request.user)
  else:
    cart_items = None

  context = {
    'vendor': vendor,
    'categories': categories,
    'cart_items': cart_items,
  }
  return render(request, 'marketplace/vendor_detail.html',context)

def add_to_cart(request, food_id):
  if request.user.is_authenticated:

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
      # chek jika food item ada
      try:
        fooditem = FoodItem.objects.get(id=food_id)

        #check jika user apakah sudah menambahkan item ke cart ?
        try:
          checkcart = Cart.objects.get(user=request.user, fooditem = fooditem)
          # jika sudah ditambahkan maka tambahkan quantity saja dan simpan ke database
          checkcart.quantity += 1
          checkcart.save()
          return JsonResponse({'status': 'success', 'message': 'qty item berhasil ditambahkan di keranjang', 'cart_counter': get_cart_counter(request), 'qty':checkcart.quantity })
        except:
          checkcart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
          return JsonResponse({'status': 'success', 'message': 'item berhasil ditambahkan di keranjang', 'cart_counter':get_cart_counter(request), 'qty': checkcart.quantity })
      except:
        return JsonResponse({'status': 'failed', 'message': 'Food ini sementara kosong'})
    else:
      return JsonResponse({'status':'failed', 'message': 'invalid request'})
  else:
    return JsonResponse({'status': 'login_required', 'message':'Login Require!'})


def decrease_cart(request, food_id):
  if request.user.is_authenticated:

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
      # chek jika food item ada
      try:
        fooditem = FoodItem.objects.get(id=food_id)

        #check jika user apakah sudah menambahkan item ke keranjang belanja ?
        try:
          checkcart = Cart.objects.get(user=request.user, fooditem = fooditem)
          #cek apakah qty lebih dari 1
          # jika sudah maka quantity tinggal kurangi 1 dan simpan ke database
          if checkcart.quantity > 1:
            checkcart.quantity -= 1
            checkcart.save()
          else:
            checkcart.delete()
            checkcart.quantity = 0
          return JsonResponse({'status': 'success', 'cart_counter': get_cart_counter(request), 'qty':checkcart.quantity })
        except:

          return JsonResponse({'status': 'failed', 'message': 'keranjang belanja anda kosong' })
      except:
        return JsonResponse({'status': 'failed', 'message': 'makanan ini sementara kosong'})
    else:
      return JsonResponse({'status':'failed', 'message': 'invalid request'})
  else:
    return JsonResponse({'status': 'login_required', 'message':'silahkan login untuk melanjutkan'})
