from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views.generic import (ListView,
                                  UpdateView)
from .models import WW_Order, Friday, Balance

# Create your views here.


class Overview(ListView):
    model = Friday
    template_name = 'wwlist/overview.html'
    context_object_name = 'Fridays'
    ordering = ['-date']
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context.update({
            'WW_Orders': WW_Order.objects.all(),
            'Users': User.objects.all(),
            'Balances':Balance.objects.all().order_by('user.last_name')
        })
        return context


class OrderUpdateView(SuccessMessageMixin, UpdateView):
    model = WW_Order
    fields = ['ww', 'brezn']
    slug_url_kwarg = 'order_id'
    slug_field = 'order_id'

    success_message = 'Your order was accepted.'
