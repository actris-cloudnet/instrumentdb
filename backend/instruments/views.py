import datetime
import re
from datetime import date

from django.contrib.auth.decorators import permission_required
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from logbook.views import can_view_logbook

from .decorators import cors
from .models import Instrument, Location, Person


def _instrument_json(request: HttpRequest, instru: Instrument) -> HttpResponse:
    return JsonResponse(instru.pidinst())


def _instrument_html(request: HttpRequest, instru: Instrument) -> HttpResponse:
    return render(
        request,
        "instruments/instrument.html",
        {
            "instrument": instru,
            "can_view_logbook": can_view_logbook(request, instru),
            "citation": _cite_instrument(instru),
        },
    )


def _instrument_xml(request: HttpRequest, instru: Instrument) -> HttpResponse:
    return render(
        request,
        "instruments/instrument.xml",
        {"instrument": instru},
        "application/xml",
    )


@cors(allow_origin="*")
def instrument(
    request: HttpRequest, instrument_uuid: str, output_format: str | None = None
) -> HttpResponse:
    instru = get_object_or_404(Instrument, uuid=instrument_uuid)

    # A single UUID has multiple textual representations with differences in
    # dashes and letter case. Let's accept the different representations but
    # redirect the user to the URL with canonical form.
    kwargs = {"instrument_uuid": str(instru.uuid)}
    if output_format is not None:
        kwargs["output_format"] = output_format
    canonical_path = reverse(request.resolver_match.view_name, kwargs=kwargs)  # type: ignore
    if request.path != canonical_path:
        return redirect(canonical_path, permanent=True)

    # Override content negotiation with file extension.
    output_formats = {
        "json": _instrument_json,
        "xml": _instrument_xml,
        "html": _instrument_html,
    }
    if output_format is not None:
        if handler := output_formats.get(output_format):
            return handler(request, instru)
        raise Http404()

    # Content negotiation with "Accept" header.
    output_formats = {
        "application/json": _instrument_json,
        "application/xml": _instrument_xml,
        "text/xml": _instrument_xml,
        "text/html": _instrument_html,
    }
    for accepted_type in request.accepted_types:
        for content_type, handler in output_formats.items():
            if accepted_type.match(content_type):
                return handler(request, instru)

    return HttpResponse(
        "Unsupported format requested", status=406, content_type="text/plain"
    )


def index(request: HttpRequest) -> HttpResponse:
    instruments = Instrument.objects.filter(component_of=None, new_version__isnull=True)
    if not request.user.is_authenticated:
        instruments = instruments.filter(pid__isnull=False)

    locations: list = []
    for location in Location.objects.order_by("name"):
        locations.append(
            {
                "name": location.name,
                "instruments": instruments.filter(
                    campaign__location=location,
                    campaign__date_range__contains=date.today(),
                ),
            }
        )
    locations.append(
        {
            "name": "Unknown",
            "instruments": instruments.exclude(
                campaign__date_range__contains=date.today()
            ),
        }
    )

    return render(
        request,
        "instruments/index.html",
        {"locations": locations},
    )


@cors(allow_origin="*")
def pi(request: HttpRequest, instrument_uuid: str) -> HttpResponse:
    instru = get_object_or_404(Instrument, uuid=instrument_uuid)
    pis = instru.pis
    if date_param := request.GET.get("date"):
        date_in = datetime.date.fromisoformat(date_param)
        pis = pis.filter(date_range__contains=date_in)
    data = [
        {
            "first_name": pi.person.first_name,
            "last_name": pi.person.last_name,
            "orcid_id": pi.person.orcid_id,
            "start_date": pi.date_range.lower,
            "end_date": pi.date_range.upper,
        }
        for pi in pis
    ]
    return JsonResponse(data, safe=False)


@permission_required("instruments.can_create_pid")
def create_pid(request: HttpRequest, instrument_uuid: str) -> HttpResponse:
    instru = get_object_or_404(Instrument, uuid=instrument_uuid)
    instru.create_or_update_pid()
    instru.update_related_pids()
    return redirect("instrument", instrument_uuid=instru.uuid, output_format="html")


def _format_list(values: list) -> str:
    if len(values) < 2:
        return "".join(values)
    return ", ".join(values[:-1]) + ", & " + values[-1]


def _cite_person(person: Person) -> str:
    return (
        person.last_name
        + ", "
        + re.sub(r"([^\W\d_])[^\W\d_]+", r"\1.", person.first_name)
    )


def _cite_instrument(instru: Instrument) -> str:
    today = datetime.datetime.now(datetime.timezone.utc).date()
    contacts = instru.pis.filter(date_range__contains=today)
    authors = _format_list([_cite_person(contact.person) for contact in contacts])
    publisher = "ACTRIS Cloud remote sensing data centre unit (CLU)"
    return f"{authors} ({today.year}). {instru.name}. {publisher}. {instru.pid or instru.landing_page}"
