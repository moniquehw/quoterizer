# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-27 12:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0009_quote_vat'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='currency',
            field=models.CharField(choices=[('GBP', 'GBP'), ('EUR', 'EUR'), ('USD', 'USD')], default='GBP', max_length=250),
        ),
    ]
