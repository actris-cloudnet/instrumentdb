from django.contrib import admin
from django.urls import reverse
from sorl.thumbnail.admin import AdminImageMixin

from . import models

admin.site.register(models.Type)
admin.site.register(models.Variable)
admin.site.register(models.Organization)
admin.site.register(models.Person)


class ModelAdmin(AdminImageMixin, admin.ModelAdmin):
    pass


admin.site.register(models.Model, ModelAdmin)


class RelatedIdentifierAdminInline(admin.TabularInline):
    model = models.RelatedIdentifier


class InstrumentAdmin(AdminImageMixin, admin.ModelAdmin):
    inlines = [RelatedIdentifierAdminInline]
    readonly_fields = ["pid"]

    @staticmethod
    def view_on_site(obj):
        return reverse(
            "instrument", kwargs={"instrument_uuid": obj.uuid, "output_format": "html"}
        )


admin.site.register(models.Instrument, InstrumentAdmin)
