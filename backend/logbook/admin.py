from django.contrib import admin

from . import models


@admin.register(models.LogEntry)
class TypeAdmin(admin.ModelAdmin):
    list_display = ["created_at", "author", "instrument", "content"]
    ordering = ["-created_at"]
