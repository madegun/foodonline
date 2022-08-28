from django.shortcuts import render

# Create your views here.
def vProfile(request):
  return render(request, 'vendor/vProfile.html')
