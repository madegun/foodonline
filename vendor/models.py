from tkinter import CASCADE
from django.db import models

from accounts.models import User, UserProfile
from accounts.utils import send_email_vendor_notification
from datetime import time, date, datetime


# Create your models here.
class Vendor(models.Model):
  user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
  user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
  vendor_name = models.CharField(max_length=50)
  vendor_slug = models.SlugField(max_length=100, unique=True)
  vendor_license = models.ImageField(upload_to='vendor/license')
  is_approved = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.vendor_name

  def is_open(self):
    #get current date day
    today_date = date.today() #date fungsi untuk mendapatkan tgl hari ini
    today = today_date.isoweekday()  #fungsi date untuk mnedapat weekly (senin=1,... - munggu=7)
    current_date_day = OpeningHour.objects.filter(vendor=self, day=today)

    #mencari status apakah date  time buka / closed
    now = datetime.now()
    current_time = now.strftime('%H:%M:%S')

    is_open = None
    for i in current_date_day:
      if not i.is_closed:
        start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
        end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())

        if current_time > start and current_time < end:
            is_open = True
            break
        else:
            is_open = False

    return is_open


  def save(self, *args, **kwargs):
    if self.pk is not None:
      #update
      default_status = Vendor.objects.get(pk=self.pk)
      if default_status.is_approved != self.is_approved:
        mail_template = 'accounts/emails/vendor_approval_email.html'
        context = {
          'user': self.user,
          'is_approved': self.is_approved,
          'to_email': self.user.email,
        }

        if self.is_approved == True:
          #send notification email ke vendor is approved
          mail_subject = 'Selamat, Restaurant yang anda daftarkan sudah di approved.'
          send_email_vendor_notification(mail_subject, mail_template, context)
        else:
          #send notification email vendor tidak si approve
          mail_subject = 'Sorry, Restaurant yang anda daftarkan belum di setujui.'
          send_email_vendor_notification(mail_subject, mail_template, context)

    return super(Vendor, self).save(*args, **kwargs)

#model untuk set opening hour restaurant
DAYS = [
  (1,("Senin")),
  (2,("Selasa")),
  (3,("Rabu")),
  (4,("Kamis")),
  (5,("Jumat")),
  (6,("Sabtu")),
  (7,("Minggu")),
]

HOUR_Of_DAYS_24 = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0, 24) for m in (0, 30)]

class OpeningHour(models.Model):
  vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
  day = models.IntegerField(choices=DAYS)
  from_hour = models.CharField(choices=HOUR_Of_DAYS_24, max_length=10, blank=True)
  to_hour = models.CharField(choices=HOUR_Of_DAYS_24, max_length=10, blank=True)
  is_closed = models.BooleanField(default=False)

  class Meta:
    ordering = ('day', '-from_hour')
    unique_together = ('vendor','day', 'from_hour', 'to_hour')

  def __str__(self):
    return self.get_day_display()
