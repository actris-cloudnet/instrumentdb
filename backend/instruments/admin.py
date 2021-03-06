from django.contrib import admin, messages
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


@admin.register(models.Instrument)
class InstrumentAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ["name", "pid"]
    ordering = ["name"]
    inlines = [RelatedIdentifierAdminInline]
    fields = [
        "pid",
        "name",
        "owners",
        "model",
        "description",
        "contact_person",
        "commission_date",
        "decommission_date",
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
    def create_pids(self, request, queryset):
        created_pids = 0
        try:
            for obj in queryset:
                obj.create_pid()
                created_pids += 1
        except Exception as err:
            self.message_user(request, f"Failed to create PID: {err}.", messages.ERROR)
        if created_pids:
            self.message_user(
                request, f"Created {created_pids} PIDs successfully.", messages.SUCCESS
            )
