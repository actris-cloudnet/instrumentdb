import json
import uuid

import requests
from django.conf import settings
from django.db import models
from django.http import HttpRequest
from django.urls import reverse
from sorl.thumbnail import ImageField

from .fields import OrcidIdField, RorIdField


class Type(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Variable(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Organization(models.Model):
    name = models.CharField(max_length=255)
    ror_id = RorIdField(null=True, blank=True, verbose_name="ROR ID", unique=True)

    def pidinst(self, prefix: str):
        obj = {f"{prefix}Name": self.name}
        if self.ror_id:
            obj[f"{prefix}Identifier"] = {
                f"{prefix}IdentifierValue": self.ror_id,
                f"{prefix}IdentifierType": "ROR",
            }
        return {prefix: obj}

    def __str__(self) -> str:
        return self.name


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

    def __str__(self) -> str:
        return self.name


class Person(models.Model):
    full_name = models.CharField(max_length=255)
    email_address = models.EmailField()
    orcid_id = OrcidIdField(null=True, blank=True, verbose_name="ORCID iD", unique=True)

    def __str__(self) -> str:
        return self.full_name


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
    contact_person = models.ForeignKey(
        Person, on_delete=models.PROTECT, null=True, blank=True
    )
    commission_date = models.DateField(null=True, blank=True)
    decommission_date = models.DateField(null=True, blank=True)
    image = ImageField(
        null=True,
        blank=True,
        help_text="Photograph of the instrument on site. Leave empty to use default image of the model.",
    )
    serial_number = models.CharField(max_length=255, null=True, blank=True)

    def pidinst(self):
        result = {
            "LandingPage": self.landing_page,
            "Name": self.name,
            "Owners": [owner.pidinst("owner") for owner in self.owners.all()],
            "Manufacturers": [
                manufacturer.pidinst("manufacturer")
                for manufacturer in self.model.manufacturers.all()
            ],
            "Model": {
                "modelName": self.model.name,
            },
        }
        if self.pid:
            result["Identifier"] = {
                "identifierValue": self.pid,
                "identifierType": "Handle",
            }
        if description := self.description:
            result["Description"] = description
        if types := self.model.types.all():
            result["InstrumentType"] = [type.name for type in types]
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

    def create_pid(self):
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

    def __str__(self) -> str:
        return self.name


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
