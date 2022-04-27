from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Instrument, Organization


def _instrument_html(request: HttpRequest, instru: Instrument) -> HttpResponse:
    return render(request, "instruments/instrument.html", {"instrument": instru})


def _instrument_xml(request: HttpRequest, instru: Instrument) -> HttpResponse:
    return render(
        request, "instruments/instrument.xml", {"instrument": instru}, "application/xml"
    )


def _organization_json(organization: Organization, prefix: str):
    obj = {f"{prefix}Name": organization.name}
    if organization.ror_id:
        obj[f"{prefix}Identifier"] = {
            f"{prefix}IdentifierValue": organization.ror_id,
            f"{prefix}IdentifierType": "ROR",
        }
    return {prefix: obj}


def _instrument_json(request: HttpRequest, instru: Instrument) -> HttpResponse:
    result = {
        "LandingPage": instru.landing_page,
        "Name": instru.name,
        "Owners": [_organization_json(owner, "owner") for owner in instru.owners.all()],
        "Manufacturers": [
            _organization_json(owner, "manufacturer")
            for owner in instru.model.manufacturers.all()
        ],
        "Model": {
            "modelName": instru.model.name,
        },
    }
    if instru.pid:
        result["Identifier"] = {
            "identifierValue": instru.pid,
            "identifierType": "Handle",
        }
    if description := instru.description:
        result["Description"] = description
    if types := instru.model.types.all():
        result["InstrumentType"] = [type.name for type in types]
    if variables := instru.model.variables.all():
        result["MeasuredVariables"] = [
            {"measuredVariable": {"variableMeasured": variable.name}}
            for variable in variables
        ]
    dates = []
    if date := instru.commission_date:
        dates.append(
            {
                "date": {
                    "date": date.strftime("%Y-%m-%d"),
                    "dateType": "Commissioned",
                }
            }
        )
    if date := instru.decommission_date:
        dates.append(
            {
                "date": {
                    "date": date.strftime("%Y-%m-%d"),
                    "dateType": "DeCommissioned",
                }
            }
        )
    if dates:
        result["Dates"] = dates
    if identifiers := instru.alternate_identifiers.all():
        result["AlternateIdentifiers"] = [
            {
                "alternateIdentifier": {
                    "alternateIdentifierValue": identifier.identifier,
                    "alternateIdentifierType": identifier.identifier_type,
                }
            }
            for identifier in identifiers
        ]
    if identifiers := instru.related_identifiers.all():
        result["RelatedIdentifiers"] = [
            {
                "relatedIdentifier": {
                    "relatedIdentifierValue": identifier.identifier,
                    "relatedIdentifierType": identifier.identifier_type,
                    "relationType": identifier.relation_type,
                }
            }
            for identifier in identifiers
        ]
    return JsonResponse(result)


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
        return _instrument_html(request, instru)
    if output_format == "json":
        return _instrument_json(request, instru)
    if output_format == "xml":
        return _instrument_xml(request, instru)

    raise Http404()
