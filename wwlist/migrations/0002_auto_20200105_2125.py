# Generated by Django 3.0.1 on 2020-01-05 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wwlist', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ww_order',
            old_name='weißwiaschd',
            new_name='ww',
        ),
    ]