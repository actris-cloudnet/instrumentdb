from django.contrib import admin
from django.urls import reverse

from . import models

admin.site.register(models.Type)
admin.site.register(models.Variable)
admin.site.register(models.Organization)
admin.site.register(models.Model)
admin.site.register(models.Person)


class RelatedIdentifierAdminInline(admin.TabularInline):
    model = models.RelatedIdentifier


class AlternateIdentifierAdminInline(admin.TabularInline):
    model = models.AlternateIdentifier


class InstrumentAdmin(admin.ModelAdmin):
    inlines = (RelatedIdentifierAdminInline, AlternateIdentifierAdminInline)

    def view_on_site(self, obj):
        return reverse("instrument_html", kwargs={"instrument_uuid": obj.uuid})


admin.site.register(models.Instrument, InstrumentAdmin)
