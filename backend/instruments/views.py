from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .decorators import cors
from .models import Instrument


def _instrument_json(request: HttpRequest, instru: Instrument) -> HttpResponse:
    return JsonResponse(instru.pidinst())


def _instrument_html(request: HttpRequest, instru: Instrument) -> HttpResponse:
    return render(request, "instruments/instrument.html", {"instrument": instru})


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
    return render(
        request,
        "instruments/index.html",
        {"instruments": Instrument.objects.order_by("name")},
    )
