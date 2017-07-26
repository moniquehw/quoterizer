from django.db.models import Sum
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.utils import timezone

from .models import Quote


class IndexView(generic.ListView):
    template_name = 'quotes/index.html'
    context_object_name = 'quote_list'
    sent = Quote.sent

    def get_queryset(self):
        """
        Return the last 20 quotes

        """
        return Quote.objects.order_by('-created')[:20]


class DetailView(generic.DetailView):
    model = Quote
    template_name = 'quotes/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = self.object.lineitem_set.aggregate(Sum('amount'))['amount__sum']
        return context
