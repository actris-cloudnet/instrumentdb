import datetime
from operator import attrgetter
from typing import Any, Literal, NamedTuple

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from instruments.models import Instrument

from .forms import LogEntryForm
from .models import LogEntry


def can_edit_logbook(request: HttpRequest, instrument: Instrument) -> bool:
    return (
        request.user.is_authenticated
        and instrument.persons.filter(user=request.user).exists()
    )


def can_view_logbook(request: HttpRequest, instrument: Instrument) -> bool:
    return request.user.is_staff or can_edit_logbook(request, instrument)


class Event(NamedTuple):
    kind: Literal["log_entry", "campaign_start"]
    date: datetime.date
    data: Any


def view(request: HttpRequest, instrument_uuid: str) -> HttpResponse:
    instru = get_object_or_404(Instrument, uuid=instrument_uuid)
    if not can_view_logbook(request, instru):
        raise Http404
    can_edit = can_edit_logbook(request, instru)
    events = []
    for entry in instru.logentry_set.order_by("-date"):
        events.append(Event(kind="log_entry", date=entry.date, data=entry))
    for campaign in instru.campaign_set.order_by("-date_range"):
        events.append(
            Event(
                kind="campaign_start",
                date=campaign.date_range.lower,
                data=campaign,
            )
        )
    events.sort(key=attrgetter("date"), reverse=True)
    return render(
        request,
        "logbook/view.html",
        {"instrument": instru, "events": events, "can_edit": can_edit},
    )


def add(request: HttpRequest, instrument_uuid: str) -> HttpResponse:
    instru = get_object_or_404(Instrument, uuid=instrument_uuid)
    if not can_edit_logbook(request, instru):
        raise Http404
    if request.POST:
        form = LogEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.instrument = instru
            entry.author = request.user
            entry.save()
            return redirect("logbook:view", instrument_uuid=instru.uuid)
    else:
        form = LogEntryForm()
    return render(
        request,
        "logbook/edit.html",
        {"instrument": instru, "form": form},
    )


def edit(request: HttpRequest, instrument_uuid: str, entry_id: int) -> HttpResponse:
    instru = get_object_or_404(Instrument, uuid=instrument_uuid)
    if not can_edit_logbook(request, instru):
        raise Http404
    entry = get_object_or_404(LogEntry, id=entry_id, instrument=instru)
    if request.POST:
        form = LogEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("logbook:view", instrument_uuid=instru.uuid)
    else:
        form = LogEntryForm(instance=entry)
    return render(
        request,
        "logbook/edit.html",
        {"instrument": instru, "form": form},
    )


def delete(request: HttpRequest, instrument_uuid: str, entry_id: int) -> HttpResponse:
    instru = get_object_or_404(Instrument, uuid=instrument_uuid)
    if not can_edit_logbook(request, instru):
        raise Http404
    entry = get_object_or_404(LogEntry, id=entry_id, instrument=instru)
    if request.POST:
        entry.delete()
        return redirect("logbook:view", instrument_uuid=instru.uuid)
    return render(
        request,
        "logbook/delete.html",
        {"instrument": instru, "log_entry": entry},
    )
