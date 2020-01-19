from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Member

@receiver(post_save, sender=User)
def create_member(sender, instance, created, **kwargs):
    if created:
        Member.objects.create(member=instance)

# @receiver(post_save, sender=User)
# def save_member(sender, instance, **kwargs):
#     instance.User.save()