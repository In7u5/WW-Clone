from datetime import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import reverse
import secrets

# Create your models here.

class Friday(models.Model):
    date = models.DateField(default=timezone.now)

    cost_ww = models.DecimalField(default=0.8, max_digits=10, decimal_places=2)
    cost_brezn = models.DecimalField(default=1.0, max_digits=10, decimal_places=2)
    cost_mustard = models.DecimalField(default=0.2, max_digits=10, decimal_places=2)

    ordering_finished = models.BooleanField(default=False)
    mail_sent = models.BooleanField(default=False, editable=False)

    class Meta:
        ordering = ('-date', )

    def __str__(self):
            return '%s' % (str(self.date.strftime("%d.%m.%Y")))


class WW_Order(models.Model):
    friday = models.ForeignKey(Friday, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ww = models.PositiveIntegerField(default=0, verbose_name='WW')
    brezn = models.PositiveIntegerField(default=0)

    purchase = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)

    order_id = models.SlugField(unique=True)

    @property
    def full_name(self):
        return f"{str(self.user.first_name)} {str(self.user.last_name)}"    

    @property
    def price_total(self):
        return -((self.friday.cost_ww + self.friday.cost_mustard) * self.ww + self.friday.cost_brezn * self.brezn)

    class Meta:
        ordering = ('-friday__date', )

    def __str__(self):
        return f"{str(self.user.first_name)} {str(self.user.last_name)} - {str(self.friday)}"


    def get_absolute_url(self):
        return reverse('order', args=[str(self.order_id)])


class Balance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    friday = models.ForeignKey(Friday, on_delete=models.CASCADE)
    balance = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)

    previous_balance_pk = models.IntegerField(default=-1)

    class Meta:
        ordering = ('-friday__date', 'balance')

    def __str__(self):
        return f"{str(self.user.first_name)} {str(self.user.last_name)}  - {str(self.friday)}: {self.balance}€"


class Initial_Balance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)

    class Meta:
        ordering = ('user', )

    def __str__(self):
        return f"{str(self.user.first_name)} {str(self.user.last_name)}: {self.balance}€"
