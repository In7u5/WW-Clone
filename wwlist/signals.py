from django.db.models.signals import post_save, pre_save
from django.db.models import Q, Sum
from django.dispatch import receiver
from django.core.mail import send_mail, send_mass_mail, EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from .models import Friday, WW_Order, Balance, Initial_Balance
import decimal
import secrets
from datetime import date

HOST_ADDRESS = '127.0.0.1:8000'


def update_balance(user, friday):
    previous_balance = Balance.objects.filter(user=user).filter(friday__date__lt=friday.date).order_by('-friday__date').first()
    #Check if there is a previous Balance.
    if previous_balance != None:
        reference_balance = previous_balance.balance
    else:
        reference_balance = Initial_Balance.objects.get(user=user).balance
        #Check if there is already a Balance for this Friday and this User.
    if Balance.objects.filter(user=user, friday=friday).exists():
        #Loop over all following Balances and update them.
        for balance in Balance.objects.filter(user=user).filter(friday__date__gte=friday.date).order_by('friday__date'):
            price_total = WW_Order.objects.get(user=user, friday=balance.friday).price_total
            purchase = WW_Order.objects.get(user=user, friday=balance.friday).purchase
            new_balance = reference_balance + price_total + purchase
            balance.balance = new_balance
            balance.save()
            reference_balance = new_balance
    #If there is no Balance for this Friday and this User, create it and restart the function.
    else:
        Balance.objects.create(user=user, friday=friday, balance=reference_balance)
        update_balance(user, friday)


@receiver(post_save, sender=Friday)
def create_ww_order(sender, instance, created, **kwargs):
    #Loop through all active Users and create Orders for them, as soon as a new Friday is created.
    if created:
        email_list = []
        for user in User.objects.all():
            if user.is_active:
                #Create a unique ID for every Order, which will be used as the Primary-Key and the URL
                order_id = str(user.pk) + str(instance.date.strftime("%d%m%Y")) + secrets.token_urlsafe(8)
                WW_Order.objects.create(friday=instance, user=user, order_id=order_id)

                #Create a Balance for every Friday, which references the previous Balance.
                update_balance(user, instance)

                #Prepare Emails to every User with the unique Order-Link
                html_message = render_to_string('wwlist/ww_order_email.html', {'user_first_name': user.first_name, 'order_id': order_id})
                text_message = 'Servus ' + str(user.first_name) + ',\n\n' + \
                                'hier deine Einladung für den ' + str(instance) + '.\n' + \
                                'Bitte benutze den folgenden Link für deine Bestellung:' + 'http://' + str(HOST_ADDRESS) + '/order/' + str(order_id) + '\n' + \
                                'Username: ww / Password: Wurst1' + '\n' + \
                                'Bestellungen werden bis zum Vortag, um 12:00 Uhr angenommen. Ab dann ist dieser Link nicht mehr erreichbar. \n\n' + \
                                'Viele Grüße\n' + \
                                'Das WW-Team'
                email_list.append(('WW und Brezn', text_message, 'WWuB', [user.email]))

        #Check if the date is still in the future, before sending the invitations.
        if instance.date > date.today():
            #Send out all the Emails at once.
            send_mass_mail(tuple(email_list))

    else:
        #Update the balance, as soon as the coresponding Friday is updated (e.g. price changes).
        for user in User.objects.all():
            if user.is_active:
                update_balance(user, instance)

        #Check the Ordering-Finished-Parameter of the Friday
        #Check if the purchasing Mail was already sent.
        if instance.ordering_finished == True and instance.mail_sent == False:
            #Close all orders by changing their URL
            for ww_order in WW_Order.objects.filter(friday=instance):
                ww_order.order_id = str(ww_order.user.pk) + str(instance.date.strftime("%d%m%Y")) + secrets.token_urlsafe(16)
                ww_order.save()

            #Send out an Email to the User with the lowest balance.
            #Get a list of all User, with an actual Order.
            criterion_ww = Q(ww__gt=0)
            criterion_brezn = Q(brezn__gt=0)
            user_list = WW_Order.objects.filter(friday=instance).filter(criterion_ww | criterion_brezn).values('user')
            if user_list.exists():
                #Select the User with the lowest balance.
                lowest_user = Balance.objects.filter(friday=instance, user__in=user_list).order_by('balance').first().user
                #Put all other Users in CC
                purchasing_mail_cc = tuple(User.objects.filter(id__in=user_list, ).exclude(id=lowest_user.id).values_list('email', flat=True))
                #Build and send Mail.
                if User.objects.filter(first_name=lowest_user.first_name).count() > 1:
                    email_name = f"{str(lowest_user.first_name)} ({str(lowest_user.last_name)})"
                else:
                    email_name = str(lowest_user.first_name)
                sum_ww = WW_Order.objects.filter(friday=instance).aggregate(Sum('ww'))['ww__sum']
                sum_brezn = WW_Order.objects.filter(friday=instance).aggregate(Sum('brezn'))['brezn__sum']
                text_message = 'Servus ' + str(email_name) + ',\n\n' + \
                                    'bitte für morgen '  + str(sum_ww) + ' (Stück) WW und ' + str(sum_brezn) + ' Brezn besorgen und fachgerecht zubereiten.\n' + \
                                    'Schau bitte auch noch nach, ob genügend Senf vorhanden ist.' + '\n\n' + \
                                    'Übersicht:' + 'http://' + str(HOST_ADDRESS)  + '\n' + \
                                    'Username: ww / Password: Wurst1' + '\n\n' + \
                                    'Viele Grüße\n' + \
                                    'Das WW-Team'
                purchasing_mail = EmailMessage(subject='WW und Brezn',
                                            body=text_message,
                                            to=[lowest_user.email],
                                            cc=purchasing_mail_cc
                                            )
                purchasing_mail.send()
                #Set the mail_sent-parameter of the Friday.
                instance.mail_sent = True
                instance.save()


@receiver(post_save, sender=WW_Order)
def post_update_user_balance(sender, instance, created, **kwargs):
    #Update the Balance, when the WW_Order is updated (e.g. changed Order or Purchasing-Input) 
    if created == False:
        user = instance.user
        update_balance(user, instance.friday)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Initial_Balance.objects.create(user=instance)
