from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Member(models.Model):
    member = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.member.first_name + ' ' + self.member.last_name)

class Balance(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    ww_order = models.ForeignKey(WW_Order, on_delete=models.CASCADE)
    balance = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{str(self.member)} - {str(friday)}: {balance}€"

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)