from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Instrument


def instrument(
    request: HttpRequest, instrument_uuid: str, output_format: str
) -> HttpResponse:
    instru = get_object_or_404(Instrument, uuid=instrument_uuid)

    # A single UUID has multiple textual representations with differences in
    # dashes and letter case. Let's accept the different representations but
    # redirect the user to the URL with canonical form.
    canonical_path = reverse(
        request.resolver_match.view_name,
        kwargs={"instrument_uuid": instru.uuid, "output_format": output_format},
    )
    if request.path != canonical_path:
        return redirect(canonical_path, permanent=True)

    if output_format == "html":
        return render(request, "instruments/instrument.html", {"instrument": instru})
    if output_format == "xml":
        return render(
            request,
            "instruments/instrument.xml",
            {"instrument": instru},
            "application/xml",
        )
    if output_format == "json":
        return JsonResponse(instru.pidinst())

    raise Http404()
