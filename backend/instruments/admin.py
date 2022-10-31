from django.contrib import admin, messages
from django.db.models import QuerySet
from django.urls import reverse
from sorl.thumbnail.admin import AdminImageMixin

from . import models


@admin.register(models.Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]


@admin.register(models.Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]


@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]

    class Media:
        js = [
            "instruments/scripts/autoComplete.min.js",
            "instruments/scripts/organization.js",
        ]
        css = {"all": ["instruments/styles/autoComplete.css"]}


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email_address", "orcid_id"]
    ordering = ["full_name"]


@admin.register(models.Model)
class ModelAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]


class RelatedIdentifierAdminInline(admin.TabularInline):
    model = models.RelatedIdentifier
    extra = 0


class CampaignAdminInline(admin.TabularInline):
    model = models.Campaign
    ordering = ["-date_range"]
    extra = 0


class PiAdminInline(admin.TabularInline):
    model = models.Pi
    ordering = ["-date_range"]
    extra = 0


@admin.register(models.Instrument)
class InstrumentAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ["name", "pid"]
    ordering = ["name"]
    inlines = [RelatedIdentifierAdminInline, CampaignAdminInline, PiAdminInline]
    fields = [
        "pid",
        "name",
        "owners",
        "model",
        "description",
        "image",
        "serial_number",
    ]
    readonly_fields = ["pid"]
    actions = ["create_pids"]

    @staticmethod
    def view_on_site(obj):
        return reverse(
            "instrument", kwargs={"instrument_uuid": obj.uuid, "output_format": "html"}
        )

    @admin.action(description="Create PIDs for selected instruments")
    def create_pids(self, request, queryset: "QuerySet[models.Instrument]"):
        created_pids = 0
        try:
            for obj in queryset:
                obj.create_or_update_pid()
                created_pids += 1
        except Exception as err:
            self.message_user(request, f"Failed to create PID: {err}.", messages.ERROR)
        if created_pids:
            self.message_user(
                request, f"Created {created_pids} PIDs successfully.", messages.SUCCESS
            )

    def save_model(self, request, obj: models.Instrument, form, change):
        super().save_model(request, obj, form, change)
        if obj.pid:
            obj.create_or_update_pid()


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]
