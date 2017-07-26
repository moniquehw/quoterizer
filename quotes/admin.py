from django.contrib import admin

from .models import Quote, LineItem


class QuoteInline(admin.TabularInline):
    model = LineItem
    extra = 3

class QuoteAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['client', 'address']}),
        ('Sent',             {'fields': ['sent']}),
    ]
    inlines = [QuoteInline]


admin.site.register(Quote, QuoteAdmin)
