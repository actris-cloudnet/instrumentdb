from django.contrib import admin
from django.urls import reverse
from sorl.thumbnail.admin import AdminImageMixin

from . import models


class TypeAdmin(admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]


admin.site.register(models.Type, TypeAdmin)


class VariableAdmin(admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]


admin.site.register(models.Variable, VariableAdmin)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]


admin.site.register(models.Organization, OrganizationAdmin)


class PersonAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email_address", "orcid_id"]
    ordering = ["full_name"]


admin.site.register(models.Person, PersonAdmin)


class ModelAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]


admin.site.register(models.Model, ModelAdmin)


class RelatedIdentifierAdminInline(admin.TabularInline):
    model = models.RelatedIdentifier


class InstrumentAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]
    inlines = [RelatedIdentifierAdminInline]
    readonly_fields = ["pid"]

    @staticmethod
    def view_on_site(obj):
        return reverse(
            "instrument", kwargs={"instrument_uuid": obj.uuid, "output_format": "html"}
        )


admin.site.register(models.Instrument, InstrumentAdmin)
