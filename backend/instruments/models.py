import datetime
import json
import uuid
from typing import Optional

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import DateRangeField
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from sorl.thumbnail import ImageField

from .fields import OrcidIdField, RorIdField


class Type(models.Model):
    name = models.CharField(max_length=255)
    concept_url = models.URLField(null=True, blank=True, verbose_name="Concept URL")

    def pidinst(self):
        result: dict = {"instrumentTypeName": self.name}
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
        obj: dict = {f"{prefix}Name": self.name}
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
    image_attribution = models.CharField(max_length=255, null=True, blank=True)
    concept_url = models.URLField(null=True, blank=True, verbose_name="Concept URL")

    def pidinst(self):
        result: dict = {"modelName": self.name}
        if self.concept_url:
            result["modelIdentifier"] = {
                "modelIdentifierValue": self.concept_url,
                "modelIdentifierType": "URL",
            }
        return result

    def __str__(self) -> str:
        return self.name


class Person(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.PROTECT)
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
    class Meta:
        permissions = [("can_create_pid", "Can create PID")]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    pid = models.URLField(unique=True, null=True, verbose_name="PID")
    name = models.CharField(
        max_length=255, help_text="Name by which the instrument instance is known."
    )
    owners = models.ManyToManyField(Organization, related_name="owned_instruments")
    model = models.ForeignKey(Model, on_delete=models.PROTECT, null=True, blank=True)
    manufacturers = models.ManyToManyField(
        Organization,
        related_name="manufactured_instruments",
        blank=True,
        help_text="Leavy empty if model is specified.",
    )
    types = models.ManyToManyField(
        Type, blank=True, help_text="Leavy empty if model is specified."
    )
    description = models.TextField(
        blank=True,
        help_text="Technical description of the device and its capabilities.",
    )
    image = ImageField(
        null=True,
        blank=True,
        help_text="Photograph of the instrument on site. Leave empty to use default image of the model.",
    )
    image_attribution = models.CharField(max_length=255, null=True, blank=True)
    serial_number = models.CharField(max_length=255, null=True, blank=True)
    locations = models.ManyToManyField(Location, through="Campaign")
    persons = models.ManyToManyField(Person, through="Contact")
    components = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="component_of"
    )
    new_version = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT
    )

    def pidinst(self):
        result: dict = {
            "SchemaVersion": "1.0",
            "LandingPage": self.landing_page,
            "Name": self.name,
            "Owners": [owner.pidinst("owner") for owner in self.owners.all()],
        }
        result["Manufacturers"] = [
            manufacturer.pidinst("manufacturer")
            for manufacturer in self.get_manufacturers()
        ]
        if self.model:
            result["Model"] = self.model.pidinst()
        if self.pid:
            result["Identifier"] = {
                "identifierValue": self.pid,
                "identifierType": "Handle",
            }
        if description := self.description:
            result["Description"] = description
        if types := self.get_types():
            result["InstrumentType"] = [type.pidinst() for type in types]
        if variables := self.get_variables():
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
        if related_identifiers := self.get_related_identifiers():
            result["RelatedIdentifiers"] = [
                {
                    "relatedIdentifier": {
                        "relatedIdentifierValue": identifier["identifier"],
                        "relatedIdentifierType": identifier["identifier_type"],
                        "relationType": identifier["relation_type"],
                    }
                }
                for identifier in related_identifiers
            ]
        return result

    def create_or_update_pid(self):
        types = {
            "Identifier": "21.T11148/8eb858ee0b12e8e463a5",
            "SchemaVersion": "21.T11148/f5e68cc7718a6af2a96c",
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

    def update_related_pids(self):
        for component in self.components.filter(pid__isnull=False):
            component.create_or_update_pid()
        for parent in self.parents.filter(pid__isnull=False):
            parent.create_or_update_pid()
        if self.new_version and self.new_version.pid:
            self.new_version.create_or_update_pid()
        if self.previous_version and self.previous_version.pid:
            self.previous_version.create_or_update_pid()

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
    def pis(self) -> "QuerySet[Contact]":
        return self.contact_set.filter(role=Contact.PI).order_by("-date_range")

    @property
    def commission_date(self) -> Optional[datetime.date]:
        obj = self.campaign_set.order_by("date_range").first()
        return obj.date_range.lower if obj else None

    @property
    def decommission_date(self) -> Optional[datetime.date]:
        obj = self.campaign_set.order_by("date_range").last()
        return obj.date_range.upper if obj else None

    @property
    def parents(self):
        return Instrument.objects.filter(components=self)

    @property
    def previous_version(self):
        try:
            return Instrument.objects.get(new_version=self)
        except Instrument.DoesNotExist:
            return None

    def get_manufacturers(self):
        if self.model:
            return self.model.manufacturers.all()
        return self.manufacturers.all()

    def get_types(self):
        if self.model:
            return self.model.types.all()
        return self.types.all()

    def get_variables(self):
        if self.model is None:
            return []
        return self.model.variables.all()

    def get_related_identifiers(self):
        output = []
        for identifier in self.related_identifiers.all():
            output.append(
                {
                    "identifier": identifier.identifier,
                    "identifier_type": identifier.identifier_type,
                    "relation_type": identifier.relation_type,
                }
            )

        def add_relation(relation_type, instrument):
            output.append(
                {
                    "identifier": instrument.pid
                    if instrument.pid
                    else instrument.landing_page,
                    "identifier_type": "Handle" if instrument.pid else "URL",
                    "relation_type": relation_type,
                }
            )

        for component in self.components.all():
            add_relation("HasComponent", component)
        for parent in self.parents:
            add_relation("IsComponentOf", parent)
        if self.new_version:
            add_relation("IsPreviousVersionOf", self.new_version)
        if self.previous_version:
            add_relation("IsNewVersionOf", self.previous_version)
        return output

    def get_image(self) -> str | None:
        if self.image:
            return self.image
        if self.model and self.model.image:
            return self.model.image
        return None

    def get_image_attribution(self) -> str | None:
        if self.image:
            return self.image_attribution
        if self.model and self.model.image:
            return self.model.image_attribution
        return None

    def __str__(self) -> str:
        return self.name


class Campaign(models.Model):
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    instrument = models.ForeignKey(Instrument, on_delete=models.PROTECT)
    date_range = DateRangeField(blank=True)

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


class Contact(models.Model):
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    instrument = models.ForeignKey(Instrument, on_delete=models.PROTECT)
    date_range = DateRangeField(blank=True)

    PI = "pi"
    EXTRA = "extra"
    ROLE_CHOICES = [
        (PI, "Principal investigator"),
        (EXTRA, "Extra person"),
    ]
    role = models.TextField(choices=ROLE_CHOICES)


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
