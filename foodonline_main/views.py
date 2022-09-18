from django.shortcuts import render
from vendor.models import Vendor

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D  # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance


def get_n_set_currentLocation(request):
  if 'lat' in request.session:
    lat = request.session['lat']
    lng = request.session['lng']
    return lng, lat
  elif 'lat' in request.GET:
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    request.session['lat'] = lat
    request.session['lng'] = lng
    return lng, lat
  else:
    return None

def home(request):
    if get_n_set_currentLocation(request) is not None:

        pnt = GEOSGeometry('POINT(%s %s)' % (get_n_set_currentLocation(request)))
        vendors = Vendor.objects.filter(
            user_profile__location__distance_lte=(pnt, D(km=1000))).annotate(
                distance=Distance('user_profile__location', pnt)).order_by(
                    'distance')

        #jarak info dari location
        for v in vendors:
            v.kms = round(v.distance.km, 1)

    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]

    context = {
        'vendors': vendors,

    }
    return render(request, 'home.html', context)
