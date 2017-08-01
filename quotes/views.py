
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.utils import timezone
from .odtrender import QuoteRenderer

from .models import Quote, LineItem


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


def django_file_download_view(request, quote_id):
    #import odt_renderer
    #odt_renderer.render(Quote(id=quote_id))
    # work out how to get the quote object from django
    # TODO: Get the relevent quote object (like from the model) inside this function
    # TODO: Make a renderer fuinction that takes in the quote object and creates a temp odt file
    # TODO: Render the template to /tmp/somefilename
    # TODO: send sent date on the quote
    quote = Quote.objects.get(pk=quote_id)

    renderer = QuoteRenderer(quote)
    renderer.render()
    filepath = '/home/monique/projects/quoterizer/template.odt'
    with open(filepath, 'rb') as fp:
        data = fp.read()
    filename = 'quote.odt'
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=%s' % filename # force browser to download file
    response.write(data)
    return response
