from django.forms import ModelForm

from .models import LogEntry


class LogEntryForm(ModelForm):
    class Meta:
        model = LogEntry
        fields = ["date", "content"]
