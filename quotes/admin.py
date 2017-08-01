from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from .models import Quote, LineItem


class QuoteInline(admin.TabularInline):
    model = LineItem
    extra = 3

class QuoteAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['client', 'address_1', 'address_2', 'title']}),
        ('Introduction Text',{'fields': ['intro_text']}),
        ('Details',          {'fields': ['pm', 'vat', 'currency', 'conditions']}),
        ('Sent',             {'fields': ['sent']})
    ]
    inlines = [QuoteInline]

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(reverse("quotes:index"))


admin.site.register(Quote, QuoteAdmin)
