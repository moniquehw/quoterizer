from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Quote(models.Model):
    client = models.CharField('Client', max_length=255)
    address_1 = models.CharField(max_length=500, blank=True)
    address_2 = models.CharField(max_length=500, blank=True)
    title = models.CharField('Title', max_length=300, blank=False)
    intro_text = models.CharField('Introduction Text', max_length = 500, blank=False, default='text')
    pm = models.IntegerField('Project Manager Percentage', default=15)
    conditions = models.CharField(max_length=250, choices=[('Catalyst Standard Terms', 'Catalyst Standard Terms'), ('G-Cloud Terms', 'G-Cloud Terms')], default='Catalyst Standard Terms')
    vat = models.BooleanField('VAT (20%)', default=True)
    currency = models.CharField(max_length=250, choices=[('GBP', 'GBP'), ('EUR', 'EUR'), ('USD', 'USD')], default='GBP')

    created = models.DateTimeField('Date created', editable=False)
    sent = models.BooleanField('Has been sent', default=False)
    sent_date = models.DateTimeField('Date sent', editable=False, null=True)

    def __str__(self):
        return self.client

    def save(self, *args, **kwargs):
        """ On save, update created timestamp

        """
        if not self.id:
            self.created = timezone.now()
        return super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return self.lineitem_set.aggregate(Sum('amount'))['amount__sum']


class LineItem(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    description = models.CharField(max_length=500)
    amount = models.FloatField(default=0)

    def __str__(self):
        return "{}: {}".format(self.description, self.amount)
