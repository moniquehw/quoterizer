from django.db import models
from django.utils import timezone

class Quote(models.Model):
    title = models.CharField(max_length=255)
    created = models.DateTimeField('Date created', editable=False)
    sent = models.BooleanField('Has been sent')

    def __str__(self):
        return self.title

    def save(self, *arg, **kwargs):
        """ On save, update created timestamp

        """
        if not self.id:
            self.created = timezone.now()
        return super(Quote).save(*args, **kwargs)


class LineItem(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.FloatField(default=0)

    def __str__(self):
        return "{}: {}".format(self.description, self.amount)
