# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-27 12:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0008_auto_20170727_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='vat',
            field=models.BooleanField(default=True, verbose_name='VAT (20%)'),
        ),
    ]