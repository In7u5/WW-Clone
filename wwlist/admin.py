from django.contrib import admin
from .models import WW_Order, Friday, Balance, Initial_Balance


class WW_OrderAdmin(admin.ModelAdmin):
    list_display = ('friday', 'full_name', 'ww', 'brezn', 'purchase')

# Register your models here.
admin.site.register(Friday)
admin.site.register(WW_Order, WW_OrderAdmin)
admin.site.register(Balance)
admin.site.register(Initial_Balance)