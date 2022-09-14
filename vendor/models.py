from tkinter import CASCADE
from django.db import models

from accounts.models import User, UserProfile
from accounts.utils import send_email_vendor_notification


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
