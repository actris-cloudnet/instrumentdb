from http.client import HTTPResponse

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Instrument, Organization


def _instrument_html(request: HttpRequest, instrument: Instrument) -> HttpResponse:
    return render(request, "instruments/instrument.html", {"instrument": instrument})


def _instrument_xml(request: HttpRequest, instrument: Instrument) -> HttpResponse:
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
            "landing_page": instrument.get_landing_page(request),
            "dates": dates,
        },
        "application/xml",
    )


def _organization_json(organization: Organization, prefix: str):
    obj = {f"{prefix}Name": organization.name}
    if organization.ror_id:
        obj[f"{prefix}Identifier"] = {
            f"{prefix}IdentifierValue": organization.ror_id,
            f"{prefix}IdentifierType": "ROR",
        }
    return {prefix: obj}


def _instrument_json(request: HttpRequest, instrument: Instrument) -> HttpResponse:
    result = {
        "Identifier": {
            "identifierValue": "20.1000/5555",
            "identifierType": "Handle",
        },
        "LandingPage": instrument.get_landing_page(request),
        "Name": instrument.name,
        "Owners": [
            _organization_json(owner, "owner") for owner in instrument.owners.all()
        ],
        "Manufacturers": [
            _organization_json(owner, "manufacturer")
            for owner in instrument.model.manufacturers.all()
        ],
        "Model": {
            "modelName": instrument.model.name,
        },
    }
    if description := instrument.description:
        result["Description"] = description
    if types := instrument.types.all():
        result["InstrumentType"] = [type.name for type in types]
    if variables := instrument.variables.all():
        result["MeasuredVariables"] = [
            {"measuredVariable": {"variableMeasured": variable.name}}
            for variable in variables
        ]
    dates = []
    if date := instrument.commission_date:
        dates.append(
            {
                "date": {
                    "date": date.strftime("%Y-%m-%d"),
                    "dateType": "Commissioned",
                }
            }
        )
    if date := instrument.decommission_date:
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
    if identifiers := instrument.alternate_identifiers.all():
        result["AlternateIdentifiers"] = [
            {
                "alternateIdentifier": {
                    "alternateIdentifierValue": identifier.identifier,
                    "alternateIdentifierType": identifier.identifier_type,
                }
            }
            for identifier in identifiers
        ]
    if identifiers := instrument.related_identifiers.all():
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
    instrument = get_object_or_404(Instrument, uuid=instrument_uuid)

    # A single UUID has multiple textual representations with differences in
    # dashes and letter case. Let's accept the different representations but
    # redirect the user to the URL with canonical form.
    canonical_path = reverse(
        request.resolver_match.view_name,
        kwargs={"instrument_uuid": instrument.uuid, "output_format": output_format},
    )
    if request.path != canonical_path:
        return redirect(canonical_path, permanent=True)

    if output_format == "html":
        return _instrument_html(request, instrument)
    if output_format == "json":
        return _instrument_json(request, instrument)
    if output_format == "xml":
        return _instrument_xml(request, instrument)

    return HttpResponse("invalid format", status_code=400)
