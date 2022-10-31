import datetime
import json
import uuid
from datetime import date
from typing import Any, Optional

import requests
from django.conf import settings
from django.contrib.postgres.fields import DateRangeField, RangeOperators
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from sorl.thumbnail import ImageField

from .fields import OrcidIdField, RorIdField


class Type(models.Model):
    name = models.CharField(max_length=255)
    concept_url = models.URLField(null=True, blank=True, verbose_name="Concept URL")

    def pidinst(self):
        result = {"instrumentTypeName": self.name}
        if self.concept_url:
            result["instrumentTypeIdentifier"] = {
                "instrumentTypeIdentifierValue": self.concept_url,
                "instrumentTypeIdentifierType": "URL",
            }
        return {"instrumentType": result}

    def __str__(self) -> str:
        return self.name


class Variable(models.Model):
    name = models.CharField(max_length=255)
    concept_url = models.URLField(null=True, blank=True, verbose_name="Concept URL")

    def __str__(self) -> str:
        return self.name


class Organization(models.Model):
    name = models.CharField(max_length=255)
    acronym = models.CharField(max_length=16, null=True, blank=True)
    ror_id = RorIdField(null=True, blank=True, verbose_name="ROR ID", unique=True)

    def pidinst(self, prefix: str):
        obj: dict[str, Any] = {f"{prefix}Name": self.name}
        if self.ror_id:
            obj[f"{prefix}Identifier"] = {
                f"{prefix}IdentifierValue": self.ror_id,
                f"{prefix}IdentifierType": "ROR",
            }
        return {prefix: obj}

    def update_from_ror(self):
        if not self.ror_id:
            return
        res = requests.get(f"https://api.ror.org/organizations/{self.ror_id}")
        res.raise_for_status()
        data = res.json()
        self.name = data["name"]
        if data["acronyms"]:
            self.acronym = data["acronyms"][0]

    def __str__(self) -> str:
        result = self.name
        if self.acronym:
            result += f" ({self.acronym})"
        return result


class Model(models.Model):
    name = models.CharField(max_length=255)
    manufacturers = models.ManyToManyField(Organization)
    types = models.ManyToManyField(
        Type, help_text="Classification of the type of the instrument.", blank=True
    )
    variables = models.ManyToManyField(
        Variable,
        help_text="The variable(s) that this instrument measures or observes.",
        blank=True,
    )
    image = ImageField(null=True, blank=True, verbose_name="Default image")
    concept_url = models.URLField(null=True, blank=True, verbose_name="Concept URL")

    def pidinst(self):
        result = {"modelName": self.name}
        if self.concept_url:
            result["modelIdentifier"] = {
                "modelIdentifierValue": self.concept_url,
                "modelIdentifierType": "URL",
            }
        return result

    def __str__(self) -> str:
        return self.name


