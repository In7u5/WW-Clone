import os
from datetime import date, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_ww.settings")

import django
django.setup()

from wwlist import setup
setup()

from wwlist.models import Friday

#Check if today is Wednesday.
#If yes, create the next Friday.
if date.today().weekday() == 2:
    if __name__ == '__main__':    
        f = Friday()
        delta = timedelta(days=1)
        day = date.today()
        while day.weekday() != 4:
            day = day + delta
        f.date = day
        f.save()
        os.utime('/var/www/ktmtwwub_pythonanywhere_com_wsgi.py')
#Check if today is Thursday.
#If yes, finish the ordering.
elif date.today().weekday() == 3:
    if __name__ == '__main__':    
        f = Friday.objects.all().order_by('-date').first()
        if f.date > date.today() and f.ordering_finished == False:
            print('Updated')
            f.ordering_finished = True
            f.save()
            os.utime('/var/www/ktmtwwub_pythonanywhere_com_wsgi.py')

