from http.client import HTTPResponse

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from .models import Instrument


def instrument_html(request: HttpRequest, instrument_uuid: str) -> HttpResponse:
    instrument = get_object_or_404(Instrument, uuid=instrument_uuid)
    canonical_path = reverse('instrument_html', kwargs={'instrument_uuid': instrument.uuid})
    if request.path != canonical_path:
        return redirect(canonical_path)
    return render(request, "instruments/instrument.html", {"instrument": instrument})


def instrument_xml(request: HttpRequest, instrument_uuid: str) -> HttpResponse:
    instrument = get_object_or_404(Instrument, uuid=instrument_uuid)
    canonical_path = reverse('instrument_xml', kwargs={'instrument_uuid': instrument.uuid})
    if request.path != canonical_path:
        return redirect(canonical_path)
    dates = []
    if instrument.commission_date:
        dates.append(
            {
                "type": "Commissioned",
                "date": instrument.commission_date.strftime("%Y-%m-%d"),
            }
        )
    if instrument.decommission_date:
        dates.append(
            {
                "type": "DeCommissioned",
                "date": instrument.decommission_date.strftime("%Y-%m-%d"),
            }
        )
    return render(
        request,
        "instruments/instrument.xml",
        {
            "instrument": instrument,
            "dates": dates,
            "current_url": request.build_absolute_uri(),
        },
        "application/xml",
    )
