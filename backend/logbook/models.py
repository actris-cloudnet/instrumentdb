from django.conf import settings
from django.db import models


class LogEntry(models.Model):
    class Meta:
        verbose_name_plural = "log entries"

    instrument = models.ForeignKey("instruments.Instrument", on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