class Person(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email_address = models.EmailField()
    orcid_id = OrcidIdField(null=True, blank=True, verbose_name="ORCID iD", unique=True)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return self.full_name


class Location(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Instrument(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    pid = models.URLField(unique=True, null=True, verbose_name="PID")
    name = models.CharField(
        max_length=255, help_text="Name by which the instrument instance is known."
    )
    owners = models.ManyToManyField(Organization)
    model = models.ForeignKey(Model, on_delete=models.PROTECT)
    description = models.TextField(
        blank=True,
        help_text="Technical description of the device and its capabilities.",
    )
    image = ImageField(
        null=True,
        blank=True,
        help_text="Photograph of the instrument on site. Leave empty to use default image of the model.",
    )
    serial_number = models.CharField(max_length=255, null=True, blank=True)
    locations = models.ManyToManyField(Location, through="Campaign")
    persons = models.ManyToManyField(Person, through="Pi")

    def pidinst(self):
        result = {
            "LandingPage": self.landing_page,
            "Name": self.name,
            "Owners": [owner.pidinst("owner") for owner in self.owners.all()],
            "Manufacturers": [
                manufacturer.pidinst("manufacturer")
                for manufacturer in self.model.manufacturers.all()
            ],
            "Model": self.model.pidinst(),
        }
        if self.pid:
            result["Identifier"] = {
                "identifierValue": self.pid,
                "identifierType": "Handle",
            }
        if description := self.description:
            result["Description"] = description
        if types := self.model.types.all():
            result["InstrumentType"] = [type.pidinst() for type in types]
        if variables := self.model.variables.all():
            result["MeasuredVariables"] = [
                {"measuredVariable": {"variableMeasured": variable.name}}
                for variable in variables
            ]
        dates = []
        if date := self.commission_date:
            dates.append(
                {
                    "date": {
                        "date": date.strftime("%Y-%m-%d"),
                        "dateType": "Commissioned",
                    }
                }
            )
        if date := self.decommission_date:
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
        if serial_number := self.serial_number:
            result["AlternateIdentifiers"] = [
                {
                    "alternateIdentifier": {
                        "alternateIdentifierValue": serial_number,
                        "alternateIdentifierType": "SerialNumber",
                    }
                }
            ]
        if identifiers := self.related_identifiers.all():
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
        return result

    def create_or_update_pid(self):
        types = {
            "Identifier": "21.T11148/8eb858ee0b12e8e463a5",
            "LandingPage": "21.T11148/9a15a4735d4bda329d80",
            "Name": "21.T11148/709a23220f2c3d64d1e1",
            "Owners": "21.T11148/4eaec4bc0f1df68ab2a7",
            "Manufacturers": "21.T11148/1f3e82ddf0697a497432",
            "Model": "21.T11148/c1a0ec5ad347427f25d6",
            "Description": "21.T11148/55f8ebc805e65b5b71dd",
            "InstrumentType": "21.T11148/f76ad9d0324302fc47dd",
            "MeasuredVariables": "21.T11148/72928b84e060d491ee41",
            "Dates": "21.T11148/22c62082a4d2d9ae2602",
            "AlternateIdentifiers": "21.T11148/eb3c713572f681e6c4c3",
            "RelatedIdentifiers": "21.T11148/178fb558abc755ca7046",
        }
        payload = {
            "type": "instrument",
            "uuid": str(self.uuid),
            "url": self.landing_page,
            "data": [
                {"type": types[key], "value": json.dumps(value)}
                for key, value in self.pidinst().items()
            ],
        }
        res = requests.post(settings.PID_SERVICE_URL, json=payload)
        res.raise_for_status()
        pid = res.json()["pid"]
        self.pid = pid
        self.save()

    @property
    def landing_page(self) -> str:
        return settings.PUBLIC_URL + reverse(
            "instrument",
            kwargs={"instrument_uuid": self.uuid},
        )

    @property
    def campaigns(self) -> "QuerySet[Campaign]":
        return self.campaign_set.order_by("-date_range")

    @property
    def pis(self) -> "QuerySet[Pi]":
        return self.pi_set.order_by("-date_range")

    @property
    def commission_date(self) -> Optional[date]:
        obj = self.campaign_set.order_by("date_range").first()
        return obj.date_range.lower if obj else None

    @property
    def decommission_date(self) -> Optional[date]:
        obj = self.campaign_set.order_by("date_range").last()
        return obj.date_range.upper if obj else None

    def __str__(self) -> str:
        return self.name


class Campaign(models.Model):
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    instrument = models.ForeignKey(Instrument, on_delete=models.PROTECT)
    date_range = DateRangeField()

    def __str__(self) -> str:
        if self.location:
            name = self.location.name
        else:
            name = "Unknown"
        if self.date_range.upper:
            date_range = f"from {self.date_range.lower} to {self.date_range.upper}"
        else:
            date_range = f"since {self.date_range.lower}"
        return f"{name} {date_range}"


class Pi(models.Model):
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    instrument = models.ForeignKey(Instrument, on_delete=models.PROTECT)
    date_range = DateRangeField()


class RelatedIdentifier(models.Model):
    IDENTIFIER_TYPE_CHOICES = [
        ("ARK", "ARK"),
        ("arXiv", "arXiv"),
        ("bibcode", "bibcode"),
        ("DOI", "DOI"),
        ("EAN13", "EAN13"),
        ("EISSN", "EISSN"),
        ("Handle", "Handle"),
        ("IGSN", "IGSN"),
        ("ISBN", "ISBN"),
        ("ISSN", "ISSN"),
        ("ISTC", "ISTC"),
        ("LISSN", "LISSN"),
        ("PMID", "PMID"),
        ("PURL", "PURL"),
        ("RAiD", "RAiD"),
        ("RRID", "RRID"),
        ("UPC", "UPC"),
        ("URL", "URL"),
        ("URN", "URN"),
        ("w3id", "w3id"),
    ]
    RELATION_TYPE_CHOICES = [
        ("IsDescribedBy", "Described by"),
        ("IsNewVersionOf", "New version of"),
        ("IsPreviousVersionOf", "Previous version of"),
        ("HasComponent", "Has component"),
        ("IsComponentOf", "Component of"),
        ("References", "References"),
        ("HasMetadata", "Has metadata"),
        ("WasUsedIn", "Was used in"),
        ("IsIdenticalTo", "Identical to"),
        ("IsAttachedTo", "Attached to"),
    ]
    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="related_identifiers"
    )
    identifier = models.CharField(max_length=255)
    identifier_type = models.CharField(max_length=7, choices=IDENTIFIER_TYPE_CHOICES)
    relation_type = models.CharField(max_length=19, choices=RELATION_TYPE_CHOICES)
