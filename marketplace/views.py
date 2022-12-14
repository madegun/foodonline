
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import UserProfile

from order.form import OrderForm
from .context_processors import get_cart_total, get_cart_counter
from marketplace.models import Cart
from vendor.models import Vendor, OpeningHour
from menu.models import Category, FoodItem

from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D  # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance

from datetime import date


# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendors_count = vendors.count()

    context = {
        'vendors': vendors,
        'vendors_count': vendors_count,
    }
    return render(request, 'marketplace/listing.html', context)


#vendor detail
def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    #cara reverse related category in fooditem model
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch('fooditems',
                 queryset=FoodItem.objects.filter(is_available=True)))

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by(
        'day', '-from_hour')
    #get current date day
    today_date = date.today()  #date fungsi untuk mendapatkan tgl hari ini
    today = today_date.isoweekday(
    )  #fungsi date untuk mnedapat weekly (senin=1,... - munggu=7)
    current_date_day = OpeningHour.objects.filter(vendor=vendor, day=today)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_date_day': current_date_day,
    }
    return render(request, 'marketplace/vendor_detail.html', context)


#add cart
def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with'
                               ) == 'XMLHttpRequest':  #jika valid ajax request
            try:
                fooditem = FoodItem.objects.get(id=food_id)

                try:
                    cekCart = Cart.objects.get(user=request.user,
                                               fooditem=fooditem)
                    cekCart.quantity += 1
                    cekCart.save()
                    return JsonResponse({
                        'status':
                        'success',
                        'message':
                        'jumlah qty berhasil diupdate.',
                        'cart_counter':
                        get_cart_counter(request),
                        'qty':
                        cekCart.quantity,
                        'cart_total': get_cart_total(request)


                    })
                except:
                    cekCart = Cart.objects.create(user=request.user,
                                                  fooditem=fooditem,
                                                  quantity=1)
                    return JsonResponse({
                        'status':
                        'success',
                        'message':
                        'item berhasil ditambahkan',
                        'cart_counter':
                        get_cart_counter(request),
                        'qty':
                        cekCart.quantity,
                        'cart_total':get_cart_total(request)


                    })
            except:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Menu item sedang kosong!'
                })
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'invalid request!'
            })
    else:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Anda harus login dulu!'
        })


#decrease cart
def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                try:
                    cekCart = Cart.objects.get(user=request.user,
                                               fooditem=fooditem)
                    if cekCart.quantity > 1:  #jika cart lebih dr 1
                        cekCart.quantity -= 1  #maka cart kurangi -1
                        cekCart.save()  #simpan database
                    else:
                        cekCart.delete()
                        cekCart.quantity = 0

                    return JsonResponse({
                        'status':
                        'success',
                        'cart_counter':
                        get_cart_counter(request),
                        'qty':
                        cekCart.quantity,
                        'cart_total': get_cart_total(request)

                    })
                except:
                  return JsonResponse({
                        'status': 'failed',
                        'message': 'cart kosong'
                    })
            except:
              return JsonResponse({
                    'status': 'failed',
                    'message': 'menu tidak tersedia'
                })
        else:
          return JsonResponse({
                'status': 'failed',
                'message': 'Invalid request!'
            })
    else:
      return JsonResponse({
            'status': 'login_required',
            'message': 'Please login to continue'
        })


@login_required(login_url='login')
#cart
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


#delete cart
def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':

            try:
                #try apakah cart qty ada ?
                cart_item = Cart.objects.filter(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                return JsonResponse({
                    'status': 'success',
                    'message': 'belanjaan berhasil di hapus!',
                    'cart_counter': get_cart_counter(request),
                    'cart_total':get_cart_total(request)

                })
            except:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'cart anda kosong!'
                })
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'request tidak ditemukan!'
            })


#search
def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']

        #query untuk get fooditem by vendors id
        fetch_fooditems_by_vendorID = FoodItem.objects.filter(
            food_title__icontains=keyword,
            is_available=True).values_list('vendor', flat=True)

        #query filter vendor restaurant name dan fooditem name
        vendors = Vendor.objects.filter(
            Q(id__in=fetch_fooditems_by_vendorID)
            | Q(vendor_name__icontains=keyword,
                is_approved=True,
                user__is_active=True))

        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
        vendors = Vendor.objects.filter(
            Q(id__in=fetch_fooditems_by_vendorID)
            | Q(vendor_name__icontains=keyword,
                is_approved=True,
                user__is_active=True),
            user_profile__location__distance_lte=(pnt, D(
                km=radius))).annotate(distance=Distance(
                    'user_profile__location', pnt)).order_by('distance')

        #jarak info dari location
        for v in vendors:
            v.kms = round(v.distance.km, 1)

        vendors_count = vendors.count()
        context = {
            'vendors': vendors,
            'vendors_count': vendors_count,
            'address': address,
        }

        return render(request, 'marketplace/listing.html', context)

@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <=0:
        return redirect('marketplace')

    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'first_name': request.user.first_name,
        'phone_number': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }
    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items':cart_items
    }

    return render(request, 'marketplace/checkout.html', context)
