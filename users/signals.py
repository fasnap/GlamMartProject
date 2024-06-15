from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile, Wallet
from user_account.models import UserAccount


@receiver(post_save, sender=UserAccount)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        user_profile=UserProfile.objects.create(user=instance)
        username = instance.username
        if len(username) >= 4:
            referral_code = username[:4].upper() + str(instance.id)
            user_profile.referral_code=referral_code
            user_profile.save()

@receiver(post_save, sender=UserAccount)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)